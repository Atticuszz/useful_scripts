"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 31/12/2023
@Description  :
"""
from pathlib import Path

from markdown.readme_handler import MarkdownHandler


def test_generate_nav_links_from_dir():
    handle = MarkdownHandler(root_path=Path(__file__).parents[1])
    handle.generate_nav_links_from_dir(
        output_file=r'C:\Users\18317\python\useful_scripts\tests\README.md',
        target_dir='markdown',
        title='## 快捷导航')

def test_generate_recently_modified_from_git():
    handle = MarkdownHandler(root_path=Path(__file__).parents[1])
    handle.generate_recently_modified_from_git(
        output_file=r'C:\Users\18317\python\useful_scripts\tests\README.md',
        num_commits=15,
        target_dir='markdown',
        title='## 最近修改')

if __name__ == "__main__":
    # test_generate_nav_links_from_dir()
    test_generate_recently_modified_from_git()
    print("test done!")
