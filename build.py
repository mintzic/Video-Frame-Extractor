import PyInstaller.__main__
import sys
import os

# Get the directory where build.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run(
    [
        "./src/main.py",  # your main script
        "--name=VideoFrameExtractor",  # name of your exe
        "--windowed",  # prevents console window from appearing
        "--onefile",  # creates a single executable
        f'--icon={os.path.join(current_dir, "./resources/icon.ico")}',  # icon for the exe file
        "--clean",  # clean cache before building
        f'--add-data={os.path.join(current_dir, "./src/config.py")};.',  # include config
        f'--add-data={os.path.join(current_dir, "./src/video_processor.py")};.',  # include video_processor
        f'--add-data={os.path.join(current_dir, "./resources/icon.ico")};.',  # include icon file in the bundle
        "--noconfirm",  # replace output directory without asking
        f'--workpath={os.path.join(current_dir, "build")}',  # work directory
        f'--distpath={os.path.join(current_dir, "dist")}',  # output directory
        f"--specpath={current_dir}",  # spec file directory
    ]
)
