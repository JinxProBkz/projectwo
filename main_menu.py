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
  
     Definitive Edition V1.1 for Asesment Use Only 
     any issue/bug please email mohamad.mahesa@mastersystem.co.id
"""


GITHUB_REPO = "https://github.com/JinxProBkz/projectwo.git"  
BRANCH = "main"  

def update_from_github_zip():
    print("\n🔄 Menjalankan update dari GitHub ZIP (tanpa Git)...")

    zip_url = f"{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
    
    try:
        # 1. Download ZIP dari GitHub
        response = requests.get(zip_url)
        if response.status_code != 200:
            raise Exception(f"Gagal mengunduh ZIP. Status code: {response.status_code}\nURL: {zip_url}")
        
        print("📥 ZIP repo berhasil diunduh.")

        # 2. Ekstrak ke memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            extract_folder = "__update_temp__"
            zip_ref.extractall(extract_folder)

        # 3. Ambil nama folder hasil ekstraksi
        extracted_subfolder = os.path.join(extract_folder, os.listdir(extract_folder)[0])

        # 4. Salin semua file/folder ke direktori kerja
        for item in os.listdir(extracted_subfolder):
            s = os.path.join(extracted_subfolder, item)
            d = os.path.join(".", item)

            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # 5. Bersihkan folder sementara
        shutil.rmtree(extract_folder)
        print("✅ Update berhasil. Silakan restart aplikasi untuk melihat perubahan.")
        input("Tekan Enter untuk keluar...")
        sys.exit()

    except Exception as e:
        print("\n❌ Gagal update dari GitHub.")
        print("📄 Error detail:")
        traceback.print_exc()
        input("\nTekan Enter untuk keluar...")

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
           update_from_github_zip()
        elif choice == "0":
            print("Keluar dari program.")
            break
        else:
            print("Silakan pilih menu yang valid!")
            input("\nTekan ENTER untuk kembali ke menu...")

if __name__ == "__main__":
    main_menu()
