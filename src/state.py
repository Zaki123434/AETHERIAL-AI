"""
Mendefinisikan State — struktur data yang mengalir di seluruh graph LangGraph.
Setiap node menerima State ini dan mengembalikan perubahan pada field tertentu.
"""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AsitenState(TypedDict):
    """
    State utama yang mengalir di seluruh graph.

    Fields:
    - messages   : riwayat percakapan dalam format LangChain Message
                   (HumanMessage, AIMessage). Menggunakan add_messages
                   supaya setiap update MENAMBAHKAN pesan, bukan mengganti.
    - mode_aktif : mode yang terdeteksi router ("belajar"/"produktivitas"/"curhat")
    - memori     : seluruh data memori persisten dari file JSON (chat_history + user_profile)
    """
    messages: Annotated[list, add_messages]
    mode_aktif: str
    memori: dict
