import PyInstaller.__main__
import sys
import os
from scripts.version import VERSION

# Get the directory where build.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create version info file
version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION.replace(".", ", ")}, 0),
    prodvers=({VERSION.replace(".", ", ")}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'mystical.io'),
          StringStruct(u'FileDescription', u'Video Frame Extractor'),
          StringStruct(u'FileVersion', u'{VERSION}'),
          StringStruct(u'InternalName', u'VideoFrameExtractor'),
          StringStruct(u'LegalCopyright', u'(C) 2024 mystical.io. All rights reserved.'),
          StringStruct(u'OriginalFilename', u'VideoFrameExtractor.exe'),
          StringStruct(u'ProductName', u'Video Frame Extractor'),
          StringStruct(u'ProductVersion', u'{VERSION}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

# Write version info to file with UTF-8 encoding
with open("version_info.txt", "w", encoding="utf-8") as f:
    f.write(version_info)

try:
    PyInstaller.__main__.run(
        [
            "src/main.py",  # your main script
            "--name=VideoFrameExtractor",  # name of your exe
            "--windowed",  # prevents console window from appearing
            "--onefile",  # creates a single executable
            f'--icon={os.path.join(current_dir, "resources", "icon.ico")}',  # icon
            f"--version-file=version_info.txt",  # version info
            "--clean",  # clean cache before building
            f'--add-data={os.path.join(current_dir, "src/config.py")};.',  # include config
            f'--add-data={os.path.join(current_dir, "src/video_processor.py")};.',  # include video_processor
            "--noconfirm",  # replace output directory without asking
            f'--workpath={os.path.join(current_dir, "build")}',  # work directory
            f'--distpath={os.path.join(current_dir, "dist")}',  # output directory
            f"--specpath={current_dir}",  # spec file directory
        ]
    )
finally:
    # Clean up version info file
    if os.path.exists("version_info.txt"):
        os.remove("version_info.txt")
