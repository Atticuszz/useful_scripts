from pathlib import Path

import aspose.slides as slides


DIR = Path(r'C:\Users\18317\OneDrive\CXXY\B.课程\大三（上）\继电保护')


def working():
    files = list(DIR.glob('*.pptx'))
    with slides.Presentation(files[0].as_posix()) as pres1:
        for file in files[1:]:
            print(f'Combining {file.name}')
            with slides.Presentation(file.as_posix()) as pres2:
                for slide in pres2.slides:
                    pres1.slides.add_clone(slide)
        pres1.save('combined.pptx',slides.export.SaveFormat.PPTX)


if __name__ == '__main__':
    working()
