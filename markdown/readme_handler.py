"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 29/12/2023
@Description  : generate directory links and recently modified files
"""
import logging
import re
import subprocess
from pathlib import Path


class MarkdownHandler:
    def __init__(self, root_path: str | Path):
        if isinstance(root_path, str):
            root_path = Path(root_path)
        self.root_path = root_path
        if not self.root_path.exists() or not self.root_path.is_dir():
            logging.error(f"ROOT_PATH not found at {self.root_path}")
            raise FileNotFoundError
        self.exclude_dirs = []

    def generate_nav_links_from_dir(
            self,
            output_file: str | Path,
            target_dir: str = 'docs',
            title: str = '## 快捷导航'):
        """
        Generates markdown nav links for all files in target_dir
        """
        tar_path = self.root_path / target_dir
        if not tar_path.exists() or not tar_path.is_dir():
            logging.error(f"TARGET_DIR not found at {tar_path}")
            return
        markdown_links = self._create_links(tar_path)
        self._update_md_content(output_file, '\n'.join(markdown_links), title)

    def generate_recently_modified_from_git(
            self,
            output_file: str | Path,
            num_commits: int = 15,
            target_dir: str = 'docs',
            title: str = '## 最近修改'):
        """
        Generates markdown links for all files in target_dir that have been modified in the last num_commits
        """

        commit_changes = self._get_git_changes(num_commits)
        markdown_content = self._generate_markdown_from_git_changes(
            commit_changes, target_dir)
        self._update_md_content(output_file,markdown_content, title)

    def convert_wiki_links_in_dir(self, ext='.md'):
        """
        Convert wiki-links like [[]] -> standard markdown links []()
        by git changes under root_path
        """
        def convert_wiki_links_in_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            converted_content = self._convert_obsidian_image_and_links_to_standard_md(
                content)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(converted_content)
        pathlist = self.root_path.rglob(f'*{ext}')
        i = 0
        for path in pathlist:
            convert_wiki_links_in_file(path)
            i += 1
        logging.info(f"Converted {i} files in {self.root_path}")

    @staticmethod
    def _convert_obsidian_image_and_links_to_standard_md(content: str):
        obsidian_pattern = r'!\[\[(.+?)\]\]|\[\[(.+?)\]\]'

        def replace_obsidian(match):
            link_text = match.group(1) or match.group(2)
            parts = link_text.split('|')
            link = parts[0].strip().replace(' ', '%20')
            # 保留.md扩展名
            text = parts[1].strip() if len(
                parts) > 1 else link.replace('%20', ' ')

            # 如果是图片链接，添加感叹号前缀
            prefix = '!' if match.group(1) else ''
            return f'{prefix}[{text}]({link})'

        return re.sub(obsidian_pattern, replace_obsidian, content)

    def _create_links(self, path: Path, level: int = 0) -> list:
        links = []
        for item in path.iterdir():
            if (self.exclude_dirs and item.name in self.exclude_dirs):
                continue

            if item.is_dir():
                links.append(f"{'  ' * level}- **{item.name}/:**")
                links.extend(self._create_links(item, level + 1))
            elif item.is_file():
                # Replace spaces with %20 for markdown links
                rel_path = item.relative_to(
                    self.root_path).as_posix().replace(
                    ' ', '%20')

                links.append(
                    f"{'  ' * (level + 1)}- [{item.name}]({rel_path})")
            else:
                logging.warning(f"Unknown file type: {item}")
        return links

    @staticmethod
    def _update_md_content(
            file_path: str | Path,
            new_content: str,
            header_title: str):
        """
        Update the README.md file by replacing content under the specified header title
        with new_content.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with file_path.open('r+', encoding='utf-8') as file:
            lines = file.readlines()
            start_index = None
            end_index = None

            # Find the start and end index for the replacement
            for i, line in enumerate(lines):
                if line.strip() == header_title:
                    start_index = i + 1
                elif start_index is not None and line.startswith('## ') and not line.strip() == header_title:
                    end_index = i
                    break

            # Replace the content if the header title is found
            if start_index is not None:
                end_index = end_index or len(lines)
                lines[start_index:end_index] = [new_content + '\n']

            # Write back to the file
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    def _get_git_changes(self, num_commits: int) -> list:
        # 获取和解析 Git 提交数据
        # 使用唯一分隔符（例如 "|||"）来分隔日期、作者和提交信息
        separator = "|||"
        # 指定 git 命令的工作目录为 self.root_path
        commit_log = subprocess.check_output(
            [
                'git',
                'log',
                f'-{num_commits}',
                f'--pretty=format:%ad{separator}%an{separator}%s',
                '--date=short',
                '--name-status'
            ],
            cwd=self.root_path,  # 设置工作目录为 root_path
            universal_newlines=True
        )

        commit_changes = []
        current_commit_info = []
        for line in commit_log.splitlines():
            if separator in line:
                # 分割日期、作者和提交信息
                parts = line.split(separator)
                date, author, message = parts[0], parts[1], parts[2]
                current_commit_info = {
                    'date': date,
                    'author': author,
                    'message': message,
                    'changes': []}
                commit_changes.append(current_commit_info)
            else:
                match = re.match(
                    r'^([AMDRT])(\d+)?\t(.+?)(?:\t(.+))?$', line)
                if match and current_commit_info:
                    current_commit_info['changes'].append(match.groups())
        return commit_changes

    def _generate_markdown_from_git_changes(
            self, commit_changes: list, target_dir: str) -> str:
        # 定义文件状态的 emoji
        status_emojis = {
            'A': '✨',  # Added
            'M': '🔨',  # Modified
            'D': '🗑️',  # Deleted
            'R': '🚚',  # Renamed
        }
        target_dir = self.root_path / target_dir
        # 生成 Markdown
        markdown_lines = []
        for commit in commit_changes:
            # head of commit msg
            markdown_lines.append(
                f"### {commit['date']} {commit['author']} : {commit['message']}")
            start_index = len(markdown_lines)
            for status, _, path, renamed in commit['changes']:
                if not path.strip('" ').startswith(target_dir.as_posix()):
                    # print(f"Skipping {path}")
                    continue
                emoji = status_emojis.get(status, '')

                # for special case of renamed files, show both old and new
                # paths
                if status == 'R' and renamed:
                    old_path, new_path = path, renamed
                    old_path_name = Path(old_path).name
                    new_path_name = Path(new_path).name
                    rel_path = Path(
                        new_path).as_posix().replace(' ', '%20')
                    linked_path = f"[{new_path_name}]({rel_path})"
                    markdown_lines.append(
                        f"- {emoji} {linked_path} <- {old_path_name}")
                else:
                    rel_path = Path(path).as_posix().replace(' ', '%20')
                    path_name = Path(path).name
                    # no need to link dead files
                    if status != 'D':
                        linked_path = f"[{path_name}]({rel_path})"
                    else:
                        linked_path = path
                    markdown_lines.append(f"- {emoji} {linked_path}")

            if len(markdown_lines) == start_index:
                # clean
                markdown_lines.pop()

        return '\n'.join(markdown_lines)


if __name__ == '__main__':
    pass
    # update_readme_content(new, HEAD_TITLE_2)
