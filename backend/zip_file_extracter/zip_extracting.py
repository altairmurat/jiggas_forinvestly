import zipfile
import shutil
from pathlib import Path
import json
from fastapi import HTTPException

BASE_DIR = Path(__file__).parent #backend directory
UPLOAD_DIR = BASE_DIR / "uploads" #backend/uploads
EXTRACT_DIR = UPLOAD_DIR / "extracted" #backend/uploads/extracted

UPLOAD_DIR.mkdir(exist_ok=True)
EXTRACT_DIR.mkdir(exist_ok=True)

#extract zip file and save contents to backend/uploads/extracted
def extract_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(EXTRACT_DIR)

def parse_txt_files(folder: Path, messages: list[str]):
    for txt_file in folder.rglob("*.txt"):
        try:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
                if text:
                    messages.append(text)
        except Exception:
            pass
        
def parse_json_files(folder: Path, messages: list[str]):
    for json_file in folder.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if isinstance(data, dict) and "messages" in data:
                    for msg in data["messages"]:
                        sender = msg.get("sender_name", "Unknown")
                        content = msg.get("content")
                        if content:
                            messages.append(f"{sender}: {content}")
        except Exception:
            pass

def parse_messages(folder: Path) -> str:
    messages: list[str] = []
    # from .txt and .json files in extracted/ folder, receive list of messages
    parse_txt_files(folder, messages)
    parse_json_files(folder, messages)
    if not messages:
        raise HTTPException(status_code=400, detail="ZIP contains no readable .txt chat files")
    # Token safety (limit to last 1000 characters)
    return "\n".join(messages)[100:]

#function to clean extracted/ directory
def clean_extract_dir():
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir()