"""
FishTalk — TTS (Text-to-Speech) Engine.

Wraps Fish-Speech using direct Python imports from the locally bundled repo.
Uses the 3-stage pipeline: encode reference → generate semantic tokens → decode to audio.
All inference runs in background threads.
"""

import gc
import logging
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np
import soundfile as sf

logger = logging.getLogger("FishTalk.tts")


class TTSEngine:
    """
    Text-to-Speech engine using Fish-Speech.

    Integrates with the locally bundled fish-speech repo via direct Python
    imports. The 3-stage pipeline:
      1. Encode reference audio → VQ tokens (for voice cloning)
      2. Text → semantic tokens via the LLM
      3. Semantic tokens → audio via the DAC decoder
    """

    def __init__(
        self,
        fish_speech_path: str,
        device: str = "cpu",
        checkpoint_name: str = "checkpoints/fish-speech-1.4",
    ):
        self.fish_speech_path = fish_speech_path
        self.device = device
        self.checkpoint_name = checkpoint_name
        self._model = None
        self._decode_one_token = None
        self._codec = None
        self._lock = threading.Lock()
        self._cancel_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._precision = None

        # Ensure fish-speech is on sys.path
        if fish_speech_path and fish_speech_path not in sys.path:
            sys.path.insert(0, fish_speech_path)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def checkpoint_path(self) -> str:
        return os.path.join(self.fish_speech_path, self.checkpoint_name)

    @property
    def codec_checkpoint_path(self) -> str:
        return os.path.join(self.checkpoint_path, "codec.pth")

    # ------------------------------------------------------------------
    # Precision detection
    # ------------------------------------------------------------------

    def _detect_precision(self):
        """Determine the best precision for the current hardware."""
        import torch

        if self.device == "cpu":
            self._precision = torch.float32
            logger.info("Using float32 precision (CPU mode)")
            return

        try:
            cap = torch.cuda.get_device_capability(0)
            if cap[0] >= 8:  # Ampere+
                self._precision = torch.bfloat16
                logger.info("Using bfloat16 precision (Ampere+ GPU)")
            else:
                self._precision = torch.float16
                logger.info("Using float16 precision (pre-Ampere GPU)")
        except Exception:
            self._precision = torch.float32
            logger.info("Using float32 precision (fallback)")

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def load_model(
        self,
        on_progress: Callable[[str, float], None] = None,
        on_ready: Callable = None,
        on_error: Callable[[Exception], None] = None,
    ):
        """
        Load Fish-Speech models in a background thread.

        Args:
            on_progress: Callback(status_text, fraction) for splash screen.
            on_ready:    Called when models are ready.
            on_error:    Called on failure.
        """
        def _load():
            try:
                import torch
                import sys

                self._detect_precision()

                if on_progress:
                    on_progress("Loading Fish-Speech LLM...", 0.2)

                # v1.4.3 LLM loading — lives in tools/llama/generate.py
                # We need to add the fish-speech root to path for `tools` to be importable
                fs_root = self.fish_speech_path
                if fs_root not in sys.path:
                    sys.path.insert(0, fs_root)

                try:
                    from tools.llama.generate import load_model as load_llm_model
                except ImportError:
                    # Fallback for Fish-Speech 1.5 path
                    from fish_speech.models.text2semantic.inference import load_model as load_llm_model

                logger.info("Loading LLM from: %s", self.checkpoint_path)
                model, decode_fn = load_llm_model(
                    checkpoint_path=self.checkpoint_path,
                    device=self.device,
                    precision=self._precision,
                    compile=False,
                )

                # Setup KV cache
                with torch.device(self.device):
                    model.setup_caches(
                        max_batch_size=1,
                        max_seq_len=model.config.max_seq_len,
                        dtype=next(model.parameters()).dtype,
                    )

                with self._lock:
                    self._model = model
                    self._decode_one_token = decode_fn

                if on_progress:
                    on_progress("Loading audio codec...", 0.6)

                # v1.4.3 codec loading — load FireflyArchitecture directly without
                # relying on Hydra's relative config path (which breaks when called
                # from outside the fish-speech root directory).
                from omegaconf import OmegaConf
                from hydra.utils import instantiate

                config_path = os.path.join(
                    self.fish_speech_path,
                    "fish_speech", "configs", "firefly_gan_vq.yaml"
                )
                logger.info("Loading codec config from: %s", config_path)
                OmegaConf.register_new_resolver("eval", eval, replace=True)
                cfg = OmegaConf.load(config_path)
                codec = instantiate(cfg)

                logger.info("Loading codec weights from: %s", self.codec_checkpoint_path)
                import torch as _torch
                state_dict = _torch.load(
                    self.codec_checkpoint_path,
                    map_location=self.device,
                    weights_only=False,
                )
                if "state_dict" in state_dict:
                    state_dict = state_dict["state_dict"]
                if any("generator" in k for k in state_dict):
                    state_dict = {
                        k.replace("generator.", ""): v
                        for k, v in state_dict.items()
                        if "generator." in k
                    }
                codec.load_state_dict(state_dict, strict=False)
                codec.eval()
                codec.to(self.device)

                with self._lock:
                    self._codec = codec

                if on_progress:
                    on_progress("TTS engine ready!", 1.0)

                logger.info("Fish-Speech models loaded successfully.")
                if on_ready:
                    on_ready()

            except Exception as exc:
                logger.error("Failed to load Fish-Speech: %s", exc, exc_info=True)
                self.unload_model()
                if on_error:
                    on_error(exc)

        t = threading.Thread(target=_load, daemon=True, name="TTS-Load")
        t.start()
        return t

    def unload_model(self):
        """Unload all models and free GPU memory."""
        with self._lock:
            if self._model is not None:
                del self._model
                self._model = None
            if self._codec is not None:
                del self._codec
                self._codec = None
            self._decode_one_token = None

        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        logger.info("TTS models unloaded.")

    # ------------------------------------------------------------------
    # Reference audio encoding (for voice cloning)
    # ------------------------------------------------------------------

    def encode_reference(self, wav_path: str) -> np.ndarray:
        """
        Encode a reference WAV file to VQ tokens for zero-shot cloning.

        Args:
            wav_path: Path to reference .wav file (15-30 seconds recommended).

        Returns:
            numpy array of VQ token indices.
        """
        if not self.is_loaded or self._codec is None:
            raise RuntimeError("Models not loaded. Call load_model() first.")

        import torch
        import torchaudio

        logger.info("Encoding reference audio: %s", wav_path)
        with self._lock:
            # v1.4.3 encode: load audio, run through FireflyArchitecture.encode()
            wav, sr = torchaudio.load(wav_path)
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
            target_sr = self._codec.spec_transform.sample_rate
            if sr != target_sr:
                wav = torchaudio.functional.resample(wav, sr, target_sr)
            audios = wav.to(self.device).unsqueeze(0)  # [1, 1, T]
            audio_lengths = torch.tensor([audios.shape[2]], device=self.device, dtype=torch.long)
            indices = self._codec.encode(audios, audio_lengths)[0][0]  # [codebooks, T]

        npy_data = indices.cpu().detach().numpy()
        logger.info("Reference encoded: shape=%s", npy_data.shape)
        return npy_data

    # ------------------------------------------------------------------
    # Text-to-speech generation
    # ------------------------------------------------------------------

    def generate(
        self,
        text: str,
        reference_wav: str = None,
        reference_tokens: np.ndarray = None,
        prompt_text: str = None,
        speed: float = 1.0,
        output_path: str = None,
        on_progress: Callable[[str, float], None] = None,
        on_chunk: Callable[[np.ndarray, int], None] = None,
        on_complete: Callable[[str], None] = None,
        on_error: Callable[[Exception], None] = None,
    ):
        """
        Generate speech from text in a background thread.

        Args:
            text:             The text to synthesize.
            reference_wav:    Path to reference .wav for voice cloning.
            reference_tokens: Pre-computed VQ tokens (numpy array).
            prompt_text:      Transcript of the reference audio.
            speed:            Playback speed multiplier (0.5–2.0).
            output_path:      Path to save the output .wav. Auto-generated if None.
            on_progress:      Callback(status, fraction).
            on_chunk:         Callback(audio_np_array, sample_rate) fired per decoded chunk.
                              Use this for streaming playback before full generation finishes.
            on_complete:      Callback(output_wav_path) when done.
            on_error:         Callback(Exception) on failure.
        """
        if not self.is_loaded:
            if on_error:
                on_error(RuntimeError("TTS model is not loaded."))
            return

        self._cancel_event.clear()

        def _worker():
            nonlocal output_path
            try:
                import torch
                import torchaudio
                try:
                    from tools.llama.generate import generate_long
                except ImportError:
                    # Fallback for Fish-Speech 1.5 path
                    from fish_speech.models.text2semantic.inference import generate_long

                if on_progress:
                    on_progress("Preparing generation...", 0.1)

                # Prepare prompt tokens for voice cloning
                prompt_tokens_list = None
                prompt_text_list = None

                if reference_wav and os.path.isfile(reference_wav):
                    logger.info("Using reference audio: %s", reference_wav)
                    wav, sr = torchaudio.load(reference_wav)
                    if wav.shape[0] > 1:
                        wav = wav.mean(dim=0, keepdim=True)
                    with self._lock:
                        target_sr = self._codec.spec_transform.sample_rate
                        if sr != target_sr:
                            wav = torchaudio.functional.resample(wav, sr, target_sr)
                        audios = wav.to(self.device).unsqueeze(0)
                        audio_lengths = torch.tensor([audios.shape[2]], device=self.device, dtype=torch.long)
                        tokens = self._codec.encode(audios, audio_lengths)[0][0]
                    prompt_tokens_list = [tokens.to(self.device)]
                    prompt_text_list = [prompt_text or ""]
                elif reference_tokens is not None:
                    prompt_tokens_list = [torch.from_numpy(reference_tokens).to(self.device)]
                    prompt_text_list = [prompt_text or ""]

                if self._cancel_event.is_set():
                    return

                if on_progress:
                    on_progress("Generating speech...", 0.3)

                # Run generation via v1.4.3 generate_long
                all_codes = []
                with self._lock:
                    generator = generate_long(
                        model=self._model,
                        device=self.device,
                        decode_one_token=self._decode_one_token,
                        text=text,
                        num_samples=1,
                        max_new_tokens=0,
                        top_p=0.9,
                        repetition_penalty=1.5,
                        temperature=0.7,
                        compile=False,
                        iterative_prompt=True,
                        chunk_length=300,
                        prompt_text=prompt_text_list,
                        prompt_tokens=prompt_tokens_list,
                    )

                    for response in generator:
                        if self._cancel_event.is_set():
                            logger.info("TTS generation cancelled.")
                            return

                        if response.action == "sample":
                            all_codes.append(response.codes)
                            if on_progress:
                                on_progress("Generating speech...", 0.6)

                            # Decode this chunk immediately for streaming playback
                            if on_chunk:
                                try:
                                    chunk_codes = response.codes.to(self.device)
                                    chunk_lengths = torch.tensor(
                                        [chunk_codes.shape[1]], device=self._codec.device
                                    )
                                    with torch.no_grad():
                                        chunk_audio = self._codec.decode(
                                            indices=chunk_codes[None],
                                            feature_lengths=chunk_lengths,
                                        )[0].squeeze()
                                    chunk_np = chunk_audio.cpu().detach().float().numpy()
                                    on_chunk(chunk_np, self._codec.spec_transform.sample_rate)
                                except Exception as ce:
                                    logger.warning("Chunk decode error (non-fatal): %s", ce)

                        elif response.action == "next":
                            break

                if not all_codes:
                    raise RuntimeError("No audio codes generated.")

                if on_progress:
                    on_progress("Decoding to audio...", 0.8)

                # Decode full accumulated codes to audio for saving
                merged_codes = torch.cat(all_codes, dim=1).to(self.device)
                with torch.no_grad():
                    feature_lengths = torch.tensor([merged_codes.shape[1]], device=self._codec.device)
                    audio = self._codec.decode(
                        indices=merged_codes[None],
                        feature_lengths=feature_lengths,
                    )[0].squeeze()

                audio_np = audio.cpu().detach().float().numpy()


                # Save output
                if output_path is None:
                    output_path = os.path.join(
                        tempfile.gettempdir(),
                        f"fishtalk_tts_{int(time.time())}.wav"
                    )

                sample_rate = self._codec.spec_transform.sample_rate
                sf.write(output_path, audio_np, sample_rate)
                logger.info("TTS output saved: %s", output_path)

                if on_progress:
                    on_progress("Done!", 1.0)
                if on_complete:
                    on_complete(output_path)

                # Cleanup
                del merged_codes, all_codes
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            except Exception as exc:
                logger.error("TTS generation error: %s", exc, exc_info=True)
                if on_error:
                    on_error(exc)

        self._worker_thread = threading.Thread(
            target=_worker, daemon=True, name="TTS-Generate"
        )
        self._worker_thread.start()

    def generate_playlist(
        self,
        items: List[dict],
        voice_profile: dict = None,
        speed: float = 1.0,
        on_item_start: Callable[[int, str], None] = None,
        on_item_complete: Callable[[int, str], None] = None,
        on_playlist_complete: Callable = None,
        on_progress: Callable[[str, float], None] = None,
        on_error: Callable[[Exception], None] = None,
    ):
        """
        Generate TTS for a playlist of text items sequentially.

        Args:
            items: List of dicts with keys: 'name', 'text'
            voice_profile: Dict with 'wav_path' and/or 'tokens_path', 'prompt_text'
            speed: Playback speed multiplier.
            on_item_start:    Callback(index, name) when starting an item.
            on_item_complete: Callback(index, wav_path) when item is done.
            on_playlist_complete: Callback when all items are done.
            on_progress: Callback(status, fraction) for progress updates.
            on_error: Callback(Exception) on failure.
        """
        self._cancel_event.clear()

        def _worker():
            try:
                for idx, item in enumerate(items):
                    if self._cancel_event.is_set():
                        break

                    name = item.get("name", f"Item {idx + 1}")
                    text = item.get("text", "")

                    if on_item_start:
                        on_item_start(idx, name)

                    # Synchronous generation within the thread
                    done_event = threading.Event()
                    result = {"path": None, "error": None}

                    def _on_done(path):
                        result["path"] = path
                        done_event.set()

                    def _on_err(exc):
                        result["error"] = exc
                        done_event.set()

                    ref_wav = None
                    ref_tokens = None
                    prompt_text = None

                    if voice_profile:
                        ref_wav = voice_profile.get("wav_path")
                        tokens_path = voice_profile.get("tokens_path")
                        if tokens_path and os.path.isfile(tokens_path):
                            ref_tokens = np.load(tokens_path)
                        prompt_text = voice_profile.get("prompt_text", "")

                    self.generate(
                        text=text,
                        reference_wav=ref_wav,
                        reference_tokens=ref_tokens,
                        prompt_text=prompt_text,
                        speed=speed,
                        on_progress=on_progress,
                        on_complete=_on_done,
                        on_error=_on_err,
                    )
                    done_event.wait()

                    if result["error"]:
                        if on_error:
                            on_error(result["error"])
                        break

                    if on_item_complete and result["path"]:
                        on_item_complete(idx, result["path"])

                if not self._cancel_event.is_set() and on_playlist_complete:
                    on_playlist_complete()

            except Exception as exc:
                logger.error("Playlist error: %s", exc, exc_info=True)
                if on_error:
                    on_error(exc)

        t = threading.Thread(target=_worker, daemon=True, name="TTS-Playlist")
        t.start()

    def cancel(self):
        """Cancel an ongoing generation."""
        self._cancel_event.set()
        logger.info("TTS cancel requested.")

    def is_busy(self) -> bool:
        return (
            self._worker_thread is not None
            and self._worker_thread.is_alive()
        )
