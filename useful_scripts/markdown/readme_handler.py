# -*- coding: utf-8 -*-
"""
@Organization : SupaVision
@Author       : 18317
@Date Created : 29/12/2023
@Description  : Refactored script to generate directory links and recently modified files.
"""
import logging
import re
import subprocess
from pathlib import Path


class GitHandler:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_recent_changes(self, num_commits: int) -> list:
        separator = "|||"
        commit_log = subprocess.check_output(
            [
                "git",
                "log",
                f"-{num_commits}",
                f"--pretty=format:%ad{separator}%an{separator}%s",
                "--date=short",
                "--name-status",
            ],
            cwd=self.repo_path,
            universal_newlines=True,
        )
        return self.parse_commit_log(commit_log, separator)

    @staticmethod
    def parse_commit_log(commit_log: str, separator: str) -> list:
        commit_changes = []
        current_commit_info = []
        for line in commit_log.splitlines():
            if separator in line:
                date, author, message = line.split(separator)
                current_commit_info = {
                    "date": date,
                    "author": author,
                    "message": message,
                    "changes": [],
                }
                commit_changes.append(current_commit_info)
            else:
                match = re.match(r"^([AMDRT])(\d+)?\t(.+?)(?:\t(.+))?$", line)
                if match and current_commit_info:
                    current_commit_info["changes"].append(match.groups())
        return commit_changes


class MarkdownFormatter:
    @staticmethod
    def convert_links(content: str) -> str:
        """
        Convert Obsidian-style links to Markdown-style links.
        """
        obsidian_pattern = r"!\[\[(.+?)\]\]|\[\[(.+?)\]\]"

        def replace_obsidian(match):
            link_text = match.group(1) or match.group(2)
            parts = link_text.split("|")
            link = parts[0].strip().replace(" ", "%20")
            text = parts[1].strip() if len(parts) > 1 else link.replace("%20", " ")
            prefix = "!" if match.group(1) else ""
            return f"{prefix}[{text}]({link})"

        return re.sub(obsidian_pattern, replace_obsidian, content)

    @staticmethod
    def generate_link(rel_path: Path, *, name: str = "", prefix: str = "") -> str:
        """
        Generate a markdown link with the given relative path and name.
        """
        name = rel_path.name if not name else name
        rel_path = rel_path.as_posix().replace(" ", "%20")
        return f"[{name}]({prefix+rel_path})"


class MarkdownHandler:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.git_handler = GitHandler(root_path)
        self.markdown_formatter = MarkdownFormatter()

    def _calculate_relative_depth(self, output_file: Path) -> int:
        depth = 0
        parent = output_file.parent
        while parent != self.root_path and parent != parent.parent:
            depth += 1
            parent = parent.parent
        return depth

    def _check_path(self, path: Path | str):
        if not path.exists():
            raise FileNotFoundError(f"{path} not found!")

    def _create_links(self, output_file: Path, path: Path, level: int = 0) -> list:
        links = []
        depth = self._calculate_relative_depth(output_file)
        prefix = "../" * depth
        for item in path.iterdir():
            if item.is_dir():
                links.append(f"{'  ' * level}- **{item.name}/:**")
                links.extend(self._create_links(output_file, item, level + 1))
            elif item.is_file():
                rel_path = item.relative_to(self.root_path)
                links.append(
                    f"{'  ' * (level + 1)}- {self.markdown_formatter.generate_link(rel_path, prefix=prefix)}"
                )
        return links

    def generate_nav_links_from_dir(
        self, output_file: Path | str, target_dir: str, title: str
    ):
        """
        Generate navigation links from the target directory.
        :param output_file:
        :param target_dir:
        :param title:
        """
        output_file = Path(output_file) if isinstance(output_file, str) else output_file
        tar_path = self.root_path / target_dir
        self._check_path(tar_path)
        self._check_path(output_file)
        markdown_links = self._create_links(output_file, tar_path)
        self._update_md_content(output_file, "\n".join(markdown_links), title)

    def generate_recently_modified_from_git(
        self, output_file: Path | str, num_commits: int, target_dir: str, title: str
    ):
        """
        Generate recently modified files from git changes under the target directory.
        :param output_file:
        :param num_commits:
        :param target_dir:
        :param title:
        """
        output_file = Path(output_file) if isinstance(output_file, str) else output_file
        tar_path = self.root_path / target_dir
        self._check_path(tar_path)
        self._check_path(output_file)
        commit_changes = self.git_handler.get_recent_changes(num_commits)
        # logging.info(f"Found {len(commit_changes)} commits")
        # logging.info(f"git log: {commit_changes}")
        markdown_content = self._generate_markdown_from_git_changes(
            output_file, commit_changes, target_dir
        )
        # logging.info(f"markdown content: {markdown_content}")
        self._update_md_content(output_file, markdown_content, title)

    def convert_wiki_links_in_dir(self, ext=".md"):
        """
        Convert wiki-links like [[]] -> standard markdown links []()
        by git changes under root_path.
        """
        pathlist = self.root_path.rglob(f"*{ext}")
        for path in pathlist:
            self._convert_wiki_links_in_file(path)

    def _convert_wiki_links_in_file(self, file_path: Path):
        """
        Convert wiki-links in a single file to standard markdown links.
        """
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()

        converted_content = self.markdown_formatter.convert_links(content)

        with file_path.open("w", encoding="utf-8") as file:
            file.write(converted_content)

        logging.info(f"Converted links in {file_path}")

    def _update_md_content(self, file_path: Path, new_content: str, header_title: str):
        """
        Update the markdown file by replacing content under the specified header title
        with new_content.
        """
        with file_path.open("r+", encoding="utf-8") as file:
            lines = file.readlines()
            start_index = None
            end_index = None

            # Find the start and end index for the replacement
            for i, line in enumerate(lines):
                if line.strip() == header_title:
                    start_index = i + 1
                elif (
                    start_index is not None
                    and line.startswith("## ")
                    and not line.strip() == header_title
                ):
                    end_index = i
                    break

            # Replace the content if the header title is found
            if start_index is not None:
                end_index = end_index or len(lines)
                lines[start_index:end_index] = [new_content + "\n"]

            # Write back to the file
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    def _generate_markdown_from_git_changes(
        self, output_file: Path, commit_changes: list, target_dir: str
    ) -> str:
        status_emojis = {
            "A": "✨",  # Added
            "M": "🔨",  # Modified
            "D": "🗑️",  # Deleted
            "R": "🚚",  # Renamed
        }
        markdown_lines = []
        depth = self._calculate_relative_depth(output_file)
        prefix = "../" * depth
        target_dir = Path(target_dir)
        logging.info(f"target_dir: {target_dir}")
        for commit in commit_changes:
            markdown_lines.append(
                f"### {commit['date']} by {commit['author']} - {commit['message']}"
            )
            before = len(markdown_lines)
            for change in commit["changes"]:
                status, _, file_path, renamed = change
                full_path = self.root_path / file_path
                emoji = status_emojis.get(status, "")
                rel_path = full_path.relative_to(self.root_path)

                # Handle renamed files
                if status == "R" and renamed:
                    rel_renamed = Path(renamed)
                    if not rel_renamed.exists():
                        logging.warning(f"Skipping {rel_renamed} for not existing")
                        continue
                    markdown_lines.append(
                        f"- {emoji} {self.markdown_formatter.generate_link(rel_renamed, prefix=prefix)} <- {full_path.name}"
                    )
                else:
                    if (
                        not full_path.exists()
                        or not full_path.is_file()
                        or full_path.relative_to(self.root_path).parts[0]
                        != target_dir.parts[0]
                    ):
                        # check if the file is in the target directory
                        logging.warning(f"Skipping {full_path} for not in {target_dir}")
                        continue

                    # No need to link deleted files
                    if status != "D":
                        linked_path = self.markdown_formatter.generate_link(
                            rel_path, prefix=prefix
                        )
                    else:
                        linked_path = rel_path.name
                    markdown_lines.append(f"- {emoji} {linked_path}")
            if len(markdown_lines) == before:
                markdown_lines.pop()
        return "\n".join(markdown_lines)


if __name__ == "__main__":
    # Example usage:
    root_dir = Path("/path/to/your/project")
    output_md = root_dir / "README.md"
    handler = MarkdownHandler(root_dir)
    handler.generate_nav_links_from_dir(output_md, "docs", "## Quick Navigation")
    handler.generate_recently_modified_from_git(
        output_md, 10, "docs", "## Recently Modified"
    )
