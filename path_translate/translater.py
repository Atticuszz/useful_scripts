import json
import os
from pathlib import Path


def generate_empty_mapping_file(directory_path, mapping_file_path):
    directory = Path(directory_path)
    mapping = {}

    for item in directory.rglob("*"):
        if item.is_file() or item.is_dir():
            mapping[item.name] = ""

    with open(mapping_file_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)


def load_mapping_file(mapping_file_path):
    with open(mapping_file_path, 'r', encoding='utf-8') as f:
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


if __name__ == "__main__":
    directory_path = Path("C:\\Users\\18317\\OneDrive\\c++\\Wangdao-Data-Structures-code")
    mapping_file_path = Path().cwd() / "mapping.json"

    if not mapping_file_path.is_dir() or not mapping_file_path.is_file():
        generate_empty_mapping_file(directory_path, mapping_file_path)
        print(f"Empty mapping file generated at {mapping_file_path}")
    else:
        mapping = load_mapping_file(mapping_file_path)
        rename_files_and_folders(directory_path, mapping)
        mapping_file_path.unlink()
        print("Renaming completed. Mapping file has been deleted.")
