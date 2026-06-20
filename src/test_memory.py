"""
Script test untuk memastikan modul memory.py bekerja dengan benar:
1. Memuat memori kosong (pertama kali)
2. Menambah pesan & update profil
3. Menyimpan ke file
4. Memuat ulang dari file (simulasi tutup-buka aplikasi)
"""
from memory import muat_memori, simpan_memori, tambah_pesan, update_profil, ambil_riwayat_terakhir

def main():
    print("=== Test 1: Muat memori (kemungkinan masih kosong) ===")
    memori = muat_memori()
    print(memori)

    print("\n=== Test 2: Tambah pesan & update profil ===")
    memori = tambah_pesan(memori, role="user", content="Halo, nama saya Andi")
    memori = update_profil(memori, "nama", "Andi")
    memori = tambah_pesan(memori, role="assistant", content="Halo Andi! Ada yang bisa saya bantu?", mode="curhat")
    print(memori)

    print("\n=== Test 3: Simpan ke file ===")
    simpan_memori(memori)
    print("Tersimpan ke data/memory.json")

    print("\n=== Test 4: Muat ulang dari file (simulasi buka aplikasi lagi) ===")
    memori_baru = muat_memori()
    print(memori_baru)

    print("\n=== Test 5: Ambil riwayat terakhir (maks 10) ===")
    print(ambil_riwayat_terakhir(memori_baru, n=10))

    assert memori_baru["user_profile"]["nama"] == "Andi", "Profil tidak tersimpan dengan benar!"
    assert len(memori_baru["chat_history"]) == 2, "Riwayat chat tidak tersimpan dengan benar!"
    print("\n✅ Semua test berhasil! Modul memory.py bekerja dengan benar.")

if __name__ == "__main__":
    main()
