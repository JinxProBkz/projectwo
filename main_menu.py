import os
import sys
import subprocess

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
        print("0. Back / Exit")
        choice = input("\nPilih menu: ")

        if choice == "1":
            generate_json()
            input("\nTekan ENTER untuk kembali ke menu...")
        elif choice == "2":
            generate_excel()
            input("\nTekan ENTER untuk kembali ke menu...")
        elif choice == "0":
            print("Keluar dari program.")
            break
        else:
            print("Silakan pilih menu yang valid!")
            input("\nTekan ENTER untuk kembali ke menu...")

if __name__ == "__main__":
    main_menu()
