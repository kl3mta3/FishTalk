"""
FishTalk — User Interface.

CustomTkinter dark-mode GUI with 4 tabs:
  Tab 1: Read Aloud (TTS)
  Tab 2: Transcribe (STT)
  Tab 3: Voice Lab
  Tab 4: Settings
"""

import logging
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from settings import Settings, detect_cuda, get_bundled_fish_speech_path, validate_fish_speech_path
from cuda_setup import has_nvidia_gpu, get_nvidia_gpu_name, is_cuda_torch_installed, install_cuda_pytorch, revert_to_cpu_pytorch
from kokoro_engine import KOKORO_VOICES, DEFAULT_VOICE, DEFAULT_VOICE_DISPLAY, install_kokoro, _is_kokoro_installed
from utils import (
    get_ram_usage,
    is_ffmpeg_available,
    read_file,
    export_mp3,
    export_txt,
    export_docx,
    export_pdf,
)
from voice_manager import VoiceManager

logger = logging.getLogger("FishTalk.ui")

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = {
    "bg_dark":       "#0f0f1a",
    "bg_card":       "#1a1a2e",
    "bg_card_hover": "#222240",
    "bg_input":      "#16213e",
    "accent":        "#4361ee",
    "accent_hover":  "#3a56d4",
    "accent_light":  "#6c83f7",
    "success":       "#06d6a0",
    "warning":       "#ffd166",
    "danger":        "#ef476f",
    "text_primary":  "#e8e8f0",
    "text_secondary":"#9a9ab0",
    "text_muted":    "#5a5a7a",
    "border":        "#2a2a4a",
}

FONT_FAMILY = "Segoe UI"


# ============================================================================
# MAIN UI CLASS
# ============================================================================

class FishTalkUI:
    """Builds and manages the entire FishTalk user interface."""

    def __init__(
        self,
        root: ctk.CTk,
        settings: Settings,
        tts_engine,
        stt_engine,
        voice_manager: VoiceManager,
    ):
        self.root = root
        self.settings = settings
        self.tts = tts_engine
        self.stt = stt_engine
        self.voices = voice_manager

        # Playback state
        self._playlist_items = []   # List of dicts: {name, text, path}
        self._current_playing = -1
        self._is_playing = False
        self._is_paused = False
        self._playback_stream = None

        # Audio playback
        self._audio_data = None
        self._audio_sr = None
        self._play_position = 0

        self._build_ui()
        self._start_ram_monitor()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the full tabbed interface."""
        self.root.configure(fg_color=COLORS["bg_dark"])

        # Header
        header = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"], height=60)
        header.pack(fill="x", padx=20, pady=(15, 5))
        header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header,
            text="🐟  FishTalk",
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["accent_light"],
        )
        title_label.pack(side="left", pady=10)

        subtitle = ctk.CTkLabel(
            header,
            text="Local AI Voice Studio",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"],
        )
        subtitle.pack(side="left", padx=(12, 0), pady=(18, 10))

        # Tab view
        self.tabview = ctk.CTkTabview(
            self.root,
            fg_color=COLORS["bg_card"],
            segmented_button_fg_color=COLORS["bg_input"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_input"],
            segmented_button_unselected_hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=12,
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create tabs
        self.tab_tts = self.tabview.add("📖  Read Aloud")
        self.tab_stt = self.tabview.add("🎙  Transcribe")
        self.tab_voices = self.tabview.add("🧬  Voice Lab")
        self.tab_settings = self.tabview.add("⚙  Settings")

        self._build_tts_tab()
        self._build_stt_tab()
        self._build_voice_lab_tab()
        self._build_settings_tab()

        # Lock Voice Lab tab when Kokoro engine is active
        if getattr(self.settings, 'engine', 'fish14') == 'kokoro':
            self._lock_voice_lab()

        # Bind tab change for memory saver
        self.tabview.configure(command=self._on_tab_changed)

    # ==================================================================
    # TAB 1: Read Aloud (TTS)
    # ==================================================================

    def _build_tts_tab(self):
        tab = self.tab_tts

        # Top row — Drop zone + controls
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        # Drop zone
        self.tts_drop = ctk.CTkFrame(
            top,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            border_width=2,
            corner_radius=10,
            height=100,
        )
        self.tts_drop.pack(fill="x", pady=(0, 10))
        self.tts_drop.pack_propagate(False)

        self.tts_drop_label = ctk.CTkLabel(
            self.tts_drop,
            text="📄  Drag & drop .txt, .pdf, .docx, or .epub files here\nor click to browse",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        self.tts_drop_label.pack(expand=True)
        self.tts_drop_label.bind("<Button-1>", self._tts_browse_file)

        # Register drag-and-drop
        try:
            from tkinterdnd2 import DND_FILES
            self.tts_drop.drop_target_register(DND_FILES)
            self.tts_drop.dnd_bind("<<Drop>>", self._tts_on_drop)
        except Exception as e:
            logger.warning("Drag-and-drop not available: %s", e)

        # Controls row
        controls = ctk.CTkFrame(tab, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=5)

        # Voice selector
        voice_frame = ctk.CTkFrame(controls, fg_color="transparent")
        voice_frame.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            voice_frame,
            text="Voice",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        # --- Voice selector (context-sensitive) ---
        is_kokoro = getattr(self.settings, 'engine', 'fish14') == 'kokoro'

        if is_kokoro:
            # Kokoro mode: show preset voice dropdown
            kokoro_display_names = list(KOKORO_VOICES.keys())
            saved_kokoro_id = getattr(self.settings, 'kokoro_voice', DEFAULT_VOICE)
            # Find display name matching saved voice ID
            saved_display = next(
                (k for k, v in KOKORO_VOICES.items() if v == saved_kokoro_id),
                kokoro_display_names[0]
            )
            self.tts_voice_var = ctk.StringVar(value=saved_display)
            self.tts_voice_menu = ctk.CTkOptionMenu(
                voice_frame,
                values=kokoro_display_names,
                variable=self.tts_voice_var,
                width=200,
                fg_color=COLORS["bg_input"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["bg_card"],
                dropdown_hover_color=COLORS["bg_card_hover"],
                font=(FONT_FAMILY, 12),
                command=self._on_kokoro_voice_change,
            )
        else:
            # Fish-Speech mode: show cloned voice profiles
            voice_names = self.voices.get_voice_names()
            self.tts_voice_var = ctk.StringVar(value=voice_names[0] if voice_names else "Default (Random)")
            self.tts_voice_menu = ctk.CTkOptionMenu(
                voice_frame,
                values=voice_names if voice_names else ["Default (Random)"],
                variable=self.tts_voice_var,
                width=180,
                fg_color=COLORS["bg_input"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["bg_card"],
                dropdown_hover_color=COLORS["bg_card_hover"],
                font=(FONT_FAMILY, 12),
            )
        self.tts_voice_menu.pack()

        # Speed slider
        speed_frame = ctk.CTkFrame(controls, fg_color="transparent")
        speed_frame.pack(side="left", padx=15)

        self.speed_label = ctk.CTkLabel(
            speed_frame,
            text="Speed: 1.0x",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        )
        self.speed_label.pack(anchor="w")

        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.5,
            to=2.0,
            number_of_steps=30,
            width=140,
            progress_color=COLORS["accent"],
            button_color=COLORS["accent_light"],
            button_hover_color=COLORS["accent"],
        )
        self.speed_slider.set(self.settings.speed)
        self.speed_slider.configure(command=self._on_speed_change)
        self.speed_slider.pack()

        # Volume slider
        vol_frame = ctk.CTkFrame(controls, fg_color="transparent")
        vol_frame.pack(side="left", padx=15)

        self.vol_label = ctk.CTkLabel(
            vol_frame,
            text=f"Volume: {self.settings.volume}%",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        )
        self.vol_label.pack(anchor="w")

        self.vol_slider = ctk.CTkSlider(
            vol_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            width=140,
            progress_color=COLORS["success"],
            button_color=COLORS["success"],
        )
        self.vol_slider.set(self.settings.volume)
        self.vol_slider.configure(command=self._on_volume_change)
        self.vol_slider.pack()

        # Cadence slider
        cad_frame = ctk.CTkFrame(controls, fg_color="transparent")
        cad_frame.pack(side="left", padx=15)

        self.cad_label = ctk.CTkLabel(
            cad_frame,
            text=f"Cadence: {self.settings.cadence}%",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        )
        self.cad_label.pack(anchor="w")

        self.cad_slider = ctk.CTkSlider(
            cad_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            width=140,
            progress_color=COLORS["warning"],
            button_color=COLORS["warning"],
        )
        self.cad_slider.set(self.settings.cadence)
        self.cad_slider.configure(command=self._on_cadence_change)
        self.cad_slider.pack()

        # Playlist
        playlist_label = ctk.CTkLabel(
            tab,
            text="📋  Playlist",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text_primary"],
        )
        playlist_label.pack(anchor="w", padx=15, pady=(10, 2))

        self.playlist_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS["bg_input"],
            corner_radius=8,
            height=180,
            scrollbar_button_color=COLORS["accent"],
        )
        self.playlist_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.playlist_empty_label = ctk.CTkLabel(
            self.playlist_frame,
            text="No files in queue. Drop files above to add them.",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_muted"],
        )
        self.playlist_empty_label.pack(pady=30)

        # Progress bar
        self.tts_progress = ctk.CTkProgressBar(
            tab,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_input"],
            height=6,
            corner_radius=3,
        )
        self.tts_progress.pack(fill="x", padx=15, pady=(5, 5))
        self.tts_progress.set(0)

        self.tts_status = ctk.CTkLabel(
            tab,
            text="Ready",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
        )
        self.tts_status.pack(anchor="w", padx=15)

        # Transport buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))

        btn_style = {
            "font": (FONT_FAMILY, 13, "bold"),
            "corner_radius": 8,
            "height": 38,
            "width": 110,
        }

        self.btn_play = ctk.CTkButton(
            btn_frame,
            text="▶  Play",
            fg_color=COLORS["success"],
            hover_color="#05b890",
            command=self._tts_play,
            **btn_style,
        )
        self.btn_play.pack(side="left", padx=(0, 8))

        self.btn_pause = ctk.CTkButton(
            btn_frame,
            text="⏸  Pause",
            fg_color=COLORS["warning"],
            hover_color="#e6bc5c",
            text_color="#1a1a2e",
            command=self._tts_pause,
            **btn_style,
        )
        self.btn_pause.pack(side="left", padx=(0, 8))

        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text="⏹  Stop",
            fg_color=COLORS["danger"],
            hover_color="#d43d62",
            command=self._tts_stop,
            **btn_style,
        )
        self.btn_stop.pack(side="left", padx=(0, 8))

        self.btn_save_mp3 = ctk.CTkButton(
            btn_frame,
            text="💾  Save MP3",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._tts_save_mp3,
            **btn_style,
        )
        self.btn_save_mp3.pack(side="left", padx=(0, 8))

        self.btn_clear_playlist = ctk.CTkButton(
            btn_frame,
            text="🗑  Clear",
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_card_hover"],
            border_color=COLORS["border"],
            border_width=1,
            command=self._tts_clear_playlist,
            **btn_style,
        )
        self.btn_clear_playlist.pack(side="right")

        # Work Silent toggle — generate only, no audio output
        self.silent_mode_var = ctk.BooleanVar(value=getattr(self.settings, 'silent_mode', False))
        silent_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        silent_frame.pack(side="right", padx=(0, 12))
        ctk.CTkLabel(
            silent_frame,
            text="🔇 Work Silent",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 6))
        self.silent_switch = ctk.CTkSwitch(
            silent_frame,
            text="",
            variable=self.silent_mode_var,
            width=40,
            progress_color=COLORS["accent"],
            command=self._on_silent_toggle,
        )
        self.silent_switch.pack(side="left")

    # ==================================================================
    # TAB 2: Transcribe (STT)
    # ==================================================================

    def _build_stt_tab(self):
        tab = self.tab_stt

        # Top row — drop zone + controls
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        # Drop zone
        self.stt_drop = ctk.CTkFrame(
            top,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            border_width=2,
            corner_radius=10,
            height=80,
        )
        self.stt_drop.pack(fill="x", pady=(0, 10))
        self.stt_drop.pack_propagate(False)

        self.stt_drop_label = ctk.CTkLabel(
            self.stt_drop,
            text="🎧  Drag & drop .wav or .mp3 audio files here\nor click to browse",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        self.stt_drop_label.pack(expand=True)
        self.stt_drop_label.bind("<Button-1>", self._stt_browse_file)

        # Register drag-and-drop
        try:
            from tkinterdnd2 import DND_FILES
            self.stt_drop.drop_target_register(DND_FILES)
            self.stt_drop.dnd_bind("<<Drop>>", self._stt_on_drop)
        except Exception as e:
            logger.warning("Drag-and-drop not available for STT: %s", e)

        # Controls row
        stt_controls = ctk.CTkFrame(tab, fg_color="transparent")
        stt_controls.pack(fill="x", padx=10, pady=5)

        # Model size selector
        model_frame = ctk.CTkFrame(stt_controls, fg_color="transparent")
        model_frame.pack(side="left")

        ctk.CTkLabel(
            model_frame,
            text="Whisper Model",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        self.stt_model_var = ctk.StringVar(value=self.settings.whisper_model_size)
        self.stt_model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=["tiny", "base", "small", "medium", "large-v3"],
            variable=self.stt_model_var,
            width=150,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            font=(FONT_FAMILY, 12),
            command=self._on_stt_model_change,
        )
        self.stt_model_menu.pack()

        # Transcribe button
        self.btn_transcribe = ctk.CTkButton(
            stt_controls,
            text="🎙  Transcribe",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=(FONT_FAMILY, 13, "bold"),
            height=38,
            width=140,
            command=self._stt_transcribe,
        )
        self.btn_transcribe.pack(side="left", padx=15)

        self.btn_stt_cancel = ctk.CTkButton(
            stt_controls,
            text="⏹  Cancel",
            fg_color=COLORS["danger"],
            hover_color="#d43d62",
            font=(FONT_FAMILY, 13, "bold"),
            height=38,
            width=100,
            command=self._stt_cancel,
        )
        self.btn_stt_cancel.pack(side="left")

        # File info label
        self.stt_file_label = ctk.CTkLabel(
            stt_controls,
            text="No file loaded",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
        )
        self.stt_file_label.pack(side="right", padx=10)

        # Progress bar
        self.stt_progress = ctk.CTkProgressBar(
            tab,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_input"],
            height=6,
            corner_radius=3,
        )
        self.stt_progress.pack(fill="x", padx=15, pady=(5, 5))
        self.stt_progress.set(0)

        # Transcription output
        self.stt_textbox = ctk.CTkTextbox(
            tab,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            font=(FONT_FAMILY, 13),
            corner_radius=8,
            border_color=COLORS["border"],
            border_width=1,
            wrap="word",
        )
        self.stt_textbox.pack(fill="both", expand=True, padx=15, pady=5)
        self.stt_textbox.insert("1.0", "Transcription will appear here in real time...")
        self.stt_textbox.configure(state="disabled")

        # Export buttons
        export_frame = ctk.CTkFrame(tab, fg_color="transparent")
        export_frame.pack(fill="x", padx=15, pady=(5, 10))

        exp_style = {
            "font": (FONT_FAMILY, 12),
            "corner_radius": 8,
            "height": 34,
            "width": 130,
            "fg_color": COLORS["bg_input"],
            "hover_color": COLORS["bg_card_hover"],
            "border_color": COLORS["border"],
            "border_width": 1,
        }

        ctk.CTkButton(
            export_frame, text="📄  Save .txt",
            command=lambda: self._stt_export("txt"), **exp_style,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            export_frame, text="📝  Save .docx",
            command=lambda: self._stt_export("docx"), **exp_style,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            export_frame, text="📑  Save .pdf",
            command=lambda: self._stt_export("pdf"), **exp_style,
        ).pack(side="left", padx=(0, 8))

        # Store current audio path for transcription
        self._stt_audio_path = None

    # ==================================================================
    # TAB 3: Voice Lab
    # ==================================================================

    def _build_voice_lab_tab(self):
        tab = self.tab_voices

        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="🧬  Voice Profiles",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self.btn_clone = ctk.CTkButton(
            header,
            text="➕  Clone Voice",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=(FONT_FAMILY, 13, "bold"),
            height=38,
            width=150,
            corner_radius=8,
            command=self._voice_clone,
        )
        self.btn_clone.pack(side="right")

        self.btn_refresh_voices = ctk.CTkButton(
            header,
            text="🔄  Refresh",
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_card_hover"],
            border_color=COLORS["border"],
            border_width=1,
            font=(FONT_FAMILY, 12),
            height=34,
            width=100,
            corner_radius=8,
            command=self._refresh_voice_grid,
        )
        self.btn_refresh_voices.pack(side="right", padx=(0, 10))

        ctk.CTkLabel(
            tab,
            text="Upload a 15–30 second WAV reference clip to create a new voice.\n"
                 "Zero-shot cloning — no fine-tuning required.",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
            justify="left",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Voice grid (scrollable)
        self.voice_grid_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS["bg_input"],
            corner_radius=8,
            scrollbar_button_color=COLORS["accent"],
        )
        self.voice_grid_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self._refresh_voice_grid()

    def _refresh_voice_grid(self):
        """Rebuild the voice cards grid."""
        for widget in self.voice_grid_frame.winfo_children():
            widget.destroy()

        voice_list = self.voices.list_voices()

        if not voice_list:
            ctk.CTkLabel(
                self.voice_grid_frame,
                text="No voice profiles yet.\nClick 'Clone Voice' to create one.",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["text_muted"],
                justify="center",
            ).pack(pady=40)
            return

        # Grid layout
        cols = 3
        for idx, name in enumerate(voice_list):
            row = idx // cols
            col = idx % cols

            card = ctk.CTkFrame(
                self.voice_grid_frame,
                fg_color=COLORS["bg_card"],
                border_color=COLORS["border"],
                border_width=1,
                corner_radius=10,
                width=220,
                height=120,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)

            # Voice icon + name
            ctk.CTkLabel(
                card,
                text="🎤",
                font=(FONT_FAMILY, 28),
            ).pack(pady=(12, 2))

            ctk.CTkLabel(
                card,
                text=name,
                font=(FONT_FAMILY, 13, "bold"),
                text_color=COLORS["text_primary"],
            ).pack()

            # Action buttons
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(pady=(5, 8))

            ctk.CTkButton(
                btn_row,
                text="▶",
                width=35,
                height=28,
                corner_radius=6,
                fg_color=COLORS["success"],
                hover_color="#05b890",
                font=(FONT_FAMILY, 15),
                command=lambda n=name: self._voice_test(n),
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_row,
                text="🗑",
                width=35,
                height=28,
                corner_radius=6,
                fg_color=COLORS["danger"],
                hover_color="#d43d62",
                font=(FONT_FAMILY, 13),
                command=lambda n=name: self._voice_delete(n),
            ).pack(side="left", padx=3)

        # Configure grid weights
        for c in range(cols):
            self.voice_grid_frame.grid_columnconfigure(c, weight=1)

        # Also refresh the TTS dropdown
        self._refresh_tts_voice_dropdown()

    def _refresh_tts_voice_dropdown(self):
        """Update the voice dropdown in the TTS tab."""
        names = self.voices.get_voice_names()
        self.tts_voice_menu.configure(values=names)
        if self.tts_voice_var.get() not in names:
            self.tts_voice_var.set(names[0] if names else "Default (Random)")

    # ==================================================================
    # TAB 4: Settings
    # ==================================================================

    def _build_settings_tab(self):
        tab = self.tab_settings

        main = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color=COLORS["accent"],
        )
        main.pack(fill="both", expand=True, padx=5, pady=5)

        def section_header(parent, text):
            ctk.CTkLabel(
                parent,
                text=text,
                font=(FONT_FAMILY, 15, "bold"),
                text_color=COLORS["accent_light"],
            ).pack(anchor="w", pady=(15, 8), padx=10)

        def setting_row(parent):
            f = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
            f.pack(fill="x", padx=10, pady=3)
            return f

        # --- GPU / Acceleration ---
        section_header(main, "🖥  GPU Acceleration")

        cuda_row = setting_row(main)
        ctk.CTkLabel(
            cuda_row,
            text="NVIDIA CUDA Acceleration",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        has_gpu = has_nvidia_gpu()
        cuda_installed = is_cuda_torch_installed()
        self.cuda_var = ctk.BooleanVar(value=self.settings.use_cuda and cuda_installed)
        self.cuda_switch = ctk.CTkSwitch(
            cuda_row,
            text="",
            variable=self.cuda_var,
            onvalue=True,
            offvalue=False,
            progress_color=COLORS["success"],
            command=self._on_cuda_toggle,
        )
        self.cuda_switch.pack(side="right", padx=15, pady=12)

        self.cuda_status_label = ctk.CTkLabel(
            cuda_row,
            text="",
            font=(FONT_FAMILY, 11),
        )
        self.cuda_status_label.pack(side="right", padx=5, pady=12)

        if not has_gpu:
            self.cuda_switch.configure(state="disabled")
            self.cuda_status_label.configure(
                text="⚠  No NVIDIA GPU detected",
                text_color=COLORS["warning"],
            )
        elif cuda_installed:
            gpu_name = get_nvidia_gpu_name()
            self.cuda_status_label.configure(
                text=f"✅  {gpu_name}",
                text_color=COLORS["success"],
            )
        else:
            gpu_name = get_nvidia_gpu_name()
            self.cuda_status_label.configure(
                text=f"🖥  {gpu_name} — enable to download CUDA support",
                text_color=COLORS["text_secondary"],
            )
            
        # CUDA Notice
        notice_row = setting_row(main)
        ctk.CTkLabel(
            notice_row,
            text="Note:CUDA is the best option — enabling it allows real-time playback with cloning models.",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["warning"],
        ).pack(side="left", padx=15, pady=12)


        # Memory saver
        mem_row = setting_row(main)
        ctk.CTkLabel(
            mem_row,
            text="Memory Saver Mode",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        ctk.CTkLabel(
            mem_row,
            text="Unload inactive model to save RAM",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(0, 10), pady=12)

        self.memsave_var = ctk.BooleanVar(value=self.settings.memory_saver)
        self.memsave_switch = ctk.CTkSwitch(
            mem_row,
            text="",
            variable=self.memsave_var,
            onvalue=True,
            offvalue=False,
            progress_color=COLORS["success"],
            command=self._on_memsave_toggle,
        )
        self.memsave_switch.pack(side="right", padx=15, pady=12)

        _is_kokoro = getattr(self.settings, 'engine', 'fish14') == 'kokoro'

        if not _is_kokoro:
            # --- Fish-Speech Path (hidden in Kokoro mode) ---
            section_header(main, "🐟  Fish-Speech Engine")

            path_row = setting_row(main)

            ctk.CTkLabel(
                path_row,
                text="Model Path",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=15, pady=12)

            self.fish_path_var = ctk.StringVar(
                value=self.settings.fish_speech_path or get_bundled_fish_speech_path()
            )
            self.fish_path_entry = ctk.CTkEntry(
                path_row,
                textvariable=self.fish_path_var,
                width=400,
                fg_color=COLORS["bg_input"],
                border_color=COLORS["border"],
                font=(FONT_FAMILY, 11),
            )
            self.fish_path_entry.pack(side="left", padx=5, pady=12)

            ctk.CTkButton(
                path_row,
                text="📂  Browse",
                width=90,
                height=30,
                corner_radius=6,
                fg_color=COLORS["bg_input"],
                hover_color=COLORS["bg_card_hover"],
                border_color=COLORS["border"],
                border_width=1,
                font=(FONT_FAMILY, 11),
                command=self._browse_fish_path,
            ).pack(side="left", padx=5, pady=12)

            # Validation indicator
            self.fish_status_label = ctk.CTkLabel(
                path_row,
                text="",
                font=(FONT_FAMILY, 11),
            )
            self.fish_status_label.pack(side="right", padx=15, pady=12)
            self._validate_fish_path()
        else:
            # --- Kokoro Engine Info ---
            section_header(main, "🎙  Kokoro Engine")
            kokoro_row = setting_row(main)
            ctk.CTkLabel(
                kokoro_row,
                text="Model",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(
                kokoro_row,
                text="kokoro-v1.0 (int8 quantized)  •  54 preset voices  •  24 kHz",
                font=(FONT_FAMILY, 11),
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=5, pady=12)
            ctk.CTkLabel(
                kokoro_row,
                text="✅  Ready",
                font=(FONT_FAMILY, 11),
                text_color=COLORS["success"],
            ).pack(side="right", padx=15, pady=12)



        # Engine Selection
        engine_row = setting_row(main)
        ctk.CTkLabel(
            engine_row,
            text="Engine Architecture",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        ctk.CTkLabel(
            engine_row,
            text="Core neural logic framework",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(0, 10), pady=12)

        engine_options = [
            "Fish-Speech 1.4 — Smallest (Cloning)",
            "Fish-Speech 1.5 — Best Quality (Cloning)",
            "Kokoro — Fast CPU (Preset Voices)",
        ]

        # Determine current engine from settings.engine field
        _eng = getattr(self.settings, 'engine', 'fish14')
        if _eng == 'kokoro':
            current_engine = engine_options[2]
        elif _eng == 'fish15':
            current_engine = engine_options[1]
        else:
            current_engine = engine_options[0]



        self.engine_var = ctk.StringVar(value=current_engine)
        self.engine_menu = ctk.CTkOptionMenu(
            engine_row,
            variable=self.engine_var,
            values=engine_options,
            width=230,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["bg_input"],
            button_hover_color=COLORS["bg_card_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            font=(FONT_FAMILY, 12),
            command=self._on_engine_select,
        )
        self.engine_menu.pack(side="right", padx=15, pady=12)

        # --- Status ---
        section_header(main, "📊  System Status")

        # RAM readout
        ram_row = setting_row(main)
        ctk.CTkLabel(
            ram_row,
            text="RAM Usage",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        self.ram_label = ctk.CTkLabel(
            ram_row,
            text="Calculating...",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"],
        )
        self.ram_label.pack(side="right", padx=15, pady=12)

        # ffmpeg status
        ffmpeg_row = setting_row(main)
        ctk.CTkLabel(
            ffmpeg_row,
            text="FFmpeg Status",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        ffmpeg_ok = is_ffmpeg_available()
        ffmpeg_text = "✅  Found" if ffmpeg_ok else "❌  Not found — install ffmpeg for MP3 export"
        ffmpeg_color = COLORS["success"] if ffmpeg_ok else COLORS["danger"]
        ctk.CTkLabel(
            ffmpeg_row,
            text=ffmpeg_text,
            font=(FONT_FAMILY, 12),
            text_color=ffmpeg_color,
        ).pack(side="right", padx=15, pady=12)

        # TTS model status
        tts_status_row = setting_row(main)
        ctk.CTkLabel(
            tts_status_row,
            text="TTS Engine",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        self.tts_status_label = ctk.CTkLabel(
            tts_status_row,
            text="⏳  Not loaded",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_muted"],
        )
        self.tts_status_label.pack(side="right", padx=15, pady=12)

        # STT model status
        stt_status_row = setting_row(main)
        ctk.CTkLabel(
            stt_status_row,
            text="STT Engine",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=15, pady=12)

        self.stt_status_label = ctk.CTkLabel(
            stt_status_row,
            text="⏳  Not loaded",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_muted"],
        )
        self.stt_status_label.pack(side="right", padx=15, pady=12)

        # --- Credits ---
        section_header(main, "ℹ  Credits")

        credits_frame = setting_row(main)
        credits_text = (
            "FishTalk uses the following open-source libraries:\n"
            "• Fish-Speech (Apache 2.0) — TTS engine by Fish Audio\n"
            "• faster-whisper (MIT) — STT engine by SYSTRAN\n"
            "• CustomTkinter (MIT) — GUI framework by Tom Schimansky\n"
            "• PyTorch (BSD 3-Clause) — ML backend by Meta\n"
            "• pydub (MIT) — Audio processing\n"
            "• See CREDITS.txt for full license details."
        )
        ctk.CTkLabel(
            credits_frame,
            text=credits_text,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
            justify="left",
        ).pack(padx=15, pady=12, anchor="w")

    # ==================================================================
    # EVENT HANDLERS — TTS Tab
    # ==================================================================

    def _tts_on_drop(self, event):
        """Handle file drop on the TTS drop zone."""
        paths = self._parse_drop_data(event.data)
        for path in paths:
            self._tts_add_file(path)

    def _tts_browse_file(self, event=None):
        """Open file dialog to add a file to the playlist."""
        paths = filedialog.askopenfilenames(
            title="Select text files",
            filetypes=[
                ("Text files", "*.txt *.pdf *.docx *.epub"),
                ("All files", "*.*"),
            ],
        )
        for path in paths:
            self._tts_add_file(path)

    def _tts_add_file(self, path: str):
        """Add a file to the playlist."""
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".txt", ".pdf", ".docx", ".epub"):
            logger.warning("Unsupported file type: %s", ext)
            return

        try:
            text = read_file(path)
            name = os.path.basename(path)
            item = {"name": name, "text": text, "path": path}
            self._playlist_items.append(item)
            self._rebuild_playlist_ui()
            logger.info("Added to playlist: %s (%d chars)", name, len(text))
        except Exception as exc:
            logger.error("Failed to read file: %s", exc)
            messagebox.showerror("Error", f"Could not read file:\n{exc}")

    def _rebuild_playlist_ui(self):
        """Rebuild the playlist list in the scrollable frame."""
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()

        if not self._playlist_items:
            self.playlist_empty_label = ctk.CTkLabel(
                self.playlist_frame,
                text="No files in queue. Drop files above to add them.",
                font=(FONT_FAMILY, 12),
                text_color=COLORS["text_muted"],
            )
            self.playlist_empty_label.pack(pady=30)
            return

        for idx, item in enumerate(self._playlist_items):
            row = ctk.CTkFrame(
                self.playlist_frame,
                fg_color=COLORS["bg_card"] if idx != self._current_playing else COLORS["accent"],
                corner_radius=6,
                height=40,
            )
            row.pack(fill="x", pady=2, padx=4)
            row.pack_propagate(False)

            # Index
            idx_color = COLORS["text_primary"] if idx != self._current_playing else "#ffffff"
            ctk.CTkLabel(
                row,
                text=f"{idx + 1}.",
                font=(FONT_FAMILY, 12),
                text_color=idx_color,
                width=30,
            ).pack(side="left", padx=(10, 5))

            # File name
            ctk.CTkLabel(
                row,
                text=item["name"],
                font=(FONT_FAMILY, 12),
                text_color=idx_color,
            ).pack(side="left", padx=5)

            # Character count
            ctk.CTkLabel(
                row,
                text=f"({len(item['text']):,} chars)",
                font=(FONT_FAMILY, 10),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=5)

            # Remove button
            ctk.CTkButton(
                row,
                text="✕",
                width=28,
                height=24,
                corner_radius=4,
                fg_color=COLORS["danger"],
                hover_color="#d43d62",
                font=(FONT_FAMILY, 11),
                command=lambda i=idx: self._tts_remove_item(i),
            ).pack(side="right", padx=8)

    def _tts_remove_item(self, index: int):
        if 0 <= index < len(self._playlist_items):
            self._playlist_items.pop(index)
            self._rebuild_playlist_ui()

    def _tts_clear_playlist(self):
        self._playlist_items.clear()
        self._current_playing = -1
        self._rebuild_playlist_ui()

    def _on_speed_change(self, value):
        self.speed_label.configure(text=f"Speed: {value:.1f}x")
        self.settings.speed = round(value, 1)

    def _on_volume_change(self, value):
        self.vol_label.configure(text=f"Volume: {int(value)}%")
        self.settings.volume = int(value)

    def _on_cadence_change(self, value):
        self.cad_label.configure(text=f"Cadence: {int(value)}%")
        self.settings.cadence = int(value)

    def _ensure_tts_loaded(self, on_success):
        """Helper to lazy load TTS with a beautiful popup overlay."""
        if self.tts.is_loaded:
            on_success()
            return
            
        # Create themed popup
        popup = ctk.CTkToplevel(self.root)
        popup.title("Starting AI Engine")
        popup.geometry("350x140")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(fg_color=COLORS["bg_card"])
        
        # Center popup over the main window
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 70
        popup.geometry(f"+{x}+{y}")
        
        engine_name = "Kokoro" if getattr(self.settings, 'engine', 'fish14') == 'kokoro' else "Fish-Speech"
        lbl_msg = ctk.CTkLabel(popup, text=f"Booting {engine_name} Engine...", font=(FONT_FAMILY, 14, "bold"), text_color=COLORS["text_primary"])
        lbl_msg.pack(pady=(20, 10))
        
        pb = ctk.CTkProgressBar(popup, progress_color=COLORS["accent"], fg_color=COLORS["bg_input"], width=280, height=8, corner_radius=4)
        pb.pack(pady=5)
        pb.set(0)
        
        status = ctk.CTkLabel(popup, text="Initializing...", font=(FONT_FAMILY, 11), text_color=COLORS["text_muted"])
        status.pack(pady=5)

        def on_progress(text: str, frac: float):
            self.root.after(0, lambda: status.configure(text=text))
            self.root.after(0, lambda: pb.set(frac))

        def on_ready():
            def _ready_ui():
                popup.grab_release()
                popup.destroy()
                self.update_tts_status("✅  Engine ready", COLORS["success"])
                try:
                    self.tts_progress.set(0)
                    for btn in (self.btn_play, self.btn_pause, self.btn_save_mp3):
                        btn.configure(state="normal")
                except AttributeError:
                    pass
                on_success()
            self.root.after(0, _ready_ui)

        def on_error(exc):
            def _err_ui():
                popup.grab_release()
                popup.destroy()
                messagebox.showerror("Error", f"Failed to load engine:\n{exc}")
                self.update_tts_status("❌  Load failed", COLORS["danger"])
            self.root.after(0, _err_ui)

        self.tts.load_model(on_progress=on_progress, on_ready=on_ready, on_error=on_error)

    def _tts_play(self):
        """Start TTS playback from the playlist."""
        if not self._playlist_items:
            messagebox.showinfo("FishTalk", "Add files to the playlist first.")
            return

        if not self.tts.is_loaded:
            for btn in (self.btn_play, self.btn_pause, self.btn_save_mp3):
                btn.configure(state="disabled")
            self._ensure_tts_loaded(self._tts_play)
            return

        if self._is_paused:
            self._is_paused = False
            self._resume_audio()
            return

        self._is_playing = True
        self._current_playing = 0
        self._rebuild_playlist_ui()
        self._play_current_item()

    def _play_current_item(self):
        """Generate and play the current playlist item."""
        if self._current_playing < 0 or self._current_playing >= len(self._playlist_items):
            self._is_playing = False
            self._current_playing = -1
            self._rebuild_playlist_ui()
            self.tts_status.configure(text="Playlist complete")
            return

        item = self._playlist_items[self._current_playing]
        self.tts_status.configure(text=f"Generating: {item['name']}...")
        self._rebuild_playlist_ui()

        # Get voice profile
        voice_name = self.tts_voice_var.get()
        profile = None
        if voice_name != "Default (Random)":
            profile = self.voices.get_voice(voice_name)

        speed = self.speed_slider.get()

        def on_progress(status, frac):
            self.root.after(0, lambda: self.tts_progress.set(frac))
            self.root.after(0, lambda: self.tts_status.configure(text=status))

        # --- Streaming chunk playback via continuous OutputStream ---
        # Volume is read live from the slider inside the audio callback
        # so moving the slider mid-playback takes effect immediately.
        import queue as _queue
        import numpy as _np
        import sounddevice as _sd

        _sample_queue = _queue.Queue()
        _SENTINEL = object()
        _stream = [None]

        def _stream_callback(outdata, frames, time_info, status):
            vol = self.vol_slider.get() / 100.0
            remaining = frames
            offset = 0
            outdata[:] = 0  # default silence
            while remaining > 0:
                if _stream_callback._buf is None or len(_stream_callback._buf) == 0:
                    try:
                        item = _sample_queue.get_nowait()
                        if item is _SENTINEL:
                            return
                        _stream_callback._buf = item
                    except _queue.Empty:
                        return  # underrun — silence already written
                take = min(remaining, len(_stream_callback._buf))
                out_slice = (_stream_callback._buf[:take] * vol).astype(_np.float32)
                outdata[offset:offset+take, 0] = out_slice
                if outdata.shape[1] > 1:
                    outdata[offset:offset+take, 1] = out_slice
                _stream_callback._buf = _stream_callback._buf[take:]
                offset += take
                remaining -= take
        _stream_callback._buf = None


        def on_chunk(chunk_np, sr):
            """Push decoded samples into the playback stream (skipped in silent mode)."""
            if self.silent_mode_var.get():
                return  # Work Silent: generate only, no output
            if _stream[0] is None:
                s = _sd.OutputStream(
                    samplerate=sr, channels=1, dtype='float32',
                    blocksize=2048, callback=_stream_callback,
                )
                s.start()
                _stream[0] = s
            _sample_queue.put(chunk_np.astype(_np.float32))

        def on_complete(wav_path):
            _sample_queue.put(_SENTINEL)
            def _finish():
                import time as _t; _t.sleep(1.0)
                if _stream[0]:
                    _stream[0].stop(); _stream[0].close()
                self.root.after(0, lambda: self.tts_status.configure(
                    text=f"✅ Done: {self._playlist_items[self._current_playing]['name']}"
                ))
                self.root.after(0, lambda: self.tts_progress.set(1.0))
                self._current_playing += 1
                self.root.after(500, self._play_current_item)
            threading.Thread(target=_finish, daemon=True).start()

        def on_error(exc):
            _sample_queue.put(_SENTINEL)
            if _stream[0]:
                try: _stream[0].stop(); _stream[0].close()
                except Exception: pass
            self.root.after(0, lambda: self.tts_status.configure(text=f"Error: {exc}"))

        # Route to correct engine based on settings
        _is_kokoro_mode = getattr(self.settings, 'engine', 'fish14') == 'kokoro'

        if _is_kokoro_mode:
            voice_id = KOKORO_VOICES.get(voice_name, DEFAULT_VOICE)
            self.tts.generate(
                text=item["text"],
                voice_id=voice_id,
                speed=speed,
                on_progress=on_progress,
                on_chunk=on_chunk,
                on_complete=on_complete,
                on_error=on_error,
            )
        else:
            self.tts.generate(
                text=item["text"],
                reference_wav=profile["wav_path"] if profile else None,
                reference_tokens=None,
                prompt_text=profile["prompt_text"] if profile else None,
                speed=speed,
                on_progress=on_progress,
                on_chunk=on_chunk,
                on_complete=on_complete,
                on_error=on_error,
            )

    def _play_audio(self, wav_path: str):
        """Play generated audio through speakers and auto-advance."""
        try:
            import soundfile as sf_lib
            import sounddevice as sd

            data, sr = sf_lib.read(wav_path)

            # Apply volume
            vol = self.vol_slider.get() / 100.0
            data = data * vol

            self._audio_data = data
            self._audio_sr = sr
            self.tts_status.configure(text=f"Playing: {self._playlist_items[self._current_playing]['name']}")

            # Stop any existing playback
            sd.stop()

            def _play_thread():
                import time as t
                try:
                    sd.play(data, sr)
                    # Poll in small slices so pause/stop can interrupt
                    duration = len(data) / sr if sr else 1
                    start = t.time()
                    while sd.get_stream() is not None and sd.get_stream().active:
                        if not self._is_playing or self._is_paused:
                            sd.stop()
                            return
                        elapsed = t.time() - start
                        progress = min(elapsed / duration, 1.0) if duration > 0 else 1.0
                        self.root.after(0, lambda p=progress: self.tts_progress.set(p))
                        t.sleep(0.05)
                    # Natural end — advance to next item
                    if self._is_playing and not self._is_paused:
                        self._current_playing += 1
                        self.root.after(300, self._play_current_item)
                except Exception as exc:
                    logger.error("Playback thread error: %s", exc)

            threading.Thread(target=_play_thread, daemon=True).start()

        except Exception as exc:
            logger.error("Audio playback error: %s", exc)
            self.tts_status.configure(text=f"Playback error: {exc}")

    def _resume_audio(self):
        """Resume paused audio playback."""
        try:
            import sounddevice as sd
            # sounddevice doesn't support true pause/resume easily,
            # so this is a simplified implementation
            self.tts_status.configure(text="Resumed")
        except Exception:
            pass

    def _tts_pause(self):
        """Pause playback."""
        self._is_paused = True
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass
        self.tts_status.configure(text="Paused")

    def _tts_stop(self):
        """Stop playback and cancel any pending generation."""
        self._is_playing = False
        self._is_paused = False
        self._current_playing = -1
        self.tts.cancel()
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass
        self.tts_progress.set(0)
        self.tts_status.configure(text="Stopped")
        self._rebuild_playlist_ui()

    def _tts_save_mp3(self):
        """Export the last generated audio to MP3."""
        if not is_ffmpeg_available():
            messagebox.showwarning(
                "FishTalk",
                "ffmpeg is not installed.\nPlease install ffmpeg or place ffmpeg.exe in the bin/ folder."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save as MP3",
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")],
            initialdir=os.path.expanduser("~/Documents"),
        )
        if not path:
            return

        # Find the most recent temp wav
        import glob
        import tempfile
        wavs = sorted(
            glob.glob(os.path.join(tempfile.gettempdir(), "fishtalk_tts_*.wav")),
            key=os.path.getmtime,
            reverse=True,
        )
        if wavs:
            try:
                export_mp3(wavs[0], path)
                messagebox.showinfo("FishTalk", f"Saved to:\n{path}")
            except Exception as exc:
                messagebox.showerror("Error", f"Export failed:\n{exc}")
        else:
            messagebox.showinfo("FishTalk", "No audio to export. Generate speech first.")

    # ==================================================================
    # EVENT HANDLERS — STT Tab
    # ==================================================================

    def _stt_on_drop(self, event):
        """Handle file drop on the STT drop zone."""
        paths = self._parse_drop_data(event.data)
        if paths:
            self._stt_set_file(paths[0])

    def _stt_browse_file(self, event=None):
        """Open file dialog to select an audio file."""
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._stt_set_file(path)

    def _stt_set_file(self, path: str):
        """Set the audio file for transcription."""
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".wav", ".mp3", ".m4a", ".flac", ".ogg"):
            messagebox.showwarning("FishTalk", f"Unsupported audio format: {ext}")
            return
        self._stt_audio_path = path
        name = os.path.basename(path)
        self.stt_file_label.configure(text=f"📎  {name}", text_color=COLORS["success"])
        self.stt_drop_label.configure(text=f"✅  {name}")

    def _stt_transcribe(self):
        """Start transcription."""
        if not self._stt_audio_path:
            messagebox.showinfo("FishTalk", "Drop or select an audio file first.")
            return

        if not self.stt.is_loaded:
            # Load model first
            device = "cuda" if self.cuda_var.get() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            model_size = self.stt_model_var.get()

            self.stt_textbox.configure(state="normal")
            self.stt_textbox.delete("1.0", "end")
            self.stt_textbox.insert("1.0", "Loading Whisper model...\n")
            self.stt_textbox.configure(state="disabled")

            def on_ready():
                self.root.after(0, self._stt_run_transcription)
                self.root.after(
                    0,
                    lambda: self.stt_status_label.configure(
                        text="✅  Loaded",
                        text_color=COLORS["success"],
                    )
                )

            def on_error(exc):
                self.root.after(
                    0,
                    lambda: self._stt_append_text(f"\nError loading model: {exc}")
                )

            self.stt.load_model(
                model_size=model_size,
                device=device,
                compute_type=compute_type,
                on_ready=on_ready,
                on_error=on_error,
            )
        else:
            self._stt_run_transcription()

    def _stt_run_transcription(self):
        """Run the actual transcription."""
        self.stt_textbox.configure(state="normal")
        self.stt_textbox.delete("1.0", "end")
        self.stt_textbox.configure(state="disabled")
        self.stt_progress.set(0)

        def on_segment(text, start, end):
            timestamp = f"[{start:.1f}s → {end:.1f}s]"
            self.root.after(
                0,
                lambda: self._stt_append_text(f"{timestamp}  {text}\n")
            )

        def on_progress(frac):
            self.root.after(0, lambda: self.stt_progress.set(frac))

        def on_complete(full_text, info):
            self.root.after(0, lambda: self.stt_progress.set(1.0))
            lang = info.get("language", "unknown")
            prob = info.get("language_probability", 0.0) * 100
            self.root.after(
                0,
                lambda: self._stt_append_text(
                    f"\n--- Done! Language: {lang} ({prob:.0f}% confidence) ---"
                )
            )

        def on_error(exc):
            self.root.after(
                0,
                lambda: self._stt_append_text(f"\n⚠ Error: {exc}")
            )

        self.stt.transcribe(
            audio_path=self._stt_audio_path,
            on_segment=on_segment,
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error,
        )

    def _stt_append_text(self, text: str):
        """Append text to the STT textbox (thread-safe via root.after)."""
        self.stt_textbox.configure(state="normal")
        self.stt_textbox.insert("end", text)
        self.stt_textbox.see("end")
        self.stt_textbox.configure(state="disabled")

    def _stt_cancel(self):
        """Cancel ongoing transcription."""
        self.stt.cancel()
        self._stt_append_text("\n--- Cancelled ---")

    def _stt_export(self, fmt: str):
        """Export transcription to a file."""
        self.stt_textbox.configure(state="normal")
        text = self.stt_textbox.get("1.0", "end").strip()
        self.stt_textbox.configure(state="disabled")

        if not text or text == "Transcription will appear here in real time...":
            messagebox.showinfo("FishTalk", "No transcription to export.")
            return

        exts = {"txt": ".txt", "docx": ".docx", "pdf": ".pdf"}
        ftypes = {
            "txt": [("Text files", "*.txt")],
            "docx": [("Word documents", "*.docx")],
            "pdf": [("PDF files", "*.pdf")],
        }

        path = filedialog.asksaveasfilename(
            title=f"Save as {fmt.upper()}",
            defaultextension=exts[fmt],
            filetypes=ftypes[fmt],
        )
        if not path:
            return

        try:
            {"txt": export_txt, "docx": export_docx, "pdf": export_pdf}[fmt](text, path)
            messagebox.showinfo("FishTalk", f"Saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Export failed:\n{exc}")

    def _on_stt_model_change(self, value):
        """Handle Whisper model size change."""
        self.settings.whisper_model_size = value
        # Force model reload on next transcription
        if self.stt.is_loaded:
            self.stt.unload_model()
            self.stt_status_label.configure(
                text="⏳  Model changed — will reload on next use",
                text_color=COLORS["warning"],
            )

    # ==================================================================
    # EVENT HANDLERS — Voice Lab
    # ==================================================================

    def _voice_clone(self):
        """Open dialog to clone a new voice."""
        path = filedialog.askopenfilename(
            title="Select reference audio (15–30 sec WAV)",
            filetypes=[
                ("WAV files", "*.wav"),
                ("All audio", "*.wav *.mp3 *.flac"),
            ],
        )
        if not path:
            return

        # Ask for voice name
        dialog = ctk.CTkInputDialog(
            text="Enter a name for this voice profile:",
            title="Clone Voice",
        )
        name = dialog.get_input()
        if not name or not name.strip():
            return

        name = name.strip()
        if self.voices.voice_exists(name):
            messagebox.showwarning("FishTalk", f"Voice '{name}' already exists.")
            return

        try:
            tts = self.tts if self.tts.is_loaded else None
            self.voices.clone_voice(
                name=name,
                reference_wav_path=path,
                tts_engine=tts,
                prompt_text="",
            )
            self._refresh_voice_grid()
            messagebox.showinfo("FishTalk", f"Voice '{name}' created successfully!")
        except Exception as exc:
            messagebox.showerror("Error", f"Voice cloning failed:\n{exc}")

    def _voice_delete(self, name: str):
        """Delete a voice profile."""
        confirm = messagebox.askyesno(
            "Delete Voice",
            f"Are you sure you want to delete '{name}'?"
        )
        if confirm:
            self.voices.delete_voice(name)
            self._refresh_voice_grid()

    def _voice_test(self, name: str):
        """Generate and play a sample of the selected voice."""
        if not self.tts.is_loaded:
            self._ensure_tts_loaded(lambda: self._voice_test(name))
            return
            
        profile = self.voices.get_voice(name)
        if not profile:
            return
            
        test_text = "Hello, how do I sound?"
        
        # We need a small loading indicator. We can use the status bar of TTS tab or similar
        self.update_tts_status(f"⏳ Testing {name}...", COLORS["warning"])
        
        def on_complete(wav_path):
            self.root.after(0, lambda: self.update_tts_status("✅ Engine ready (test complete)", COLORS["success"]))
            def _play():
                try:
                    import soundfile as sf_lib
                    import sounddevice as sd
                    data, sr = sf_lib.read(wav_path)
                    sd.stop()
                    sd.play(data, sr)
                    sd.wait()
                except Exception as e:
                    logger.error("Voice test playback error: %s", e)
            threading.Thread(target=_play, daemon=True).start()
                
        def on_error(exc):
            self.root.after(0, lambda: self.update_tts_status("✅ Engine ready", COLORS["success"]))
            self.root.after(0, lambda: messagebox.showerror("Test Failed", f"Could not generate sample:\n{exc}"))

        ref_wav = profile.get("wav_path")
        tokens_path = profile.get("tokens_path")
        ref_tokens = np.load(tokens_path) if tokens_path and os.path.isfile(tokens_path) else None
        
        self.tts.generate(
            text=test_text,
            reference_wav=ref_wav,
            reference_tokens=ref_tokens,
            prompt_text=profile.get("prompt_text", ""),
            on_complete=on_complete,
            on_error=on_error
        )

    # ==================================================================
    # EVENT HANDLERS — Settings
    # ==================================================================

    def _on_cuda_toggle(self):
        """Handle CUDA toggle — download CUDA PyTorch on demand."""
        wants_cuda = self.cuda_var.get()

        if wants_cuda and not is_cuda_torch_installed():
            # User is enabling CUDA but doesn't have CUDA PyTorch yet
            if not has_nvidia_gpu():
                messagebox.showwarning(
                    "FishTalk",
                    "No NVIDIA GPU detected.\nCUDA acceleration is not available on this system."
                )
                self.cuda_var.set(False)
                return

            gpu_name = get_nvidia_gpu_name()
            confirm = messagebox.askyesno(
                "Download CUDA Support",
                f"GPU detected: {gpu_name}\n\n"
                "To enable GPU acceleration, FishTalk needs to download\n"
                "the CUDA version of PyTorch (~2.5 GB).\n\n"
                "This is a one-time download. The app will continue\n"
                "working while it downloads in the background.\n\n"
                "Download now?"
            )

            if not confirm:
                self.cuda_var.set(False)
                return

            # Start download
            self.cuda_switch.configure(state="disabled")
            self.cuda_status_label.configure(
                text="⏳  Downloading CUDA PyTorch...",
                text_color=COLORS["warning"],
            )

            def on_progress(status):
                self.root.after(0, lambda: self.cuda_status_label.configure(
                    text=f"⏳  {status}",
                    text_color=COLORS["warning"],
                ))

            def on_complete(success, message):
                def _update():
                    self.cuda_switch.configure(state="normal")
                    if success:
                        self.cuda_status_label.configure(
                            text=f"✅  {gpu_name} — CUDA ready",
                            text_color=COLORS["success"],
                        )
                        self.settings.use_cuda = True
                        self.settings.save()
                        messagebox.showinfo(
                            "CUDA Ready",
                            f"{message}\n\nRestart FishTalk to use GPU acceleration."
                        )
                    else:
                        self.cuda_var.set(False)
                        self.cuda_status_label.configure(
                            text="❌  CUDA download failed",
                            text_color=COLORS["danger"],
                        )
                        messagebox.showerror("CUDA Setup Failed", message)
                self.root.after(0, _update)

            install_cuda_pytorch(on_progress=on_progress, on_complete=on_complete)

        elif not wants_cuda and is_cuda_torch_installed():
            # User is disabling CUDA — offer to revert to save space
            revert = messagebox.askyesno(
                "Revert to CPU",
                "Would you like to remove CUDA PyTorch and switch back\n"
                "to CPU-only mode? This frees ~2 GB of disk space.\n\n"
                "(Choose 'No' to keep CUDA installed but disabled)"
            )

            self.settings.use_cuda = False
            self.settings.save()

            if revert:
                self.cuda_switch.configure(state="disabled")
                self.cuda_status_label.configure(
                    text="⏳  Reverting to CPU...",
                    text_color=COLORS["warning"],
                )

                def on_revert_complete(success, message):
                    def _update():
                        self.cuda_switch.configure(state="normal")
                        self.cuda_status_label.configure(
                            text="✅  Reverted to CPU mode",
                            text_color=COLORS["success"],
                        )
                        messagebox.showinfo("Done", message)
                    self.root.after(0, _update)

                revert_to_cpu_pytorch(on_complete=on_revert_complete)
            else:
                self.cuda_status_label.configure(
                    text="💤  CUDA installed but disabled",
                    text_color=COLORS["text_muted"],
                )
        else:
            # Simple toggle (CUDA already installed, or already CPU)
            self.settings.use_cuda = wants_cuda
            self.settings.save()

    def _on_memsave_toggle(self):
        self.settings.memory_saver = self.memsave_var.get()
        self.settings.save()

    def _on_silent_toggle(self):
        self.settings.silent_mode = self.silent_mode_var.get()
        self.settings.save()
        state = "enabled — audio will be generated but not played" if self.settings.silent_mode else "disabled"
        self.tts_status.configure(text=f"🔇 Work Silent {state}")

    def _lock_voice_lab(self):
        """Disable the Voice Lab tab when Kokoro engine is active."""
        try:
            # Destroy all existing children so voice cards don't show through
            for widget in self.tab_voices.winfo_children():
                widget.destroy()
            # Show centred notice
            notice_frame = ctk.CTkFrame(self.tab_voices, fg_color="transparent")
            notice_frame.pack(expand=True, fill="both")
            ctk.CTkLabel(
                notice_frame,
                text="🔒",
                font=(FONT_FAMILY, 48),
                text_color=COLORS["text_muted"],
            ).pack(expand=True, pady=(80, 8))
            ctk.CTkLabel(
                notice_frame,
                text="Voice Lab is not available in Kokoro mode.\n\n"
                     "Kokoro uses 54 built-in preset voices — no cloning needed.\n"
                     "Switch to Fish-Speech 1.4 or 1.5 in Settings to clone voices.",
                font=(FONT_FAMILY, 14),
                text_color=COLORS["text_muted"],
                justify="center",
            ).pack(pady=(0, 80))
        except Exception as exc:
            logger.warning("Could not lock Voice Lab: %s", exc)


    def _on_kokoro_voice_change(self, display_name: str):
        """Save the selected Kokoro voice to settings."""
        voice_id = KOKORO_VOICES.get(display_name, DEFAULT_VOICE)
        self.settings.kokoro_voice = voice_id
        self.settings.save()

    def _on_engine_select(self, new_val: str):
        """Update the active AI engine and prompt restart."""
        app_dir = os.path.dirname(os.path.abspath(__file__))

        # Helper: display name for current saved engine
        def _current_label():
            _eng = getattr(self.settings, 'engine', 'fish14')
            if _eng == 'kokoro':
                return "Kokoro — Fast CPU (Preset Voices)"
            if _eng == 'fish15':
                return "Fish-Speech 1.5 — Best Quality (Cloning)"
            return "Fish-Speech 1.4 — Smallest (Cloning)"

        if "Kokoro" in new_val:
            self.settings.engine = 'kokoro'
        elif "1.5" in new_val:
            self.settings.fish_speech_path = os.path.join(app_dir, "fish-speech-1.5")
            self.settings.checkpoint_name = "checkpoints/fish-speech-1.5"
            self.settings.engine = 'fish15'
        else:
            self.settings.fish_speech_path = os.path.join(app_dir, "fish-speech")
            self.settings.checkpoint_name = "checkpoints/fish-speech-1.4"
            self.settings.engine = 'fish14'

        self.settings.save()

        confirm = messagebox.askyesno(
            "Engine Restart Required",
            f"Switched to: {new_val}\n\n"
            "FishTalk needs to restart to load the new engine.\n\n"
            "Restart now?",
        )

        if confirm:
            import sys
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Revert dropdown visually (settings already saved — will take effect on next restart)
            self.engine_var.set(_current_label())


    def _browse_fish_path(self):
        path = filedialog.askdirectory(title="Select Fish-Speech directory")
        if path:
            self.fish_path_var.set(path)
            self.settings.fish_speech_path = path
            self._validate_fish_path()
            self.settings.save()

    def _validate_fish_path(self):
        path = self.fish_path_var.get()
        result = validate_fish_speech_path(path)
        if result["valid"]:
            self.fish_status_label.configure(
                text="✅  Valid",
                text_color=COLORS["success"],
            )
        else:
            self.fish_status_label.configure(
                text=f"❌  {result['message']}",
                text_color=COLORS["danger"],
            )

    def _on_tab_changed(self):
        """Handle tab switching for Memory Saver mode."""
        if not self.settings.memory_saver:
            return

        current = self.tabview.get()

        if "Read Aloud" in current:
            # On TTS tab — unload STT, load TTS
            if self.stt.is_loaded:
                self.stt.unload_model()
                self.stt_status_label.configure(
                    text="💤  Unloaded (Memory Saver)",
                    text_color=COLORS["text_muted"],
                )
        elif "Transcribe" in current:
            # On STT tab — unload TTS, keep STT
            if self.tts.is_loaded:
                self.tts.unload_model()
                self.tts_status_label.configure(
                    text="💤  Unloaded (Memory Saver)",
                    text_color=COLORS["text_muted"],
                )

    # ==================================================================
    # RAM monitoring
    # ==================================================================

    def _start_ram_monitor(self):
        """Start periodic RAM usage updates."""
        self._update_ram()

    def _update_ram(self):
        """Update RAM readout label."""
        try:
            ram = get_ram_usage()
            text = (
                f"App: {ram['process_mb']:.0f} MB  |  "
                f"System: {ram['system_used_gb']:.1f} / "
                f"{ram['system_total_gb']:.1f} GB ({ram['system_percent']:.0f}%)"
            )
            self.ram_label.configure(text=text)
        except Exception:
            self.ram_label.configure(text="Unable to read")

        # Schedule next update
        self.root.after(5000, self._update_ram)

    # ==================================================================
    # Helpers
    # ==================================================================

    def _parse_drop_data(self, data: str) -> list:
        """Parse tkinterdnd2 drop event data into file paths."""
        # Windows wraps paths with spaces in {}
        paths = []
        if "{" in data:
            import re
            paths = re.findall(r"\{([^}]+)\}", data)
            remaining = re.sub(r"\{[^}]+\}", "", data).strip()
            if remaining:
                paths.extend(remaining.split())
        else:
            paths = data.strip().split()
        return [p for p in paths if os.path.isfile(p)]

    def update_tts_status(self, text: str, color: str = None):
        """Update TTS engine status label in Settings tab."""
        self.tts_status_label.configure(
            text=text,
            text_color=color or COLORS["text_secondary"],
        )

    def update_stt_status(self, text: str, color: str = None):
        """Update STT engine status label in Settings tab."""
        self.stt_status_label.configure(
            text=text,
            text_color=color or COLORS["text_secondary"],
        )
