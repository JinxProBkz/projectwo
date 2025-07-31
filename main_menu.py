import os
import sys
import subprocess
import requests
import zipfile
import io
import os
import shutil
import sys

# ASCII Art
ASCII_ART = r"""
  _____              _              _     _______              
 |  __ \            (_)            | |   |__   __|             
 | |__) |_ __  ___   _   ___   ___ | |_     | |__      __ ___  
 |  ___/| '__|/ _ \ | | / _ \ / __|| __|    | |\ \ /\ / // _ \ 
 | |    | |  | (_) || ||  __/| (__ | |_     | | \ V  V /| (_) |
 |_|    |_|   \___/ | | \___| \___| \__|    |_|  \_/\_/  \___/ 
                   _/ |                                        
                  |__/   
  
     Definitive Edition V1.4 for Asesment Use Only 
     any issue/bug please email mohamad.mahesa@mastersystem.co.id
"""


GITHUB_REPO = "https://github.com/JinxProBkz/projectwo"  
BRANCH = "main"  

def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    raw_url = f"https://raw.githubusercontent.com/JinxProBkz/projectwo/{BRANCH}/version.txt"
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f" Gagal mengambil versi dari GitHub: {e}")
        return None

def update_from_github_zip():
    zip_url = f"{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
    
    try:
        print(" Mengunduh update...")
        response = requests.get(zip_url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            extract_folder = "__update_temp__"
            zip_ref.extractall(extract_folder)

        extracted_subfolder = os.path.join(extract_folder, os.listdir(extract_folder)[0])

        for item in os.listdir(extracted_subfolder):
            s = os.path.join(extracted_subfolder, item)
            d = os.path.join(".", item)

            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        shutil.rmtree(extract_folder)
        print(" Update selesai. Silakan restart aplikasi.")
        input("Tekan Enter untuk keluar...")
        sys.exit()

    except Exception as e:
        print(" Gagal update:", e)
        input("Tekan Enter untuk keluar...")

def check_and_update():
    print("\n Mengecek versi...")

    local_version = get_local_version()
    remote_version = get_remote_version()

    if remote_version is None:
        print(" Tidak bisa mengambil versi dari GitHub.")
        input("Tekan Enter untuk kembali ke menu...")
        return

    print(f" Versi saat ini: {local_version}")
    print(f" Versi tersedia: {remote_version}")

    if local_version == remote_version:
        print(" Sudah menggunakan versi terbaru.")
    else:
        print(" Versi baru tersedia!")
        pilihan = input("Ingin update sekarang? (y/n): ").strip().lower()
        if pilihan == 'y':
            update_from_github_zip()
        else:
            print(" Update dibatalkan.")

    input("Tekan Enter untuk kembali ke menu...")

def generate_json():
    print("\n[1] Generate JSON File from TXT...")
    # Jalankan txt_to_json.py
    subprocess.run([sys.executable, "core/txt_to_json.py"])

def generate_excel():
    print("\n[2] Generate Excel File from JSON...")
    # Jalankan json_to_excel.py
    subprocess.run([sys.executable, "core/json_to_excel.py"])


def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ASCII_ART)
        print("1. Generate Json File parsing from txt")
        print("2. Generate Excel File From Json")
        print("3. Update All script from GitHub")
        print("0. Back / Exit")
        choice = input("\nPilih menu: ")

        if choice == "1":
            generate_json()
            input("\nTekan ENTER untuk kembali ke menu...")
        elif choice == "2":
            generate_excel()
            input("\nTekan ENTER untuk kembali ke menu...")
        elif choice == '3':
            check_and_update()
        elif choice == "0":
            print("Keluar dari program.")
            break
        else:
            print("Silakan pilih menu yang valid!")
            input("\nTekan ENTER untuk kembali ke menu...")

if __name__ == "__main__":
    main_menu()
