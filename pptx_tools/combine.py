import io
from pathlib import Path

import win32com.client

DIR = Path(r'C:\Users\18317\OneDrive\CXXY\B.课程\大三（上）\继电保护')
files = list(DIR.glob('*.pptx'))

def merge_presentations():
    ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
    prs = ppt_instance.Presentations.open(files[0].as_posix(), True, False, False)

    for file in files[1:]:
        print(f'Combining {file.name}')
        prs.Slides.InsertFromFile(file, prs.Slides.Count)

    prs.SaveAs(DIR / 'combined.pptx')
    prs.Close()


if __name__ == '__main__':
    merge_presentations()
    # working()
