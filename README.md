# dirpacker

A CLI tool for packing a directory (text files only) into a single text file and unpacking it again.

## Usage

```
python dirpacker.py pack <source_directory> <output_file>
python dirpacker.py unpack <archive_file> <destination_directory>
python dirpacker.py pack --all <directory> <output_file>
```

### Options

| Option | Description |
|---|---|
| `pack` | Packs a directory into a `.dp` file |
| `unpack` | Unpacks a `.dp` file into a directory |
| `--all`, `-a` | Includes all files (attempts to read them as text regardless of extension) |

### Example

```
python dirpacker.py pack ./my_project project.dp
python dirpacker.py unpack project.dp ./restored_project
```

## File format

A custom marker-based text format with a dynamic prefix:

```
[DIRPCK] DIRPCK_20260702_123456_
DIRPCK_20260702_123456_[FILE] src/app.py
DIRPCK_20260702_123456_[SIZE] 256
DIRPCK_20260702_123456_[BEGIN]
...file contents...
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[FILE] src/utils/helper.sql
DIRPCK_20260702_123456_[SIZE] 128
DIRPCK_20260702_123456_[BEGIN]
...contents...
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[DIR] src/data
```

The first `[DIRPCK]` line contains the generated prefix (based on the date and time), which is repeated before every marker to eliminate the risk of collisions with file contents.

Markers:

| Marker | Description |
|---|---|
| `{PREFIX}[FILE] <path>` | Begins a file entry (relative path, using `/` as the separator) |
| `{PREFIX}[SIZE] <N>` | Content size in bytes |
| `{PREFIX}[BEGIN]` | Beginning of the file contents |
| `{PREFIX}[END]` | End of the file contents |
| `{PREFIX}[DIR] <path>` | Empty directory to create |

`[BEGIN]` and `[END]` wrap the file contents. `unpack` reads line by line until `[END]`, so converting `\n` ↔ `\r\n` (Unix/Windows) does not cause errors.

## Supported extensions

By default, only files with these text-file extensions are packed:

```
.txt .py .md .json .xml .html .css .js
.yml .yaml .toml .ini .cfg .conf .csv .log
.env .sql .sh .bat .ps1 .r .rb .php
.asm .inc .h .c .cpp .hpp .java .kt .swift
```

Binary files (`.png`, `.exe`, `.jpg`, etc.) are skipped.

## Ignored directories

`.git`, `__pycache__`, `node_modules`, `.svn`, `.hg`, `.idea`, `.vscode`, `.venv`, `venv`
