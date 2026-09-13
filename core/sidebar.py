import customtkinter as ctk

class TelemetrySidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        
        # Sidebar Title
        self.title_label = ctk.CTkLabel(self, text="ARIES TELEMETRY", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.pack(padx=20, pady=20)
        
        # Device Status Section
        self.device_header = ctk.CTkLabel(self, text="Connected Devices", font=ctk.CTkFont(size=12, weight="bold"))
        self.device_header.pack(padx=20, anchor="w")
        
        self.device_status = ctk.CTkLabel(self, text="• Realme 6 (Online)\n• Secondary (Online)", text_color="green", font=ctk.CTkFont(size=11))
        self.device_status.pack(padx=20, pady=(5, 20), anchor="w")
        
        # Security Protocols Panel
        self.sec_header = ctk.CTkLabel(self, text="Security Protocols", font=ctk.CTkFont(size=12, weight="bold"))
        self.sec_header.pack(padx=20, anchor="w")
        
        self.sec_status = ctk.CTkLabel(self, text="STATUS: ACTIVE\nENCRYPTION: LOCAL ADB", text_color="cyan", font=ctk.CTkFont(size=11))
        self.sec_status.pack(padx=20, pady=(5, 20), anchor="w")