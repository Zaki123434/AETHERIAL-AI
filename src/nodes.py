"""
Semua node LangGraph untuk asisten personal multi-mode.

Node yang ada:
1. node_router      — mendeteksi mode dari pesan terakhir pengguna
2. node_belajar     — merespons dalam mode belajar (edukatif, sabar, pakai analogi)
3. node_produktivitas — merespons dalam mode produktivitas (ringkas, action-oriented)
4. node_curhat      — merespons dalam mode curhat (empatik, mendengarkan)
5. node_update_memori — menyimpan pesan terbaru ke file JSON setelah respons dihasilkan
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AsitenState
from memory import tambah_pesan, simpan_memori, ambil_riwayat_terakhir, update_profil

# ─────────────────────────────────────────────
# Inisialisasi model Gemini 
# ─────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
)

# ─────────────────────────────────────────────
# NODE 1: ROUTER
# Mendeteksi mode dari pesan terakhir pengguna.
# Tidak memanggil LLM untuk jawaban — hanya klasifikasi singkat.
# ─────────────────────────────────────────────
def node_router(state: AsitenState) -> dict:
    """
    Membaca pesan terakhir dari pengguna dan mengklasifikasikannya
    ke salah satu dari tiga mode: belajar, produktivitas, curhat.
    """
    mode_manual = state.get("mode_aktif", "")
    if mode_manual in ["belajar", "produktivitas", "curhat"]:
        return {"mode_aktif": mode_manual}

    pesan_terakhir = state["messages"][-1].content

    prompt_router = f"""Kamu adalah classifier teks. Tugasmu HANYA menentukan kategori dari pesan pengguna.
Pilih SATU dari tiga kategori ini:
- belajar      : pengguna ingin belajar, bertanya tentang konsep/ilmu, minta penjelasan, latihan soal
- produktivitas: pengguna ingin mencatat tugas, membuat rencana, mengatur jadwal, minta bantuan kerja
- curhat        : pengguna ingin berbagi perasaan, cerita harian, curhat, mencari dukungan emosional

Pesan pengguna: "{pesan_terakhir}"

Jawab HANYA dengan satu kata: belajar, produktivitas, atau curhat. Tanpa penjelasan apapun."""

    respons = llm.invoke([HumanMessage(content=prompt_router)])
    mode = respons.content.strip().lower()

    # Validasi — kalau model mengembalikan sesuatu di luar tiga pilihan, default ke curhat
    if mode not in ["belajar", "produktivitas", "curhat"]:
        mode = "curhat"

    return {"mode_aktif": mode}


# ─────────────────────────────────────────────
# Helper: bangun konteks riwayat untuk dikirim ke LLM
# ─────────────────────────────────────────────
def _bangun_konteks_riwayat(memori: dict) -> str:
    """Mengubah riwayat chat terakhir menjadi teks konteks ringkas untuk system prompt."""
    riwayat = ambil_riwayat_terakhir(memori, n=8)
    if not riwayat:
        return "Belum ada riwayat percakapan sebelumnya."
    baris = []
    for pesan in riwayat:
        role = "Pengguna" if pesan["role"] == "user" else "Asisten"
        baris.append(f"{role}: {pesan['content']}")
    return "\n".join(baris)


def _bangun_info_profil(memori: dict) -> str:
    """Mengubah profil pengguna menjadi teks ringkas untuk system prompt."""
    profil = memori.get("user_profile", {})
    if not profil:
        return "Belum ada info profil pengguna."
    return "\n".join([f"- {k}: {v}" for k, v in profil.items()])


# ─────────────────────────────────────────────
# NODE 2: MODE BELAJAR
# ─────────────────────────────────────────────
def node_belajar(state: AsitenState) -> dict:
    """
    Merespons dalam mode belajar:
    - Menjelaskan konsep dengan sabar dan terstruktur
    - Menggunakan analogi bila perlu
    - Bisa memberikan contoh soal atau latihan
    """
    memori = state["memori"]
    pesan_terakhir = state["messages"][-1].content

    system_prompt = f"""Kamu adalah asisten belajar pribadi yang sabar dan menyenangkan.
Gaya komunikasimu: menggunakan bahasa yang mudah dipahami, suka memberi analogi sehari-hari,
terstruktur (poin-poin atau langkah-langkah), dan selalu menawarkan contoh atau latihan bila relevan.

Info tentang pengguna:
{_bangun_info_profil(memori)}

Riwayat percakapan terakhir:
{_bangun_konteks_riwayat(memori)}

Sekarang pengguna mengirim: "{pesan_terakhir}"
Bantu mereka belajar dengan baik!"""

    respons = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=pesan_terakhir),
    ])

    return {"messages": [AIMessage(content=respons.content)]}


# ─────────────────────────────────────────────
# NODE 3: MODE PRODUKTIVITAS
# ─────────────────────────────────────────────
def node_produktivitas(state: AsitenState) -> dict:
    """
    Merespons dalam mode produktivitas:
    - Ringkas, langsung ke poin
    - Membantu mencatat tugas, membuat checklist, atau rencana kerja
    - Nada profesional tapi tetap ramah
    """
    memori = state["memori"]
    pesan_terakhir = state["messages"][-1].content

    system_prompt = f"""Kamu adalah asisten produktivitas pribadi yang efisien dan to-the-point.
Gaya komunikasimu: ringkas, langsung ke inti, suka membuat checklist atau daftar prioritas,
dan selalu mengarahkan pengguna ke aksi nyata yang bisa langsung dikerjakan.

Info tentang pengguna:
{_bangun_info_profil(memori)}

Riwayat percakapan terakhir:
{_bangun_konteks_riwayat(memori)}

Sekarang pengguna mengirim: "{pesan_terakhir}"
Bantu mereka jadi lebih produktif!"""

    respons = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=pesan_terakhir),
    ])

    return {"messages": [AIMessage(content=respons.content)]}


# ─────────────────────────────────────────────
# NODE 4: MODE CURHAT
# ─────────────────────────────────────────────
def node_curhat(state: AsitenState) -> dict:
    """
    Merespons dalam mode curhat:
    - Empatik dan hangat
    - Mendengarkan dulu sebelum memberi saran
    - Tidak terburu-buru memberikan solusi
    """
    memori = state["memori"]
    pesan_terakhir = state["messages"][-1].content

    system_prompt = f"""Kamu adalah teman curhat yang hangat, empatik, dan penuh perhatian.
Gaya komunikasimu: mendengarkan dengan tulus, tidak menghakimi, mengakui perasaan pengguna
sebelum memberi saran, dan membuat mereka merasa didengar dan diterima.

Info tentang pengguna:
{_bangun_info_profil(memori)}

Riwayat percakapan terakhir:
{_bangun_konteks_riwayat(memori)}

Sekarang pengguna mengirim: "{pesan_terakhir}"
Dengarkan dan dampingi mereka dengan tulus!"""

    respons = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=pesan_terakhir),
    ])

    return {"messages": [AIMessage(content=respons.content)]}


# ─────────────────────────────────────────────
# NODE 5: UPDATE MEMORI
# Dipanggil setelah salah satu node mode menghasilkan respons.
# Tugasnya menyimpan pasangan (pesan user + respons asisten) ke file JSON.
# ─────────────────────────────────────────────
def node_update_memori(state: AsitenState) -> dict:
    """
    Menyimpan pesan terbaru ke memori persisten (file JSON).
    Dipanggil setelah node mode selesai, sebelum respons ditampilkan ke pengguna.
    """
    memori = state["memori"]
    mode = state["mode_aktif"]
    messages = state["messages"]

    # Ambil pesan user dan respons asisten terbaru
    # messages[-2] = pesan user terakhir, messages[-1] = respons asisten
    if len(messages) >= 2:
        pesan_user = messages[-2].content
        respons_asisten = messages[-1].content

        memori = tambah_pesan(memori, role="user", content=pesan_user)
        memori = tambah_pesan(memori, role="assistant", content=respons_asisten, mode=mode)

        # Kalau pengguna menyebut namanya, simpan ke profil
        pesan_lower = pesan_user.lower()
        for kata in ["nama saya", "saya bernama", "panggil saya", "namaku"]:
            if kata in pesan_lower:
                idx = pesan_lower.find(kata) + len(kata)
                sisa = pesan_user[idx:].strip().split()[0].rstrip(".,!")
                if sisa:
                    memori = update_profil(memori, "nama", sisa.capitalize())
                break

        simpan_memori(memori)

    return {"memori": memori}


# ─────────────────────────────────────────────
# CONDITIONAL EDGE: Penentu arah setelah Router
# ─────────────────────────────────────────────
def tentukan_mode(state: AsitenState) -> str:
    """
    Dibaca oleh LangGraph sebagai conditional edge.
    Mengembalikan nama node tujuan berdasarkan mode_aktif di State.
    """
    return state["mode_aktif"]  # "belajar", "produktivitas", atau "curhat"
