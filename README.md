# Asynchroniczne przesyłanie danych z konwersją obrazów na ASCII art

## Funkcje i cechy systemu:
- Skrypt pythonowy odpalający serwera i klienta
- Użycie wątków
- Komunikacja asynchroniczna z użyciem wątków
- Konwersja obrazów do ASCII art

## Wymagania
- Python 3.x
- Biblioteka Pillow (PIL) - `pip install pillow`

## Użycie

### Uruchomienie serwera
```
python serwer_w.py
```

### Uruchomienie klienta
```
python klient_w.py
```

### Konwersja obrazu na ASCII art
1. W interfejsie klienta wybierz opcję "2. Konwertuj obraz na ASCII art"
2. Podaj ścieżkę do pliku obrazu (np. `test_image.png`)
3. Podaj szerokość ASCII art (domyślnie 100 znaków)
4. ASCII art zostanie wyświetlony w konsoli klienta

## Jak to działa
- Klient wysyła żądanie do serwera w formacie JSON, zawierające ścieżkę do obrazu
- Serwer odczytuje obraz, przetwarza go na ASCII art i odsyła wynik do klienta
- Klient odbiera i wyświetla ASCII art

## Testowanie
W repozytorium znajduje się przykładowy plik obrazu `test_image.png` do testowania funkcjonalności.
