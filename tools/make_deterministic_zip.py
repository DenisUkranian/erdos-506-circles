#!/usr/bin/env python3
"""Create a byte-for-byte reproducible ZIP from selected repository paths."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

FIXED_TIME = (2026, 8, 21, 0, 0, 0)


def iter_files(path: Path):
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(p for p in path.rglob("*") if p.is_file())
    else:
        raise FileNotFoundError(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    base = args.base.resolve()
    files: dict[str, Path] = {}
    for item in args.inputs:
        for file_path in iter_files(item.resolve()):
            arcname = file_path.relative_to(base).as_posix()
            files[arcname] = file_path

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for arcname in sorted(files):
            source = files[arcname]
            info = ZipInfo(arcname, FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.flag_bits |= 0x800  # UTF-8 file names
            archive.writestr(info, source.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
