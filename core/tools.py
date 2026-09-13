from __future__ import annotations
import io
from pathlib import Path
import pyautogui
from google import genai
from google.genai import types
from core.config import GEMINI_MODEL, require_gemini_key

def search_local_files(query: str, search_dir: str | None = None) -> str:
    """
    Searches for files locally using pathlib over the user's Documents or target folder.
    """
    if not search_dir:
        # Default to user's Documents folder or home directory
        search_dir = Path.home() / "Documents"
    else:
        search_dir = Path(search_dir)

    if not search_dir.exists():
        return f"[Error] Search directory does not exist: {search_dir}"

    matches = []
    try:
        # Search for files matching the query pattern recursively
        for path in search_dir.rglob(f"*{query}*"):
            if path.is_file():
                matches.append(str(path))
                if len(matches) >= 10:  # Limit results to top 10
                    break
    except Exception as e:
        return f"[Error scanning files: {str(e)}]"

    if not matches:
        return f"No local files found matching '{query}' in {search_dir}."
    
    return "Found local files:\n- " + "\n- ".join(matches)


def capture_and_analyze_screen(prompt: str = "Describe what is currently visible on my screen.") -> str:
    """
    Takes a PyAutoGUI screenshot, converts it to JPEG bytes, and passes it 
    to Gemini as a multimodal request.
    """
    try:
        # 1. Capture screen screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()
        
        # 2. Save image to an in-memory bytes buffer as JPEG
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()

        # 3. Call Gemini with multimodal image input using the correct SDK types pattern
        client = genai.Client(api_key=require_gemini_key())
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                prompt
            ]
        )
        
        return response.text or "(No description generated)"
    except Exception as e:
        return f"[Error capturing/analyzing screen: {str(e)}]"