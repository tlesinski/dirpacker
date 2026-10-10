# dirpacker

Narzędzie CLI do pakowania katalogu (tylko pliki tekstowe) do pojedynczego pliku tekstowego i rozpakowywania z powrotem.

## Użycie

```
python dirpacker.py pack <katalog_zrodlowy> <plik_wynikowy>
python dirpacker.py unpack <plik_paczki> <katalog_docelowy>
python dirpacker.py pack --all <katalog> <plik_wynikowy>
```

### Opcje

| Opcja | Opis |
|---|---|
| `pack` | Pakuje katalog do pliku `.dp` |
| `unpack` | Rozpakowuje plik `.dp` do katalogu |
| `--all`, `-a` | Włącza wszystkie pliki (próba odczytu jako tekst niezależnie od rozszerzenia) |

### Przykład

```
python dirpacker.py pack ./moj_projekt projekt.dp
python dirpacker.py unpack projekt.dp ./odtworzony_projekt
```

## Format pliku

Własny, tekstowy format markerowy z dynamicznym prefiksem:

```
[DIRPCK] DIRPCK_20260702_123456_
DIRPCK_20260702_123456_[FILE] src/app.py
DIRPCK_20260702_123456_[SIZE] 256
DIRPCK_20260702_123456_[BEGIN]
...treść pliku...
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[FILE] src/utils/helper.sql
DIRPCK_20260702_123456_[SIZE] 128
DIRPCK_20260702_123456_[BEGIN]
...treść...
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[DIR] src/data
```

Pierwsza linia `[DIRPCK]` zawiera wygenerowany prefiks (z datą/godziną), który jest powtarzany przed każdym znacznikiem — eliminuje ryzyko kolizji z treścią plików.

Znaczniki:

| Znacznik | Opis |
|---|---|
| `{PREFIX}[FILE] <ścieżka>` | Początek pliku (ścieżka względna, `/` jako separator) |
| `{PREFIX}[SIZE] <N>` | Rozmiar treści w bajtach |
| `{PREFIX}[BEGIN]` | Początek treści pliku |
| `{PREFIX}[END]` | Koniec treści pliku |
| `{PREFIX}[DIR] <ścieżka>` | Pusty katalog do utworzenia |

`[BEGIN]` i `[END]` otaczają treść pliku — `unpack` czyta linia po linii aż do `[END]`, dzięki czemu konwersja `\n`↔`\r\n` (Unix/Windows) nie powoduje błędów.

## Obsługiwane rozszerzenia

Tylko pliki tekstowe są domyślnie pakowane:

```
.txt .py .md .json .xml .html .css .js
.yml .yaml .toml .ini .cfg .conf .csv .log
.env .sql .sh .bat .ps1 .r .rb .php
.asm .inc .h .c .cpp .hpp .java .kt .swift
```

Pliki binarne (`.png`, `.exe`, `.jpg` itp.) są pomijane.

## Ignorowane katalogi

`.git`, `__pycache__`, `node_modules`, `.svn`, `.hg`, `.idea`, `.vscode`, `.venv`, `venv`
