# Aplikacja Komunikacyjna Klient-Serwer

## 🚀 Funkcjonalności

### Podstawowe
- Komunikacja TCP/IP między wieloma klientami a serwerem
- Wysyłanie wiadomości tekstowych w czasie rzeczywistym
- Obsługa wielu klientów równocześnie (wątki)

### Zaawansowane
1. **Konwersja obrazu na ASCII Art**
   - Automatyczne dostosowywanie szerokości do wymiarów obrazu
   - Domyślny plik `emoji.png`
   - Obsługa formatów: PNG, JPG, JPEG, BMP

2. **Przesyłanie dokumentów DOCX**
   - Wybór pliku przez okno dialogowe
   - Ekstrakcja tekstu z dokumentu
   - Automatyczne zapisywanie na serwerze z unikalną nazwą
   - Powiadamianie innych klientów o przesłanym dokumencie

3. **Interfejs Użytkownika**
   - Dwie wersje klienta:
     - **Konsolowa** [klient_w.py]
     - **Graficzna GUI** [klient_gui.py] z użyciem PySide6
   - Możliwość wyboru interfejsu przez launcher [klient.py]

4. **Zabezpieczenia i Obsługa Błędów**
   - Podstawowa walidacja plików
   - Komunikaty o błędach w GUI
   - Automatyczne czyszczenie historii wiadomości

## 📦 Wymagania
- Python 3.9+