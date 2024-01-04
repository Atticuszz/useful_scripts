# useful_scripts/main.py

import argparse
from useful_scripts.markdown.main import print_help as markdown_help

# 导入其他模块 ...


def main():
    parser = argparse.ArgumentParser(description="Helper Tool for Useful Scripts")
    parser.add_argument(
        "--list", action="store_true", help="List all available module commands"
    )
    args = parser.parse_args()

    if args.list:
        print("Available module commands:")
        print("\nMarkdown module:")
        markdown_help()
        # ... 调用其他模块的 print_help 函数 ...


if __name__ == "__main__":
    main()
