"""
Merakit semua node menjadi satu graph LangGraph yang utuh.

Alur graph:
START → router → [belajar | produktivitas | curhat] → update_memori → END

Conditional edge di antara router dan node mode:
  - mode_aktif == "belajar"       → node_belajar
  - mode_aktif == "produktivitas" → node_produktivitas
  - mode_aktif == "curhat"        → node_curhat
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from state import AsitenState
from nodes import (
    node_router,
    node_belajar,
    node_produktivitas,
    node_curhat,
    node_update_memori,
    tentukan_mode,
)


def buat_graph():
    """
    Membangun dan mengkompilasi graph asisten personal multi-mode.
    Mengembalikan graph yang siap dijalankan (.invoke() / .stream()).
    """
    builder = StateGraph(AsitenState)

    # ── Daftarkan semua node ──
    builder.add_node("router", node_router)
    builder.add_node("belajar", node_belajar)
    builder.add_node("produktivitas", node_produktivitas)
    builder.add_node("curhat", node_curhat)
    builder.add_node("update_memori", node_update_memori)

    # ── Definisikan alur (edges) ──
    # 1. Mulai dari START, selalu masuk ke router dulu
    builder.add_edge(START, "router")

    # 2. Dari router, pilih mode berdasarkan hasil deteksi (conditional edge)
    builder.add_conditional_edges(
        "router",            # dari node ini
        tentukan_mode,       # fungsi yang menentukan tujuan
        {                    # peta: hasil fungsi → nama node tujuan
            "belajar": "belajar",
            "produktivitas": "produktivitas",
            "curhat": "curhat",
        }
    )

    # 3. Setelah node mode selesai, selalu lanjut ke update_memori
    builder.add_edge("belajar", "update_memori")
    builder.add_edge("produktivitas", "update_memori")
    builder.add_edge("curhat", "update_memori")

    # 4. Setelah update_memori, selesai
    builder.add_edge("update_memori", END)

    # ── Kompilasi graph ──
    graph = builder.compile()
    return graph


# Jalankan langsung untuk test cepat struktur graph
if __name__ == "__main__":
    graph = buat_graph()
    print("✅ Graph berhasil dikompilasi!")
    print("Nodes:", list(graph.nodes))
