import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from video_processor import VideoProcessor, ProcessCancelled
import config
import threading
from queue import Queue
import time


class AboutDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"About {config.APP_NAME}")
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)

        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        x = parent.winfo_x() + parent.winfo_width() // 2 - 200
        y = parent.winfo_y() + parent.winfo_height() // 2 - 225
        self.dialog.geometry(f"+{x}+{y}")

        # Set dialog background color
        self.dialog.configure(bg="#f0f0f0")

        self.create_widgets()

    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text=config.APP_NAME,
            font=("Helvetica", 16, "bold"),
            justify="center",
        )
        title_label.pack(pady=(0, 5))

        # Version
        version_label = ttk.Label(
            main_frame,
            text=f"Version {config.APP_VERSION}",
            font=("Helvetica", 10),
            justify="center",
        )
        version_label.pack(pady=(0, 20))

        # Description
        desc_label = ttk.Label(
            main_frame, text=config.APP_DESCRIPTION, wraplength=350, justify="center"
        )
        desc_label.pack(pady=(0, 20))

        # Author info
        author_label = ttk.Label(
            main_frame,
            text=f"Created by: {config.AUTHOR_NAME}",
            font=("Helvetica", 11),
            justify="center",
        )
        author_label.pack(pady=(0, 5))

        # Contact info with clickable links
        email_link = ttk.Label(
            main_frame,
            text=f"Contact: {config.AUTHOR_EMAIL}",
            cursor="hand2",
            foreground="blue",
            justify="center",
        )
        email_link.pack(pady=2)
        email_link.bind(
            "<Button-1>", lambda e: webbrowser.open(f"mailto:{config.AUTHOR_EMAIL}")
        )

        github_link = ttk.Label(
            main_frame,
            text=f"GitHub: {config.GITHUB_URL.split('/')[-1]}",
            cursor="hand2",
            foreground="blue",
            justify="center",
        )
        github_link.pack(pady=2)
        github_link.bind("<Button-1>", lambda e: webbrowser.open(config.GITHUB_URL))

        # website_link = ttk.Label(
        #     main_frame,
        #     text="Website",
        #     cursor="hand2",
        #     foreground="blue",
        #     justify="center",
        # )
        # website_link.pack(pady=2)
        # website_link.bind("<Button-1>", lambda e: webbrowser.open(config.WEBSITE_URL))

        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=20)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10), padx=20, fill="x")

        # Close button
        close_button = ttk.Button(
            button_frame, text="Close", command=self.dialog.destroy, width=15
        )
        close_button.pack(pady=10)

        # Add event binding for Escape key
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

        # Set initial focus to the dialog so Escape works immediately
        self.dialog.focus_set()


class VideoProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Extractor")
        self.root.geometry("600x700")

        # Message queue for thread communication
        self.message_queue = Queue()

        # Variables
        self.video_path = tk.StringVar()
        self.interval = tk.IntVar(value=30)
        self.output_format = tk.StringVar(value="png")
        self.quality = tk.IntVar(value=95)
        self.progress_var = tk.StringVar(value="Ready")
        self.is_processing = False
        self.processor = None

        # Create menu bar
        self.create_menu()

        # Create main widgets
        self.create_widgets()

        # Start queue checking
        self.check_queue()

    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Video...", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        """Show the about dialog"""
        AboutDialog(self.root)

    def create_widgets(self):
        # Set window icon (if you have one)
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Video Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(
            row=0, column=1, padx=5
        )

        # Settings
        settings_frame = ttk.LabelFrame(
            main_frame, text="Processing Settings", padding="10"
        )
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Interval setting
        ttk.Label(settings_frame, text="Frame Interval (seconds):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        interval_spin = ttk.Spinbox(
            settings_frame, from_=1, to=3600, textvariable=self.interval, width=10
        )
        interval_spin.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Output format setting
        ttk.Label(settings_frame, text="Output Format:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.output_format,
            values=["png", "jpg"],
            width=7,
        )
        format_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Quality setting
        ttk.Label(settings_frame, text="Quality (JPEG only):").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        quality_spin = ttk.Spinbox(
            settings_frame, from_=1, to=100, textvariable=self.quality, width=10
        )
        quality_spin.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.progress_bar.grid_remove()  # Hide initially

        # Results Text
        results_frame = ttk.LabelFrame(
            main_frame, text="Processing Results", padding="10"
        )
        results_frame.grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        self.results_text = tk.Text(results_frame, height=15, width=60)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for results
        scrollbar = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.results_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Process button
        self.process_button = ttk.Button(
            buttons_frame, text="Process Video", command=self.start_processing
        )
        self.process_button.grid(row=0, column=0, padx=5)

        # Stop button
        self.stop_button = ttk.Button(
            buttons_frame, text="Stop", command=self.stop_processing, state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*"),
            ),
        )
        if filename:
            self.video_path.set(filename)

    def check_queue(self):
        """Check message queue for updates from processing thread"""
        while True:
            try:
                msg = self.message_queue.get_nowait()

                if msg.get("type") == "progress":
                    self.progress_var.set(msg["message"])
                    self.append_result(msg["message"])
                elif msg.get("type") == "result":
                    self.display_results(msg["results"])
                    self.process_complete()
                elif msg.get("type") == "error":
                    if isinstance(msg["error"], ProcessCancelled):
                        self.handle_cancellation()
                    else:
                        self.handle_error(msg["error"])
                    self.process_complete()

            except Exception:
                break

        # Schedule next queue check
        self.root.after(100, self.check_queue)

    def append_result(self, message):
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)

    def display_results(self, results):
        self.append_result("\nProcessing Summary:")
        self.append_result(
            f"Video Duration: {results['metadata']['duration']:.2f} seconds"
        )
        self.append_result(f"Frames Extracted: {results['analysis']['total_frames']}")
        self.append_result(
            f"Average Frame Size: {results['analysis']['average_file_size']:.2f} MB"
        )
        self.append_result(f"Output Directory: {results['output_directory']}")
        messagebox.showinfo("Success", "Video processing completed successfully!")

    def handle_error(self, error):
        self.progress_var.set("Error occurred!")
        messagebox.showerror("Error", f"Error processing video: {str(error)}")

    def handle_cancellation(self):
        self.progress_var.set("Processing cancelled by user")
        self.append_result("\nProcessing cancelled by user")
        messagebox.showinfo("Cancelled", "Video processing was cancelled")

    def process_complete(self):
        self.is_processing = False
        self.process_button.state(["!disabled"])
        self.stop_button.state(["disabled"])
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.processor = None

    def stop_processing(self):
        """Cancel the current processing operation"""
        if self.processor and self.is_processing:
            self.processor.cancel_processing()
            self.stop_button.state(["disabled"])
            self.progress_var.set("Cancelling...")
            self.append_result("\nCancelling processing...")

    def process_video_thread(self):
        """Video processing function that runs in separate thread"""
        try:
            self.processor = VideoProcessor(self.video_path.get())

            def status_callback(message):
                self.message_queue.put({"type": "progress", "message": message})

            self.processor.print_status = status_callback

            results = self.processor.process_video(
                interval=self.interval.get(),
                output_format=self.output_format.get(),
                quality=self.quality.get(),
            )

            self.message_queue.put({"type": "result", "results": results})

        except Exception as e:
            self.message_queue.put({"type": "error", "error": e})

    def start_processing(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file first!")
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.process_button.state(["disabled"])
        self.stop_button.state(["!disabled"])  # Enable stop button
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set("Starting processing...")

        # Show and start progress bar
        self.progress_bar.grid()
        self.progress_bar.start(10)

        # Start processing thread
        thread = threading.Thread(target=self.process_video_thread)
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    app = VideoProcessorGUI(root)
    icon = tk.PhotoImage(file="./icon.png")
    root.iconphoto(True, icon)
    root.mainloop()


if __name__ == "__main__":
    main()
