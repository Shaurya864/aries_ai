import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shlex
import urllib.parse
import customtkinter as ctk
from core.messaging import execute_adb_command, get_connected_devices

# Set up general appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class AriesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aries AI — Phase 7 HUD & Telemetry")
        self.geometry("1100x700")

        # Configure grid layout (2 rows, 2 columns)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Reactor-Core Header (Top spanning both columns)
        self.create_header()

        # 2. Telemetry Sidebar (Left column)
        self.create_sidebar()

        # 3. Main Chat & Control Panel (Right column)
        self.create_main_panel()

    def create_header(self):
        """Reactor-core header simulation bar."""
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="⚡ ARIES CORE [ONLINE] — DIRECT ADB PROTOCOL ACTIVE", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ffcc"
        )
        self.title_label.pack(side="left", padx=20, pady=15)

    def create_sidebar(self):
        """Telemetry sidebar with live device statuses and protocols."""
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")

        # Sidebar Title
        self.sb_title = ctk.CTkLabel(self.sidebar_frame, text="TELEMETRY", font=ctk.CTkFont(size=15, weight="bold"))
        self.sb_title.pack(padx=20, pady=(20, 10), anchor="w")

        # Connected Devices Section
        self.dev_header = ctk.CTkLabel(self.sidebar_frame, text="Connected Devices", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.dev_header.pack(padx=20, pady=(10, 0), anchor="w")

        # Dynamically fetch connected devices
        try:
            devices = get_connected_devices()
            if devices:
                dev_text = "\n".join([f"• {dev} (Online)" for dev in devices])
            else:
                dev_text = "• No devices connected"
        except Exception:
            dev_text = "• Realme 6 (MNXS5...)"

        self.dev_list = ctk.CTkLabel(
            self.sidebar_frame, 
            text=dev_text, 
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.dev_list.pack(padx=20, pady=(5, 15), anchor="w")

        # Security Protocols Panel
        self.sec_header = ctk.CTkLabel(self.sidebar_frame, text="Security Protocols", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.sec_header.pack(padx=20, pady=(10, 0), anchor="w")

        self.sec_status = ctk.CTkLabel(
            self.sidebar_frame, 
            text="STATUS: SECURE\nENCRYPTION: LOCAL ADB\nCLOUD SYNC: BYPASSED", 
            font=ctk.CTkFont(size=11),
            text_color="#00ffcc",
            justify="left"
        )
        self.sec_status.pack(padx=20, pady=(5, 20), anchor="w")

    def create_main_panel(self):
        """Main interaction window for chat and system logs."""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Chat / Output Box
        self.chat_box = ctk.CTkTextbox(self.main_frame, width=400, corner_radius=8)
        self.chat_box.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.chat_box.insert("0.0", "Aries HUD initialized successfully.\nReady for commands...\n")
        self.chat_box.configure(state="disabled")

        # Input Row
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text='Enter command (e.g. text 0947692453 "Hello")...')
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        # Bind the Enter key to submit commands
        self.entry.bind("<Return>", self.execute_command)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Execute", width=100, command=self.execute_command)
        self.send_btn.grid(row=0, column=1)

    def execute_command(self, event=None):
        """Handles user input, triggers backend ADB/intents, and updates the chat box."""
        query = self.entry.get().strip()
        if not query:
            return

        # Enable chat box temporarily to append text
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n> {query}\n")
        self.entry.delete(0, "end")

        # Route to backend logic
        try:
            query_lower = query.lower()
            if "battery" in query_lower:
                result = execute_adb_command(['shell', 'dumpsys', 'battery'])
                response_text = f"[ADB Hardware Success]:\n{result}"
            elif "launch" in query_lower or "open" in query_lower:
                if "whatsapp" in query_lower:
                    cmd = ['shell', 'am', 'start', '-n', 'com.whatsapp/.HomeActivity']
                elif "youtube" in query_lower:
                    cmd = ['shell', 'monkey', '-p', 'com.google.android.youtube', '-c', 'android.intent.category.LAUNCHER', '1']
                else:
                    cmd = ['shell', 'am', 'start', '-n', 'com.android.settings/.Settings']
                
                result = execute_adb_command(cmd)
                response_text = f"[App Launch Success]:\n{result}"
            elif "call" in query_lower:
                parts = shlex.split(query)
                number = parts[1] if len(parts) > 1 else ""
                if number:
                    cmd = ['shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{number}']
                    result = execute_adb_command(cmd)
                    response_text = f"[Call Initiated to {number}]:\n{result}"
                else:
                    response_text = "Error: Specify a phone number (e.g., 'call 1234567890')."
            elif "text" in query_lower or "sms" in query_lower:
                parts = shlex.split(query)
                if len(parts) >= 3:
                    number = parts[1]
                    message = parts[2]
                    
                    # URL-encode the message so apostrophes and spaces don't break the Android shell
                    encoded_message = urllib.parse.quote(message)
                    
                    cmd = [
                        'shell', 'am', 'start', 
                        '-a', 'android.intent.action.VIEW', 
                        '-d', f'sms:{number}?body={encoded_message}'
                    ]
                    result = execute_adb_command(cmd)
                    response_text = f"[SMS Intent Triggered for {number}]:\n{result}"
                else:
                    response_text = 'Error: Format must be text <number> "<message>".'
            else:
                response_text = f"Aries processed command: '{query}' (Unrecognized syntax)"
        except Exception as e:
            response_text = f"[Error Executing Command]: {e}"

        self.chat_box.insert("end", f"{response_text}\n")
        self.chat_box.see("end")  # Auto-scroll to the bottom of the log
        self.chat_box.configure(state="disabled")

if __name__ == "__main__":
    app = AriesApp()
    app.mainloop()