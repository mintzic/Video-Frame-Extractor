import os
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
import datetime
from typing import Tuple, List, Dict
import json


class VideoProcessor:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.output_dir = os.path.join(os.path.dirname(video_path), "processed_output")
        self.print_status = print
        self.should_cancel = False

    def cancel_processing(self):
        """Set flag to cancel processing"""
        self.should_cancel = True

    def check_cancelled(self):
        """Check if processing should be cancelled and raise exception if so"""
        if self.should_cancel:
            raise ProcessCancelled("Processing was cancelled by user")

    def get_video_metadata(self) -> Dict:
        self.check_cancelled()
        with VideoFileClip(self.video_path) as video:
            metadata = {
                "duration": video.duration,
                "fps": video.fps,
                "resolution": video.size,
                "filename": os.path.basename(self.video_path),
                "filesize_mb": os.path.getsize(self.video_path) / (1024 * 1024),
                "format": os.path.splitext(self.video_path)[1],
                "analyzed_at": datetime.datetime.now().isoformat(),
            }
        return metadata

    def format_timestamp(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}-{minutes:02d}-{secs:02d}"

    def extract_frames(
        self, interval: int = 30, output_format: str = "png", quality: int = 95
    ) -> List[Tuple[float, str]]:
        frames_dir = os.path.join(self.output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        frame_info = []

        with VideoFileClip(self.video_path) as video:
            timestamps = range(0, int(video.duration), interval)

            for idx, t in enumerate(timestamps, 1):
                self.check_cancelled()  # Check for cancellation before each frame

                # Extract frame
                frame = video.get_frame(t)

                # Convert to PIL Image
                image = Image.fromarray(np.uint8(frame))

                # Generate safe filename
                timestamp_str = self.format_timestamp(int(t))
                frame_filename = f"frame_{timestamp_str}_{idx:04d}.{output_format}"
                frame_path = os.path.join(frames_dir, frame_filename)

                # Save frame
                if output_format.lower() == "jpg":
                    image.save(frame_path, "JPEG", quality=quality)
                else:
                    image.save(frame_path, "PNG")

                frame_info.append((t, frame_path))
                self.print_status(f"Extracted frame {idx}/{len(timestamps)} at {t}s")

        return frame_info

    def analyze_frames(self, frame_info: List[Tuple[float, str]]) -> Dict:
        self.check_cancelled()
        analysis = {
            "total_frames": len(frame_info),
            "frame_sizes": [],
            "average_file_size": 0,
            "timestamps": [],
        }

        total_size = 0
        for timestamp, frame_path in frame_info:
            self.check_cancelled()
            file_size = os.path.getsize(frame_path) / (1024 * 1024)  # Size in MB
            analysis["frame_sizes"].append(file_size)
            analysis["timestamps"].append(timestamp)
            total_size += file_size

        analysis["average_file_size"] = total_size / len(frame_info)
        return analysis

    def save_report(self, metadata: Dict, analysis: Dict):
        self.check_cancelled()
        report = {
            "video_metadata": metadata,
            "frame_analysis": analysis,
            "processing_timestamp": datetime.datetime.now().isoformat(),
        }

        report_path = os.path.join(self.output_dir, "processing_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)

        self.print_status(f"Processing report saved to {report_path}")

    def process_video(
        self, interval: int = 30, output_format: str = "png", quality: int = 95
    ) -> Dict:
        try:
            # Reset cancel flag at start of processing
            self.should_cancel = False

            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)

            # Get video metadata
            self.print_status("Extracting video metadata...")
            metadata = self.get_video_metadata()

            # Extract frames
            self.print_status("Extracting frames...")
            frame_info = self.extract_frames(
                interval=interval, output_format=output_format, quality=quality
            )

            # Analyze frames
            self.print_status("Analyzing extracted frames...")
            analysis = self.analyze_frames(frame_info)

            # Save report
            self.print_status("Generating processing report...")
            self.save_report(metadata, analysis)

            return {
                "metadata": metadata,
                "analysis": analysis,
                "output_directory": self.output_dir,
                "frame_paths": [path for _, path in frame_info],
            }
        except ProcessCancelled:
            # Clean up any partially processed files
            if os.path.exists(self.output_dir):
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
                try:
                    os.rmdir(self.output_dir)
                except:
                    pass
            raise


class ProcessCancelled(Exception):
    """Exception raised when processing is cancelled by user"""

    pass
