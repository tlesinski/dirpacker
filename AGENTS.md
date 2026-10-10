# dirpacker — instrukcje dla asystenta AI

## O projekcie

Narzędzie CLI w Pythonie do pakowania katalogu z plikami tekstowymi do jednego pliku tekstowego i rozpakowywania z powrotem.

## Komendy uruchomieniowe

```bash
# pakowanie
python dirpacker.py pack <katalog_zrodlowy> <plik_wynikowy.dp>

# rozpakowywanie
python dirpacker.py unpack <plik.dp> <katalog_docelowy>

# pakowanie wszystkich plików (próba odczytu jako tekst)
python dirpacker.py pack --all <katalog> <plik.dp>
```

## Struktura kodu

- `dirpacker.py` — jedyny plik źródłowy
- `pack()` — generuje dynamiczny prefiks (`gen_prefix`), rekurencyjnie przechodzi katalog, zapisuje znaczniki `{prefix}[FILE]`, `{prefix}[SIZE]` i treść; otacza treść `{prefix}[BEGIN]`/`{prefix}[END]`; na koniec dopisuje puste katalogi jako `{prefix}[DIR]`
- `unpack()` — czyta plik linia po linii w trybie binarnym, odczytuje prefiks z linii `[DIRPCK]`, parsuje znaczniki, odtwarza pliki i katalogi; treść między `[BEGIN]` a `[END]` odtwarza liniowo — odporny na konwersję `\n`↔`\r\n`
- `is_text_file()` — sprawdza rozszerzenie względem zbioru `TEXT_EXTENSIONS`
- `get_rel_path()` — zwraca relatywną ścieżkę z forward slashami
- `gen_prefix()` — generuje unikalny prefiks `DIRPCK_YYYYMMDD_HHMMSS_` na podstawie bieżącego czasu

## Format pliku

```
[DIRPCK] DIRPCK_20260702_123456_
DIRPCK_20260702_123456_[FILE] rel/ścieżka/pliku.txt
DIRPCK_20260702_123456_[SIZE] <liczba_bajtów>
DIRPCK_20260702_123456_[BEGIN]
<treść plika — dokładnie N bajtów>
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[DIR] rel/ścieżka/pustego/katalogu
```

Pierwsza linia `[DIRPCK] <prefix>` definiuje dynamiczny prefiks (datetime). Każdy znacznik w pliku jest poprzedzony tym prefiksem — gwarantuje brak kolizji marker-content. Plik zapisywany w trybie binarnym.

`[BEGIN]` i `[END]` otaczają treść pliku. `unpack` czyta linia po linii aż do `[END]` — dzięki temu konwersja `\n` ↔ `\r\n` (Unix/Windows) nie powoduje błędów. `[SIZE]` służy do walidacji rozmiaru.

## Rozszerzenia plików tekstowych

```python
TEXT_EXTENSIONS = {
    '.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js',
    '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.csv', '.log',
    '.env', '.sql', '.sh', '.bat', '.ps1', '.r', '.rb', '.php',
    '.asm', '.inc', '.h', '.c', '.cpp', '.hpp', '.java', '.kt', '.swift',
}
```

## Ignorowane katalogi

```python
IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.svn', '.hg', '.idea', '.vscode', '.venv', 'venv'}
```

## Ważne zasady

1. Wszystkie ścieżki w pliku `.dp` używają `/` (nawet na Windows)
2. Plik paczki jest zawsze w trybie binarnym (`'wb'`, `'rb'`)
3. `[SIZE]` wskazuje dokładną liczbę bajtów do odczytania — nie ma ryzyka kolizji marker-content
4. Puste katalogi są zapisywane na końcu pliku jako `[DIR]`, po wszystkich plikach
5. `os.makedirs(..., exist_ok=True)` chroni przed błędami przy zagnieżdżonych ścieżkach
6. Przy `pack` katalogi ignorowane (`IGNORE_DIRS`) są odfiltrowywane w `os.walk` przez `dirs[:] = [...]`
