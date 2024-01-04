"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 29/12/2023
@Description  : generate .obsidian folder to  obsidian.zip file
"""
import logging
from pathlib import Path
import zipfile

from markdown.logs.config import setup_logging


def zip_directory(root_path: Path | str):
    root_path = Path(root_path) if isinstance(root_path, str) else root_path
    # Specify the directory you want to zip
    # Change to your specific folder path
    folder_path = Path(root_path) / ".obsidian"

    # Specify the output zip file path
    # Change to your desired output path
    output_path = Path(root_path) / "assets/obsidian.zip"

    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a ZipFile object
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for file in folder_path.rglob("*"):
            if file.is_file():  # Make sure to only add files
                # Create a relative path for files to keep the directory
                # structure
                zipf.write(file, file.relative_to(folder_path))
    logging.info(f"Created zip file at: {output_path}")


if __name__ == "__main__":
    setup_logging()
    # Call the function
    zip_directory("C:/Users/18317/DevSpace/useful_scripts")
