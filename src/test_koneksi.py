"""
Script test koneksi:
1. Memastikan API key Gemini bisa dipakai untuk generate respons
2. Memastikan tracing LangSmith aktif dan mengirim data
"""
import os
from dotenv import load_dotenv

load_dotenv()  # baca file .env

from langchain_google_genai import ChatGoogleGenerativeAI

def main():
    print("=== Test Koneksi Gemini API ===")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
        )
        response = llm.invoke("Halo! Balas dengan satu kalimat singkat saja untuk konfirmasi koneksi berhasil.")
        print("Respons dari Gemini:")
        print(response.content)
        print("\n✅ Koneksi Gemini API BERHASIL")
    except Exception as e:
        print(f"\n❌ Koneksi Gemini API GAGAL: {e}")
        return

    print("\n=== Status LangSmith Tracing ===")
    tracing_enabled = os.getenv("LANGSMITH_TRACING", "false")
    project = os.getenv("LANGSMITH_PROJECT", "default")
    if tracing_enabled.lower() == "true":
        print(f"✅ Tracing AKTIF, cek dashboard project: '{project}' di https://smith.langchain.com")
    else:
        print("⚠️  Tracing belum aktif (LANGSMITH_TRACING bukan 'true')")

if __name__ == "__main__":
    main()
