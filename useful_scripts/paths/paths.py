"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 31/12/2023
@Description  :
"""
import json
import os
from pathlib import Path

__all__ = ["print_directory_structure", "find_path"]


def generate_empty_mapping_file(directory_path, mapping_file_path):
    directory = Path(directory_path)
    mapping = {}

    for item in directory.rglob("*"):
        if item.is_file() or item.is_dir():
            mapping[item.name] = ""

    with open(mapping_file_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)


def load_mapping_file(mapping_file_path):
    with open(mapping_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def rename_files_and_folders(directory_path, mapping):
    directory = Path(directory_path)

    for item in directory.rglob("*"):
        if item.name in mapping:
            new_name = mapping[item.name]
            if new_name:
                new_path = item.parent / new_name
                os.rename(item, new_path)
                print(f"Renamed {item} to {new_path}")


def print_directory_structure(startpath: Path | str):
    """
    Prints out the directory structure for the given path in a more structured format,
    excluding specified folders and files.
    """
    if isinstance(startpath, str):
        startpath = Path(startpath)
    excluded = [
        ".git",
        ".idea",
        "__pycache__",
        "node_modules",
        "dist",
        "eslint-internal-rules",
        "demo",
        "example",
        "resource",
    ]
    excluded_paths: list[Path] = [
        p for p in startpath.rglob("*") for ex in excluded if ex in p.as_posix()
    ]

    def recurse_folder(folder, prefix=""):
        # Get all entries in the folder
        entries = sorted(
            [e for e in folder.iterdir() if e not in excluded_paths],
            key=lambda x: (x.is_file(), x.name),
        )
        for index, entry in enumerate(entries):
            connector = "├── " if index < len(entries) - 1 else "└── "
            print(f"{prefix}{connector}{entry.name}")
            if entry.is_dir() and entry not in excluded_paths:
                # If it's a directory and not excluded, recurse into it
                extension = "│   " if index < len(entries) - 1 else "    "
                recurse_folder(entry, prefix=prefix + extension)

    recurse_folder(startpath)


def find_path(path: Path | str):
    if isinstance(path, str):
        path = Path(path)
    import pprint

    i = 0
    paths = []
    for p in path.rglob("*"):
        i += 1
        print(f"check{i}th path")
        if p.name.lower().startswith(".pycharm"):
            paths.append(p)
            break

    paths.sort()
    pprint.pprint(paths)


if __name__ == "__main__":
    print_directory_structure(r"C:\Users\18317\DevSpace\useful_scripts")
    # find_path(r'C:\Users\18317')
