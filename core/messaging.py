"""
Android Device Control for Aries AI (ADB Integration).
Supports multi-device management via serial numbers.
"""

from __future__ import annotations
import subprocess

ADB_PATH = "./adb.exe"

def get_connected_devices() -> list[str]:
    """Returns a list of connected Android device serial numbers."""
    try:
        result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().splitlines()[1:]  # Skip the header line
        devices = []
        for line in lines:
            if "\tdevice" in line:
                serial = line.split("\t")[0]
                devices.append(serial)
        return devices
    except Exception:
        return []

def execute_adb_command(command_args: list[str], serial: str | None = None) -> str:
    """
    Executes a local Android Debug Bridge (ADB) command.
    If multiple devices are connected and no serial is provided, 
    it defaults to the first available device.
    """
    try:
        devices = get_connected_devices()
        if not devices:
            return "ADB Error: No Android devices detected."

        # If no specific serial was passed, pick the first connected device
        target_serial = serial if serial else devices[0]

        cmd = [ADB_PATH, "-s", target_serial] + command_args
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.strip()
            return f"ADB Success (Device: {target_serial}):\n{output if output else 'Command executed successfully.'}"
        else:
            return f"ADB Error:\n{result.stderr.strip()}"
    except Exception as e:
        return f"[ADB Error: {str(e)}]"