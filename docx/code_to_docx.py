"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 25/12/2023
@Description  :
"""
from docx import Document
from pathlib import Path

# 定义要搜索的目录和文件类型
directories = [
    'C:/Users/18317/react/BoostFace_react_native',
    'C:/Users/18317/python/BoostFace_pyqt6',
    'C:/Users/18317/python/BoostFace_fastapi'
]
file_patterns = ['*.py', '*.tsx']

# 创建Word文档
doc = Document()

for directory in directories:
    # 递归搜索满足条件的文件
    for pattern in file_patterns:
        for file_path in Path(directory).rglob(pattern):
            if 'node_modules' in file_path.parts or 'resource' in file_path.name:
                continue  # 排除node_modules和包含resource的文件
            try:
                # 读取文件内容
                print(f'Processing {file_path}...')
                with file_path.open('r', encoding='utf-8') as file:
                    content = file.read()
                    line_count = content.count('\n') + 1  # 计算行数
                    # 添加文件名和行数
                    doc.add_heading(str(file_path), level=2)
                    doc.add_paragraph(f'Lines: {line_count}')
                    doc.add_paragraph(content)  # 添加文件内容
            except Exception as e:
                print(f'Error processing {file_path}: {e}')

# 保存Word文档
doc.save('code_files.docx')
