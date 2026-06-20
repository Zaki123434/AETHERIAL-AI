"""
Modul ini bertugas menyimpan dan memuat memori asisten:
1. Riwayat percakapan (chat_history)
2. Profil pengguna (user_profile) - info yang diingat jangka panjang

Disimpan sebagai file JSON sederhana di folder data/.
"""
import json
import os
from datetime import datetime

# Lokasi file penyimpanan
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")


def _pastikan_folder_data_ada():
    """Membuat folder data/ kalau belum ada."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _struktur_memori_kosong():
    """Struktur default kalau belum ada memori sama sekali (pertama kali dijalankan)."""
    return {
        "chat_history": [],       # list of {"role": "user"/"assistant", "content": str, "mode": str, "timestamp": str}
        "user_profile": {},       # dict bebas, contoh: {"nama": "Budi", "catatan": ["suka belajar dengan analogi"]}
    }


def muat_memori() -> dict:
    """
    Membaca memori dari file JSON.
    Kalau file belum ada (pertama kali jalan), kembalikan struktur kosong.
    """
    _pastikan_folder_data_ada()

    if not os.path.exists(MEMORY_FILE):
        return _struktur_memori_kosong()

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Kalau file korup/rusak, jangan crash - kembalikan struktur kosong
        return _struktur_memori_kosong()


def simpan_memori(memori: dict):
    """Menulis seluruh objek memori ke file JSON."""
    _pastikan_folder_data_ada()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memori, f, indent=2, ensure_ascii=False)


def tambah_pesan(memori: dict, role: str, content: str, mode: str = None) -> dict:
    """
    Menambahkan satu pesan baru ke riwayat percakapan.
    role: "user" atau "assistant"
    mode: mode aktif saat ini (Belajar/Produktivitas/Curhat), boleh None untuk pesan user
    """
    memori["chat_history"].append({
        "role": role,
        "content": content,
        "mode": mode,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    return memori


def update_profil(memori: dict, key: str, value) -> dict:
    """Menambah atau memperbarui satu field di profil pengguna."""
    memori["user_profile"][key] = value
    return memori


def ambil_riwayat_terakhir(memori: dict, n: int = 10) -> list:
    """
    Mengambil N pesan terakhir saja dari riwayat.
    Berguna supaya prompt ke LLM tidak terlalu panjang/boros token.
    """
    return memori["chat_history"][-n:]
