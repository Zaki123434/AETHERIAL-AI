"""
agen.py — Jembatan antara memori persisten dan graph LangGraph.

Fungsi utama:
- jalankan_agen(pesan_user) : menerima pesan teks dari pengguna,
  memuat memori dari file, menjalankan graph, dan mengembalikan
  respons asisten beserta mode yang terdeteksi.
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from graph import buat_graph
from memory import muat_memori

# Kompilasi graph sekali saja saat modul ini diimport
graph = buat_graph()


def jalankan_agen(pesan_user: str, mode_manual: str = None) -> dict:
    """
    Menjalankan satu siklus percakapan:
    1. Muat memori dari file JSON
    2. Buat State awal dengan pesan user + memori
       Jika mode_manual diisi, router akan memakai mode tersebut tanpa klasifikasi AI
    3. Jalankan graph (router → mode → update_memori)
    4. Kembalikan respons asisten dan mode yang terdeteksi

    Returns:
        dict dengan key:
        - "respons" : str, jawaban asisten
        - "mode"    : str, mode yang terdeteksi ("belajar"/"produktivitas"/"curhat")
    """
    # 1. Muat memori terkini dari file
    memori = muat_memori()

    mode_awal = mode_manual if mode_manual in ["belajar", "produktivitas", "curhat"] else ""

    # 2. Susun State awal
    state_awal = {
        "messages": [HumanMessage(content=pesan_user)],
        "mode_aktif": mode_awal,   # kosong = otomatis, terisi = mode manual
        "memori": memori,
    }

    # 3. Jalankan graph
    hasil = graph.invoke(state_awal)

    # 4. Ambil respons dan mode dari State akhir
    respons = hasil["messages"][-1].content
    mode = hasil["mode_aktif"]

    return {
        "respons": respons,
        "mode": mode,
    }


# Test cepat kalau file ini dijalankan langsung
if __name__ == "__main__":
    print("=== Test Agen (butuh koneksi ke Gemini API) ===\n")

    # Simulasi 3 pesan berbeda untuk test deteksi mode
    test_pesan = [
        "Halo! nama saya Budi, senang kenal",
        "Tolong jelaskan apa itu machine learning dengan analogi sederhana",
        "Saya lagi stres banget nih, tugas numpuk",
    ]

    for pesan in test_pesan:
        print(f"Pengguna : {pesan}")
        hasil = jalankan_agen(pesan)
        print(f"Mode     : {hasil['mode']}")
        print(f"Asisten  : {hasil['respons'][:150]}...")  # tampilkan 150 karakter pertama
        print("-" * 60)
