"""
Aries — Phase 4: Voice Subsystems integrated.

What this phase adds:
  - Enabled 🎤 SPEAK button for Speech-to-Text (STT) microphone input
  - Background audio worker threads that feed transcribed speech into the intent/chat loop
  - Automated Text-to-Speech (TTS) output reading Aries' responses aloud
"""

from __future__ import annotations

import threading
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from core import database
from core.ai_client import generate_reply
from core.config import APP_NAME
from core.intents import Intent
from core.messaging import execute_adb_command
from core.router import classify_intent
from core.tool_handlers import TOOL_HANDLERS
from core.voice import listen_to_microphone, speak_text  # Phase 4 Voice Imports

# --- Color palette: slate / neon accent ---
COLOR_BG = "#0d1117"
COLOR_PANEL = "#111827"
COLOR_ACCENT = "#00e5ff"
COLOR_TEXT = "#c9d1d9"
COLOR_MUTED = "#6b7280"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class AriesApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(f"{APP_NAME} — Personal AI Assistant")
        self.geometry("1100x680")
        self.configure(fg_color=COLOR_BG)

        database.init_db()

        self._build_layout()
        self._restore_history()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_central_panel()

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=220, fg_color=COLOR_PANEL, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="TELEMETRY", font=("Consolas", 14, "bold"), text_color=COLOR_ACCENT
        ).pack(pady=(20, 10), padx=16, anchor="w")

        # Stub rows — wired to real data in Phase 7.
        for label in ["SYSTEM: nominal", "LOCATION: —", "WEATHER: —", "AUDIO: idle", "BLUETOOTH: —", "SECURITY: —"]:
            ctk.CTkLabel(
                sidebar, text=label, font=("Consolas", 11), text_color=COLOR_MUTED, anchor="w"
            ).pack(fill="x", padx=16, pady=4)

    def _build_central_panel(self) -> None:
        central = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        central.grid(row=0, column=1, sticky="nswe")
        central.grid_rowconfigure(1, weight=1)
        central.grid_columnconfigure(0, weight=1)

        # Reactor core header stub
        header = ctk.CTkFrame(central, height=70, fg_color=COLOR_PANEL)
        header.grid(row=0, column=0, sticky="we", padx=12, pady=(12, 6))
        ctk.CTkLabel(
            header, text=f"◉ {APP_NAME}", font=("Consolas", 20, "bold"), text_color=COLOR_ACCENT
        ).pack(pady=16)

        # Terminal / chat log
        self.log = ctk.CTkTextbox(
            central,
            font=("Consolas", 13),
            fg_color="#000000",
            text_color=COLOR_TEXT,
            wrap="word",
        )
        self.log.grid(row=1, column=0, sticky="nswe", padx=12, pady=6)
        self.log.configure(state="disabled")

        # Input control bar
        controls = ctk.CTkFrame(central, fg_color=COLOR_BG)
        controls.grid(row=2, column=0, sticky="we", padx=12, pady=(6, 12))
        controls.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(controls, placeholder_text="Enter a command...", font=("Consolas", 13))
        self.entry.grid(row=0, column=0, sticky="we", padx=(0, 8))
        self.entry.bind("<Return>", lambda _event: self._on_transmit())

        ctk.CTkButton(
            controls, text="🎤 SPEAK", width=100, state="normal",  # Enabled for Phase 4 Voice Subsystems
            fg_color=COLOR_PANEL, hover_color="#1f2937",
            command=self._on_speak,
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            controls, text="TRANSMIT", width=100, fg_color=COLOR_ACCENT, text_color="#000000",
            hover_color="#33ecff", command=self._on_transmit,
        ).grid(row=0, column=2, padx=4)

        ctk.CTkButton(
            controls, text="EXPORT", width=90, fg_color=COLOR_PANEL, hover_color="#1f2937",
            command=self._on_export,
        ).grid(row=0, column=3, padx=4)

        ctk.CTkButton(
            controls, text="CLEAR", width=90, fg_color="#3b0d0d", hover_color="#5c1414",
            command=self._on_clear,
        ).grid(row=0, column=4, padx=4)

    # ------------------------------------------------------------------
    # Chat log helpers
    # ------------------------------------------------------------------
    def _append_log(self, speaker: str, content: str) -> None:
        self.log.configure(state="normal")
        prefix = "YOU" if speaker == "user" else APP_NAME
        self.log.insert("end", f"{prefix}> {content}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _restore_history(self) -> None:
        for msg in database.load_history():
            self._append_log(msg.speaker, msg.content)

    # ------------------------------------------------------------------
    # Voice Subsystems (Phase 4 STT)
    # ------------------------------------------------------------------
    def _on_speak(self) -> None:
        """Triggered when the user clicks the 🎤 SPEAK button."""
        self._append_log("aries", "…listening…")
        threading.Thread(target=self._listen_background, daemon=True).start()

    def _listen_background(self) -> None:
        """Background thread worker to capture microphone input (Speech-to-Text)."""
        spoken_text = listen_to_microphone()
        self.after(0, self._handle_spoken_input, spoken_text)

    def _handle_spoken_input(self, text: str) -> None:
        """Clean up listening placeholder and process transcribed speech."""
        self.log.configure(state="normal")
        content = self.log.get("1.0", "end").rstrip("\n")
        if content.endswith(f"{APP_NAME}> …listening…"):
            content = content[: -len(f"{APP_NAME}> …listening…")].rstrip("\n")
        self.log.delete("1.0", "end")
        self.log.insert("1.0", content + ("\n\n" if content else ""))
        self.log.configure(state="disabled")

        if not text or text.startswith("[Error"):
            if text:
                self._append_log("aries", text)
            return

        # Treat spoken text precisely like typed text input
        database.add_message("user", text)
        self._append_log("user", text)
        self._append_log("aries", "…thinking…")

        threading.Thread(target=self._call_ai, args=(text,), daemon=True).start()

    # ------------------------------------------------------------------
    # TRANSMIT — background thread, safely back to UI via self.after()
    # ------------------------------------------------------------------
    def _on_transmit(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")

        database.add_message("user", text)
        self._append_log("user", text)
        self._append_log("aries", "…thinking…")

        threading.Thread(target=self._call_ai, args=(text,), daemon=True).start()

    def _call_ai(self, prompt: str) -> None:
        try:
            prompt_lower = prompt.lower()
            
            # Bypass cloud classification entirely for core hardware commands
            if "battery" in prompt_lower:
                result = execute_adb_command(['shell', 'dumpsys', 'battery'])
                reply = f"[Hardware Telemetry Success]:\n{result}"
            elif "whatsapp" in prompt_lower:
                execute_adb_command(['shell', 'am', 'start', '-n', 'com.whatsapp/.HomeActivity'])
                reply = "[Action Executed]: WhatsApp launched."
            elif "youtube" in prompt_lower:
                execute_adb_command(['shell', 'monkey', '-p', 'com.google.android.youtube', '-c', 'android.intent.category.LAUNCHER', '1'])
                reply = "[Action Executed]: YouTube launched."
            else:
                classified = classify_intent(prompt)
                if classified.intent is Intent.GENERAL_CHAT:
                    try:
                        reply = generate_reply(prompt)
                    except Exception as api_err:
                        err_str = str(api_err)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                            reply = "API quota limit reached. Please use local hardware commands (battery, open whatsapp, call, text)."
                        else:
                            reply = f"[AI Error]: {api_err}"
                else:
                    handler = TOOL_HANDLERS[classified.intent]
                    stub_output = handler(classified.parameters)
                    reply = f"(intent: {classified.intent.value}) {stub_output}"
                    
        except Exception as exc:  
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                reply = "API quota limit reached. Please use local hardware commands (battery, open whatsapp, call, text)."
            else:
                reply = f"[System Error]: {exc}"
                
        self.after(0, self._on_ai_reply, reply)

    def _on_ai_reply(self, reply: str) -> None:
        # Remove the "…thinking…" placeholder line, then append the real reply.
        self.log.configure(state="normal")
        content = self.log.get("1.0", "end")
        trimmed = content.rstrip("\n")
        if trimmed.endswith("…thinking…"):
            trimmed = trimmed[: -len(f"{APP_NAME}> …thinking…")].rstrip("\n")
        self.log.delete("1.0", "end")
        self.log.insert("1.0", trimmed + ("\n\n" if trimmed else ""))
        self.log.configure(state="disabled")

        database.add_message("aries", reply)
        self._append_log("aries", reply)

        # Speak Aries' response aloud using Text-to-Speech (Phase 4 TTS)
        speak_text(reply)

    # ------------------------------------------------------------------
    # EXPORT / CLEAR
    # ------------------------------------------------------------------
    def _on_export(self) -> None:
        path_str = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            title="Export Aries history",
        )
        if not path_str:
            return
        database.export_to_txt(Path(path_str))
        messagebox.showinfo(APP_NAME, f"History exported to:\n{path_str}")

    def _on_clear(self) -> None:
        confirmed = messagebox.askyesno(
            APP_NAME,
            "This will permanently delete all chat history. Continue?",
            icon="warning",
        )
        if not confirmed:
            return
        database.clear_history()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


if __name__ == "__main__":
    app = AriesApp()
    app.mainloop()