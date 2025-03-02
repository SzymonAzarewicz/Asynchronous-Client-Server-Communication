import sys
import os
import subprocess
import platform

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def main():
    clear_screen()
    print("=" * 50)
    print("          WYBÓR TRYBU KLIENTA")
    print("=" * 50)
    print("1. Klient tekstowy (konsolowy)")
    print("2. Klient graficzny (GUI)")
    print("0. Wyjście")
    print("=" * 50)
    
    choice = input("Wybierz opcję (0-2): ")
    
    if choice == '1':
        print("\nUruchamianie klienta tekstowego...\n")
        try:
            subprocess.run(["python", "klient_w.py"], check=True)
        except subprocess.CalledProcessError:
            print("Wystąpił błąd podczas uruchamiania klienta tekstowego.")
        except FileNotFoundError:
            print("Nie znaleziono pliku klient_w.py")
    elif choice == '2':
        print("\nUruchamianie klienta graficznego...\n")
        try:
            subprocess.run(["python", "klient_gui.py"], check=True)
        except subprocess.CalledProcessError:
            print("Wystąpił błąd podczas uruchamiania klienta graficznego.")
        except FileNotFoundError:
            print("Nie znaleziono pliku klient_gui.py")
    elif choice == '0':
        print("\nWyjście z programu...")
        sys.exit(0)
    else:
        print("\nNieprawidłowy wybór. Spróbuj ponownie.")
        input("Naciśnij Enter, aby kontynuować...")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWyjście z programu...")
    except Exception as e:
        print(f"\nWystąpił nieoczekiwany błąd: {str(e)}")
