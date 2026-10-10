# dirpacker — AI assistant instructions

## About the project

A Python CLI tool for packing a directory of text files into a single text file and unpacking it again.

## Commands

```bash
# pack
python dirpacker.py pack <source_directory> <output_file.dp>

# unpack
python dirpacker.py unpack <archive.dp> <destination_directory>

# pack all files (attempt to read them as text)
python dirpacker.py pack --all <directory> <archive.dp>
```

## Code structure

- `dirpacker.py` — the only source file
- `pack()` — generates a dynamic prefix (`gen_prefix`), recursively walks the directory, writes `{prefix}[FILE]` and `{prefix}[SIZE]` markers and the contents; wraps contents in `{prefix}[BEGIN]`/`{prefix}[END]`; appends empty directories as `{prefix}[DIR]` at the end
- `unpack()` — reads the archive line by line in binary mode, reads the prefix from the `[DIRPCK]` header, parses markers, and restores files and directories; restores contents between `[BEGIN]` and `[END]` line by line, making it resilient to `\n`↔`\r\n` conversion
- `is_text_file()` — checks the extension against the `TEXT_EXTENSIONS` set
- `get_rel_path()` — returns a relative path with forward slashes
- `gen_prefix()` — generates a unique `DIRPCK_YYYYMMDD_HHMMSS_` prefix based on the current time

## Archive format

```
[DIRPCK] DIRPCK_20260702_123456_
DIRPCK_20260702_123456_[FILE] path/to/file.txt
DIRPCK_20260702_123456_[SIZE] <size_in_bytes>
DIRPCK_20260702_123456_[BEGIN]
<file contents>
DIRPCK_20260702_123456_[END]
DIRPCK_20260702_123456_[DIR] path/to/empty/directory
```

The first `[DIRPCK] <prefix>` line defines the dynamic prefix (date and time). Every marker in the archive is preceded by this prefix, preventing collisions between markers and file contents. The archive is written in binary mode.

`[BEGIN]` and `[END]` wrap the file contents. `unpack` reads line by line until `[END]`. `[SIZE]` stores and validates the content size while ignoring carriage returns (`\r`), so converting line endings between Unix and Windows does not change the size check. This normalization affects the size check only; file contents are not otherwise modified.

## Text-file extensions

```python
TEXT_EXTENSIONS = {
    '.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js',
    '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.csv', '.log',
    '.env', '.sql', '.sh', '.bat', '.ps1', '.r', '.rb', '.php',
    '.asm', '.inc', '.h', '.c', '.cpp', '.hpp', '.java', '.kt', '.swift',
}
```

## Ignored directories

```python
IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.svn', '.hg', '.idea', '.vscode', '.venv', 'venv'}
```

## Important rules

1. All paths in `.dp` archives use `/` (even on Windows).
2. Archive files are always opened in binary mode (`'wb'`, `'rb'`).
3. `[SIZE]` stores the content size in bytes while ignoring carriage returns (`\r`) and is used for validation; `[END]` marks the end of the content.
4. Empty directories are written at the end of the archive as `[DIR]` entries, after all files.
5. `os.makedirs(..., exist_ok=True)` prevents errors when creating nested paths.
6. During `pack`, ignored directories (`IGNORE_DIRS`) are filtered in `os.walk` using `dirs[:] = [...]`.
