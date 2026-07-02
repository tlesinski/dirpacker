#!/usr/bin/env python3
import os
import sys
import argparse

TEXT_EXTENSIONS = {
    '.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js',
    '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.csv', '.log',
    '.env', '.sql', '.sh', '.bat', '.ps1', '.r', '.rb', '.php',
    '.asm', '.inc', '.h', '.c', '.cpp', '.hpp', '.java', '.kt', '.swift',
}

IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.svn', '.hg', '.idea', '.vscode', '.venv', 'venv'}


def is_text_file(filepath):
    _, ext = os.path.splitext(filepath)
    return ext.lower() in TEXT_EXTENSIONS


def get_rel_path(root_dir, abs_path):
    return os.path.relpath(abs_path, root_dir).replace('\\', '/')


def pack(source_dir, output_file, include_all=False):
    source_dir = os.path.abspath(source_dir)

    if not os.path.isdir(source_dir):
        print(f"Error: '{source_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    packed_count = 0
    dirs_with_files = set()
    all_dirs = set()

    with open(output_file, 'wb') as out:
        for root, dirs, files in os.walk(source_dir, topdown=True):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            rel_dir = get_rel_path(source_dir, root)

            if rel_dir != '.':
                all_dirs.add(rel_dir)

            for f in sorted(files):
                filepath = os.path.join(root, f)
                rel_path = get_rel_path(source_dir, filepath)

                if not include_all and not is_text_file(filepath):
                    print(f"  [SKIP] {rel_path} (unsupported extension)")
                    continue

                try:
                    with open(filepath, 'rb') as fh:
                        content = fh.read()
                    content.decode('utf-8')
                except (UnicodeDecodeError, OSError) as e:
                    print(f"  [SKIP] {rel_path} ({e})")
                    continue

                parts = rel_path.split('/')
                for i in range(len(parts) - 1):
                    dirs_with_files.add('/'.join(parts[:i + 1]))

                out.write(f"[FILE] {rel_path}\n".encode('utf-8'))
                out.write(f"[SIZE] {len(content)}\n".encode('utf-8'))
                out.write(content)
                packed_count += 1
                print(f"  [PACK] {rel_path} ({len(content)} bytes)")

    empty_dirs = sorted(all_dirs - dirs_with_files)
    if empty_dirs:
        with open(output_file, 'ab') as out:
            for d in empty_dirs:
                out.write(f"[DIR] {d}\n".encode('utf-8'))
                print(f"  [DIR]  {d} (empty)")

    print(f"\nDone. Packed {packed_count} files into '{output_file}'.")


def unpack(input_file, output_dir):
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    count = 0

    with open(input_file, 'rb') as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = line.decode('utf-8').rstrip('\r\n')

            if not line:
                continue

            if line.startswith('[DIR] '):
                rel_path = line[6:]
                target = os.path.join(output_dir, rel_path)
                os.makedirs(target, exist_ok=True)
                print(f"  [DIR]  {rel_path}")

            elif line.startswith('[FILE] '):
                rel_path = line[7:]

                size_line = f.readline()
                if not size_line:
                    print(f"Error: expected [SIZE] for '{rel_path}'", file=sys.stderr)
                    break
                size_line = size_line.decode('utf-8').rstrip('\r\n')

                if not size_line.startswith('[SIZE] '):
                    print(f"Error: expected [SIZE], got '{size_line}'", file=sys.stderr)
                    break

                size = int(size_line[7:])
                content = f.read(size)

                target = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(target), exist_ok=True)

                with open(target, 'wb') as fh:
                    fh.write(content)

                count += 1
                print(f"  [UNPACK] {rel_path} ({size} bytes)")

            else:
                print(f"Warning: unknown marker '{line.split()[0] if ' ' in line else line}'", file=sys.stderr)

    print(f"\nDone. Unpacked {count} files into '{output_dir}'.")


def main():
    parser = argparse.ArgumentParser(description='Pack/unpack directory contents into a single text file.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    p_pack = subparsers.add_parser('pack', help='Pack directory into a file')
    p_pack.add_argument('source_dir', help='Source directory to pack')
    p_pack.add_argument('output_file', help='Output packed file')
    p_pack.add_argument('--all', '-a', action='store_true',
                        help='Include all files (attempt to read as text regardless of extension)')

    p_unpack = subparsers.add_parser('unpack', help='Unpack file into a directory')
    p_unpack.add_argument('input_file', help='Packed file to unpack')
    p_unpack.add_argument('output_dir', help='Output directory')

    args = parser.parse_args()

    if args.command == 'pack':
        pack(args.source_dir, args.output_file, args.all)
    elif args.command == 'unpack':
        unpack(args.input_file, args.output_dir)


if __name__ == '__main__':
    main()
