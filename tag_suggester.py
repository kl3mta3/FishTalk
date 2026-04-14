"""
FishTalk — Tag Suggester

Provides two levels of emotion/prosody tag suggestion for Fish Speech text:
  1. Rule-based (instant, no dependencies beyond vaderSentiment)
  2. LLM-based via Qwen 2.5 0.5B GGUF (requires llama-cpp-python, ~400 MB model)

Fish Speech tag reference:
  Emotion (parenthesis, before sentence):
    (excited) (happy) (sad) (angry) (surprised) (confused)
    (nervous) (confident) (satisfied) (fearful) (gentle) (serious)
  Voice effects (square bracket, inline):
    [laugh]  [whisper]  [breath]  [sigh]
"""

import logging
import os
import re
import subprocess
import sys
import threading
from typing import Optional, Callable

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

logger = logging.getLogger("FishTalk.tags")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(APP_DIR, "models")
QWEN_MODEL_FILENAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
QWEN_MODEL_PATH = os.path.join(MODELS_DIR, QWEN_MODEL_FILENAME)
QWEN_HF_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"

# ---------------------------------------------------------------------------
# Tag catalogue (used by both the editor panel and the suggester)
# ---------------------------------------------------------------------------

FISH_TAGS = {
    "Emotion": [
        ("(excited)",    "Excited / High energy"),
        ("(happy)",      "Happy / Upbeat"),
        ("(satisfied)",  "Satisfied / Content"),
        ("(confident)",  "Confident / Assertive"),
        ("(gentle)",     "Gentle / Soft"),
        ("(serious)",    "Serious / Formal"),
        ("(sad)",        "Sad / Melancholy"),
        ("(angry)",      "Angry / Frustrated"),
        ("(nervous)",    "Nervous / Anxious"),
        ("(fearful)",    "Fearful / Scared"),
        ("(surprised)",  "Surprised / Shocked"),
        ("(confused)",   "Confused / Uncertain"),
    ],
    "Voice Effects": [
        ("[laugh]",      "Laughter"),
        ("[whisper]",    "Whispering"),
        ("[breath]",     "Breath sound"),
        ("[sigh]",       "Sighing"),
    ],
}

# ---------------------------------------------------------------------------
# Rule-based suggestion
# ---------------------------------------------------------------------------

# (regex, tag, placement)
# placement: "before" = insert tag at start of sentence containing match
#            "inline" = insert tag immediately before the matched word
_RULES = [
    # Excitement / energy
    (re.compile(r'[!]{2,}'),
     "(excited)", "before"),
    (re.compile(r'\b(amazing|incredible|fantastic|wonderful|awesome|unbelievable|extraordinary)\b', re.I),
     "(excited)", "before"),

    # Happiness
    (re.compile(r'\b(great|perfect|love|joy|delight|pleased|glad|thrilled|overjoyed)\b', re.I),
     "(happy)", "before"),

    # Sadness
    (re.compile(r'\b(sad|unfortunately|sorry|apologize|miss|lost|died|death|crying|tears|grief|mourning)\b', re.I),
     "(sad)", "before"),

    # Anger
    (re.compile(r'\b(angry|furious|rage|hate|frustrated|annoying|terrible|awful|outraged|infuriated)\b', re.I),
     "(angry)", "before"),

    # Fear / nervousness
    (re.compile(r'\b(afraid|terrified|scared|frightened|nervous|anxious|trembling|panic)\b', re.I),
     "(fearful)", "before"),

    # Confidence
    (re.compile(r'\b(certainly|absolutely|definitely|without doubt|I am sure|I know|clearly)\b', re.I),
     "(confident)", "before"),

    # Surprise
    (re.compile(r'\b(what\?|no way|unbelievable|shocking|suddenly|startled|gasp)\b', re.I),
     "(surprised)", "before"),

    # Laughter — inline
    (re.compile(r'\b(haha|hehe|lol|chuckled|giggled|laughed|cackled|snickered)\b', re.I),
     "[laugh]", "inline"),

    # Whisper — inline
    (re.compile(r'\b(whispered|quietly|softly|in a hushed|murmured|breathed)\b', re.I),
     "[whisper]", "inline"),
]


def suggest_tags(text: str) -> str:
    """
    Rule-based tag suggestion.  Scans the text sentence by sentence and
    inserts the most appropriate tag per sentence.  Returns the tagged text.

    Only one emotion tag is added per sentence (the first rule that matches).
    Inline [effects] can be added on top.
    """
    # Split into sentences preserving delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result = []

    for sentence in sentences:
        emotion_added = False
        tagged = sentence

        for pattern, tag, placement in _RULES:
            if not pattern.search(sentence):
                continue

            if placement == "before" and not emotion_added:
                # Only one emotion tag per sentence
                if tag.startswith("("):
                    tagged = tag + " " + tagged
                    emotion_added = True
                else:
                    # bracket tag at start too
                    tagged = tag + " " + tagged

            elif placement == "inline":
                # Insert tag before first match
                match = pattern.search(tagged)
                if match:
                    tagged = tagged[:match.start()] + tag + " " + tagged[match.start():]

        result.append(tagged)

    return " ".join(result)


# ---------------------------------------------------------------------------
# Qwen 0.5B GGUF — LLM-based tagging
# ---------------------------------------------------------------------------

_llm = None          # llama_cpp.Llama instance (loaded on demand)
_llm_lock = threading.Lock()


def is_llm_available() -> bool:
    """Return True if llama-cpp-python is installed."""
    try:
        import llama_cpp  # noqa
        return True
    except ImportError:
        return False


def install_llama_cpp(
    on_line: Optional[Callable[[str], None]] = None,
    on_complete: Optional[Callable[[bool, str], None]] = None,
):
    """
    Install llama-cpp-python (CPU pre-built wheel) via pip in a background thread.

    on_line(text)          — called with each line of pip output
    on_complete(ok, msg)   — called when done; ok=True on success
    """
    def _worker():
        # Resolve pip inside the active venv if present
        app_dir = os.path.dirname(os.path.abspath(__file__))
        venv_pip = os.path.join(app_dir, "venv", "Scripts", "pip.exe")
        pip_cmd = [venv_pip] if os.path.isfile(venv_pip) else [sys.executable, "-m", "pip"]

        cmd = pip_cmd + [
            "install", "llama-cpp-python",
            "--prefer-binary",   # use pre-built wheel, never compile from source
            "--upgrade",
            "--quiet", "--progress-bar", "off",
        ]

        try:
            if on_line:
                on_line("Starting llama-cpp-python install…")

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=CREATE_NO_WINDOW,
            )

            for raw_line in proc.stdout:
                line = raw_line.rstrip()
                if line and on_line:
                    on_line(line)

            proc.wait()

            if proc.returncode == 0:
                logger.info("llama-cpp-python installed successfully.")
                if on_complete:
                    on_complete(True, "llama-cpp-python installed.")
            else:
                msg = "pip exited with code " + str(proc.returncode)
                logger.error("llama-cpp-python install failed: %s", msg)
                if on_complete:
                    on_complete(False, msg)

        except Exception as exc:
            logger.error("llama-cpp-python install error: %s", exc)
            if on_complete:
                on_complete(False, str(exc))

    threading.Thread(target=_worker, daemon=True, name="LlamaCppInstall").start()


def is_qwen_model_ready() -> bool:
    """Return True if the Qwen GGUF model file exists on disk."""
    return os.path.isfile(QWEN_MODEL_PATH)


def download_qwen_model(
    on_progress: Optional[Callable[[str, float], None]] = None,
    on_complete: Optional[Callable[[bool, str], None]] = None,
):
    """Download the Qwen 2.5 0.5B Q4_K_M GGUF from HuggingFace in a background thread."""

    def _worker():
        os.makedirs(MODELS_DIR, exist_ok=True)
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            if on_complete:
                on_complete(False, "huggingface_hub not installed.")
            return

        try:
            if on_progress:
                on_progress(f"Downloading {QWEN_MODEL_FILENAME} (~400 MB)…", 0.05)
            logger.info("Downloading Qwen model from %s", QWEN_HF_REPO)

            hf_hub_download(
                repo_id=QWEN_HF_REPO,
                filename=QWEN_MODEL_FILENAME,
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False,
            )

            # hf_hub_download may nest inside a subfolder — move to flat MODELS_DIR
            nested = os.path.join(MODELS_DIR, QWEN_MODEL_FILENAME.split("/")[-1])
            if not os.path.isfile(QWEN_MODEL_PATH) and os.path.isfile(nested):
                import shutil
                shutil.move(nested, QWEN_MODEL_PATH)

            if is_qwen_model_ready():
                logger.info("Qwen model downloaded: %s", QWEN_MODEL_PATH)
                if on_complete:
                    on_complete(True, "Qwen model ready.")
            else:
                if on_complete:
                    on_complete(False, "Download completed but model file not found.")
        except Exception as exc:
            logger.error("Qwen download failed: %s", exc)
            if on_complete:
                on_complete(False, str(exc))

    threading.Thread(target=_worker, daemon=True, name="QwenDownload").start()


def _load_llm():
    """Load the Qwen GGUF model (call inside _llm_lock)."""
    global _llm
    if _llm is not None:
        return
    from llama_cpp import Llama
    logger.info("Loading Qwen model: %s", QWEN_MODEL_PATH)
    _llm = Llama(
        model_path=QWEN_MODEL_PATH,
        n_ctx=2048,
        n_threads=max(1, os.cpu_count() - 1),
        n_gpu_layers=0,      # CPU only — keeps VRAM free for TTS
        verbose=False,
    )
    logger.info("Qwen model loaded.")


def prewarm_llm():
    """Load the Qwen model in the background so it's ready for immediate use."""
    if is_llm_available() and is_qwen_model_ready():
        with _llm_lock:
            _load_llm()


def unload_llm():
    """Explicitly unload the Qwen model to reclaim RAM."""
    global _llm
    with _llm_lock:
        if _llm is not None:
            del _llm
            _llm = None
            import gc; gc.collect()
            logger.info("Qwen model unloaded.")


_GRAMMAR_SYSTEM_PROMPT = """You are a proofreading assistant preparing text for text-to-speech narration.
Your ONLY job is to fix spelling mistakes and grammar errors in the text provided.

Rules:
1. NEVER change the meaning, tone, or style of the writing.
2. NEVER alter proper nouns, character names, place names, invented words, or fictional terminology — even if they look unusual. If it could be a deliberate creative choice, leave it alone.
3. Fix only clear, unambiguous spelling errors and grammatical mistakes.
4. Preserve all punctuation, paragraph breaks, and formatting.
5. Return ONLY the corrected text. No explanations, no commentary, no extra formatting."""

_SYSTEM_PROMPT = """You are a TTS preprocessing assistant for Fish Speech.
Your ONLY job is to add emotion/prosody tags to text — never change, add, or remove words.

Available tags:
  Emotion (place at START of sentence): (excited) (happy) (satisfied) (confident)
    (gentle) (serious) (sad) (angry) (nervous) (fearful) (surprised) (confused)
  Voice effects (place INLINE before the word): [laugh] [whisper] [breath] [sigh]

Rules:
1. Never modify any words — only INSERT tags.
2. Be conservative — only tag sentences with a clear emotional tone.
3. One emotion tag per sentence maximum.
4. Return ONLY the tagged text. No explanations, no extra formatting."""


def generate_tags(
    text: str,
    on_progress: Optional[Callable[[str, float], None]] = None,
) -> str:
    """
    Use Qwen 0.5B to insert Fish Speech tags into text.

    Processes the text in paragraph-sized chunks to stay within context limits.
    Returns the fully tagged text.

    Raises RuntimeError if llama-cpp-python or the model file is missing.
    """
    if not is_llm_available():
        raise RuntimeError(
            "llama-cpp-python is not installed.\n"
            "Install it with: pip install llama-cpp-python"
        )
    if not is_qwen_model_ready():
        raise RuntimeError(
            f"Qwen model not found at {QWEN_MODEL_PATH}.\n"
            "Use the 'Download AI Tagger' button to fetch it."
        )

    with _llm_lock:
        _load_llm()

    # Split into manageable paragraphs (~500 chars each to stay in context)
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return text

    tagged_parts = []
    for i, para in enumerate(paragraphs):
        if on_progress:
            on_progress(
                f"Tagging paragraph {i + 1}/{len(paragraphs)}…",
                0.1 + 0.85 * (i / len(paragraphs)),
            )

        # Sub-chunk if paragraph is very long
        chunks = _chunk_text(para, max_chars=600)
        para_result = []
        for chunk in chunks:
            with _llm_lock:
                output = _llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": chunk},
                    ],
                    max_tokens=int(len(chunk) * 1.5) + 64,
                    temperature=0.2,
                    top_p=0.9,
                )
            tagged_chunk = output["choices"][0]["message"]["content"].strip()
            # Sanity check: result shouldn't be much longer than input
            # (if model added prose, fall back to the original)
            if len(tagged_chunk) > len(chunk) * 2.5:
                logger.warning("LLM output too long — using rule-based fallback for this chunk.")
                tagged_chunk = suggest_tags(chunk)
            para_result.append(tagged_chunk)

        tagged_parts.append(" ".join(para_result))

    if on_progress:
        on_progress("Done", 1.0)

    return "\n\n".join(tagged_parts)


def grammar_check(
    text: str,
    on_progress: Optional[Callable[[str, float], None]] = None,
) -> str:
    """
    Use Qwen 0.5B to fix spelling and grammar errors in text.

    Preserves proper nouns, fictional terms, and creative style choices.
    Returns the corrected text.

    Raises RuntimeError if llama-cpp-python or the model file is missing.
    """
    if not is_llm_available():
        raise RuntimeError(
            "llama-cpp-python is not installed.\n"
            "Install it via the Generate Tags (AI) button."
        )
    if not is_qwen_model_ready():
        raise RuntimeError(
            f"Qwen model not found at {QWEN_MODEL_PATH}.\n"
            "Use the Generate Tags (AI) button to download it."
        )

    with _llm_lock:
        _load_llm()

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return text

    corrected_parts = []
    for i, para in enumerate(paragraphs):
        if on_progress:
            on_progress(
                f"Checking paragraph {i + 1}/{len(paragraphs)}…",
                0.1 + 0.85 * (i / len(paragraphs)),
            )

        chunks = _chunk_text(para, max_chars=600)
        para_result = []
        for chunk in chunks:
            with _llm_lock:
                output = _llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": _GRAMMAR_SYSTEM_PROMPT},
                        {"role": "user",   "content": chunk},
                    ],
                    max_tokens=int(len(chunk) * 1.5) + 64,
                    temperature=0.1,   # lower = more conservative corrections
                    top_p=0.9,
                )
            result = output["choices"][0]["message"]["content"].strip()
            # Sanity check: if model went off the rails, keep original chunk
            if len(result) > len(chunk) * 2.5 or len(result) < len(chunk) * 0.5:
                logger.warning("Grammar LLM output suspicious length — keeping original chunk.")
                result = chunk
            para_result.append(result)

        corrected_parts.append(" ".join(para_result))

    if on_progress:
        on_progress("Done", 1.0)

    return "\n\n".join(corrected_parts)


# Fish Speech supports inline prosody/emotion tags — encourage their use.
_ENHANCE_SYSTEM_PROMPT_FISH = """You are a TTS preparation assistant for Fish Speech, a neural voice engine.
Your job is to make text sound natural and expressive when read aloud.

Improvements you should make:
- Add commas, em-dashes (—), or ellipses (...) where a speaker would naturally pause or breathe
- Break very long sentences into shorter ones for better pacing
- Spell out numbers and abbreviations in spoken form (e.g. "3" → "three", "Dr." → "Doctor", "e.g." → "for example")
- Simplify awkward written constructions that sound unnatural when spoken
- Where emotion is clearly present in the text, insert ONE Fish Speech tag at the START of the sentence:
    Emotions: (excited) (happy) (satisfied) (confident) (gentle) (serious) (sad) (angry) (nervous) (fearful) (surprised) (confused)
    Inline effects (place directly before the relevant word): [laugh] [breath] [sigh] [whisper]
- Use [breath] at natural inhale points in long passages

Rules:
1. Preserve all meaning, names, proper nouns, and fictional terminology exactly.
2. Do NOT change the tone or style of the writing.
3. Be conservative with tags — only add them where the emotion or effect is clearly warranted.
4. Return ONLY the improved text. No explanations, no preamble."""

# Kokoro does not parse Fish Speech tags — focus on punctuation and pacing only.
_ENHANCE_SYSTEM_PROMPT_KOKORO = """You are a TTS preparation assistant for Kokoro, a clean neural voice engine.
Your job is to make text sound natural and well-paced when read aloud.

Improvements you should make:
- Add commas, em-dashes (—), or ellipses (...) where a speaker would naturally pause or breathe
- Break very long sentences into shorter ones for better pacing
- Spell out numbers and abbreviations in spoken form (e.g. "3" → "three", "Dr." → "Doctor", "e.g." → "for example")
- Simplify awkward written constructions that sound unnatural when spoken

Rules:
1. Preserve all meaning, names, proper nouns, and fictional terminology exactly.
2. Do NOT add any special tags, brackets, or markup — Kokoro reads plain text only.
3. Do NOT change the tone or style of the writing.
4. Return ONLY the improved text. No explanations, no preamble."""

_TONE_SYSTEM_PROMPT_TEMPLATE = """You are a writing assistant. Rewrite the following text in a {tone} tone.

Rules:
1. Preserve ALL core information, events, and meaning.
2. Preserve all proper nouns, character names, place names, and fictional terminology exactly.
3. Keep roughly the same length — do not add new content or remove key details.
4. Return ONLY the rewritten text. No explanations, no preamble."""

TONE_OPTIONS = [
    "Neutral",
    "Casual / Conversational",
    "Formal / Professional",
    "Dramatic / Cinematic",
    "Energetic / Upbeat",
    "Calm / Soothing",
    "Humorous / Playful",
    "Narrative / Storytelling",
    "Tense / Suspenseful",
]


def enhance_for_tts(
    text: str,
    engine: str = "fish14",
    on_progress: Optional[Callable[[str, float], None]] = None,
) -> str:
    """
    Use Qwen 0.5B to improve text for natural TTS delivery.

    engine: "kokoro" uses a plain-text prompt (no tags).
            "fish14" / "fish15" uses the Fish Speech prompt (prosody tags encouraged).
    """
    if not is_llm_available():
        raise RuntimeError("llama-cpp-python is not installed.")
    if not is_qwen_model_ready():
        raise RuntimeError(f"Qwen model not found at {QWEN_MODEL_PATH}.")

    system_prompt = (
        _ENHANCE_SYSTEM_PROMPT_KOKORO
        if engine == "kokoro"
        else _ENHANCE_SYSTEM_PROMPT_FISH
    )

    with _llm_lock:
        _load_llm()

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return text

    result_parts = []
    for i, para in enumerate(paragraphs):
        if on_progress:
            on_progress(f"Enhancing paragraph {i + 1}/{len(paragraphs)}…",
                        0.1 + 0.85 * (i / len(paragraphs)))
        chunks = _chunk_text(para, max_chars=600)
        para_result = []
        for chunk in chunks:
            with _llm_lock:
                output = _llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": chunk},
                    ],
                    max_tokens=int(len(chunk) * 1.6) + 64,
                    temperature=0.3,
                    top_p=0.9,
                )
            result = output["choices"][0]["message"]["content"].strip()
            if len(result) > len(chunk) * 2.5 or len(result) < len(chunk) * 0.4:
                logger.warning("enhance_for_tts: suspicious output length — keeping original.")
                result = chunk
            para_result.append(result)
        result_parts.append(" ".join(para_result))

    if on_progress:
        on_progress("Done", 1.0)
    return "\n\n".join(result_parts)


def rewrite_tone(
    text: str,
    tone: str,
    on_progress: Optional[Callable[[str, float], None]] = None,
) -> str:
    """
    Use Qwen 0.5B to rewrite text in the given tone.
    tone should be one of TONE_OPTIONS.
    """
    if not is_llm_available():
        raise RuntimeError("llama-cpp-python is not installed.")
    if not is_qwen_model_ready():
        raise RuntimeError(f"Qwen model not found at {QWEN_MODEL_PATH}.")

    system_prompt = _TONE_SYSTEM_PROMPT_TEMPLATE.format(tone=tone)

    with _llm_lock:
        _load_llm()

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return text

    result_parts = []
    for i, para in enumerate(paragraphs):
        if on_progress:
            on_progress(f"Rewriting paragraph {i + 1}/{len(paragraphs)}…",
                        0.1 + 0.85 * (i / len(paragraphs)))
        chunks = _chunk_text(para, max_chars=600)
        para_result = []
        for chunk in chunks:
            with _llm_lock:
                output = _llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": chunk},
                    ],
                    max_tokens=int(len(chunk) * 2.0) + 128,
                    temperature=0.7,
                    top_p=0.95,
                )
            result = output["choices"][0]["message"]["content"].strip()
            if len(result) > len(chunk) * 3.5 or len(result) < len(chunk) * 0.3:
                logger.warning("rewrite_tone: suspicious output length — keeping original.")
                result = chunk
            para_result.append(result)
        result_parts.append(" ".join(para_result))

    if on_progress:
        on_progress("Done", 1.0)
    return "\n\n".join(result_parts)


def _chunk_text(text: str, max_chars: int = 600) -> list:
    """Split text into sentence-boundary chunks no larger than max_chars."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, buf = [], ""
    for s in sentences:
        if buf and len(buf) + len(s) + 1 > max_chars:
            chunks.append(buf.strip())
            buf = s
        else:
            buf = (buf + " " + s).strip() if buf else s
    if buf:
        chunks.append(buf.strip())
    return chunks or [text]
