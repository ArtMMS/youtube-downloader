import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from pathlib import Path

import json
import sys
import threading

import yt_dlp

if getattr(sys, "frozen", False):
    project_folder = Path(sys.executable).parent
else:
    project_folder = Path(__file__).parent

default_download_folder = project_folder / "downloads"

# File where the user's settings are stored
settings_file = project_folder / "settings.json"


def load_settings():
    try:
        with open(settings_file, "r", encoding="utf-8") as file:
            settings = json.load(file)

        if isinstance(settings, dict):
            return settings

    except (OSError, ValueError):
        pass

    return {}


def save_settings(settings):
    try:
        with open(settings_file, "w", encoding="utf-8") as file:
            json.dump(
                settings,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError:
        pass


def load_download_folder():
    saved_folder = load_settings().get("download_folder")

    if saved_folder:
        saved_path = Path(saved_folder)

        # Only use the saved folder if it still exists
        if saved_path.is_dir():
            return saved_path

    default_download_folder.mkdir(exist_ok=True)
    return default_download_folder


download_folder = load_download_folder()

# Folder containing ffmpeg.exe and ffprobe.exe
ffmpeg_folder = project_folder / "ffmpeg"


def is_youtube_url(url):
    return (
        "youtube.com" in url
        or "youtu.be" in url
    )


def update_progress(data):
    if data["status"] == "downloading":
        downloaded = data.get("downloaded_bytes", 0)
        total = data.get("total_bytes")

        if total:
            percentage = downloaded / total * 100

            root.after(
                0,
                lambda: progress_bar.config(
                    value=percentage
                )
            )

            root.after(
                0,
                lambda: progress_label.config(
                    text=f"Downloading... {percentage:.1f}%"
                )
            )

    elif data["status"] == "finished":
        root.after(
            0,
            lambda: progress_bar.config(
                value=100
            )
        )

        root.after(
            0,
            lambda: progress_label.config(
                text="Processing..."
            )
        )


def download_mp3():
    url = url_entry.get().strip()

    if not is_youtube_url(url):
        messagebox.showerror(
            "Error",
            "Please enter a valid YouTube URL."
        )
        return

    mp3_button.config(state=tk.DISABLED)
    mp4_button.config(state=tk.DISABLED)

    progress_bar["value"] = 0
    progress_label.config(
        text="Starting download..."
    )

    thread = threading.Thread(
        target=download_mp3_thread,
        args=(url,),
        daemon=True
    )

    thread.start()


def download_mp3_thread(url):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "ffmpeg_location": str(ffmpeg_folder),
            "outtmpl": str(
                download_folder /
                "%(title)s.%(ext)s"
            ),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ],
            "progress_hooks": [
                update_progress
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        root.after(
            0,
            download_finished
        )

    except Exception as error:
        root.after(
            0,
            lambda: download_error(error)
        )


def confirm_exit():
    answer = messagebox.askyesno(
        "Exit",
        "Are you sure you want to close the application?"
    )

    if answer:
        root.destroy()


def get_video_qualities(url):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            url,
            download=False
        )

    qualities = set()

    for format_info in info.get("formats", []):
        height = format_info.get("height")

        if height:
            qualities.add(height)

    return sorted(qualities)


def download_mp4():
    url = url_entry.get().strip()

    if not is_youtube_url(url):
        messagebox.showerror(
            "Error",
            "Please enter a valid YouTube URL."
        )
        return

    try:
        qualities = get_video_qualities(url)

        if not qualities:
            messagebox.showerror(
                "Error",
                "No video qualities were found."
            )
            return

        quality_window = tk.Toplevel(root)
        quality_window.title("Select Quality")
        quality_window.geometry("300x180")

        tk.Label(
            quality_window,
            text="Select video quality:"
        ).pack(pady=10)

        quality_values = [
            f"{quality}p"
            for quality in qualities
        ]

        quality_combobox = ttk.Combobox(
            quality_window,
            values=quality_values,
            state="readonly"
        )

        quality_combobox.pack(pady=5)

        quality_combobox.current(
            len(quality_values) - 1
        )

        def start_download():
            selected_quality = quality_combobox.get()

            if not selected_quality:
                return

            height = int(
                selected_quality.replace("p", "")
            )

            quality_window.destroy()

            mp3_button.config(state=tk.DISABLED)
            mp4_button.config(state=tk.DISABLED)

            progress_bar["value"] = 0
            progress_label.config(
                text="Starting download..."
            )

            thread = threading.Thread(
                target=download_mp4_thread,
                args=(url, height),
                daemon=True
            )

            thread.start()

        tk.Button(
            quality_window,
            text="Download",
            command=start_download
        ).pack(pady=15)

    except Exception as error:
        messagebox.showerror(
            "Error",
            str(error)
        )


def download_mp4_thread(url, height):
    try:
        ydl_opts = {
            "format": (
                f"bestvideo[height<={height}]"
                f"+bestaudio/best[height<={height}]"
            ),
            "noplaylist": True,
            "ffmpeg_location": str(ffmpeg_folder),
            "outtmpl": str(
                download_folder /
                "%(title)s.%(ext)s"
            ),
            "merge_output_format": "mp4",
            "progress_hooks": [
                update_progress
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        root.after(
            0,
            download_finished
        )

    except Exception as error:
        root.after(
            0,
            lambda: download_error(error)
        )


def download_finished():
    progress_bar["value"] = 100
    progress_label.config(
        text="Download completed!"
    )

    mp3_button.config(
        state=tk.NORMAL
    )

    mp4_button.config(
        state=tk.NORMAL
    )

    messagebox.showinfo(
        "Success",
        "Download completed."
    )


def download_error(error):
    progress_label.config(
        text="Download failed."
    )

    progress_bar["value"] = 0

    mp3_button.config(
        state=tk.NORMAL
    )

    mp4_button.config(
        state=tk.NORMAL
    )

    messagebox.showerror(
        "Download Error",
        str(error)
    )


def choose_folder():
    global download_folder

    selected_folder = filedialog.askdirectory(
        initialdir=download_folder
    )

    if selected_folder:
        download_folder = Path(selected_folder)

        settings = load_settings()
        settings["download_folder"] = str(download_folder)
        save_settings(settings)

        folder_label.config(
            text=f"Download Folder: {download_folder}"
        )


def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()

        url_entry.delete(
            0,
            tk.END
        )

        url_entry.insert(
            0,
            clipboard_text
        )

    except tk.TclError:
        pass


def show_context_menu(event):
    context_menu.tk_popup(
        event.x_root,
        event.y_root
    )


def paste_from_menu():
    paste_from_clipboard()


# Main Window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("700x300")

root.protocol(
    "WM_DELETE_WINDOW",
    confirm_exit
)

root.bind(
    "<Escape>",
    lambda event: confirm_exit()
)

# Set application icon
root.iconbitmap("youtube_icon.ico")

# Title
title_label = tk.Label(
    root,
    text="YouTube Downloader",
    font=("Arial", 14)
)

title_label.pack(pady=10)


# URL Area
url_frame = tk.Frame(root)
url_frame.pack(pady=5)

url_entry = tk.Entry(
    url_frame,
    width=70
)

url_entry.pack(
    side=tk.LEFT,
    padx=(0, 5)
)

paste_button = tk.Button(
    url_frame,
    text="Paste",
    command=paste_from_clipboard
)

paste_button.pack(
    side=tk.LEFT
)


# Right Click Menu
context_menu = tk.Menu(
    root,
    tearoff=0
)

context_menu.add_command(
    label="Paste",
    command=paste_from_menu
)

url_entry.bind(
    "<Button-3>",
    show_context_menu
)


# Download Folder
folder_label = tk.Label(
    root,
    text=f"Download Folder: {download_folder}"
)

folder_label.pack(pady=10)

folder_button = tk.Button(
    root,
    text="Choose Folder",
    command=choose_folder
)

folder_button.pack(pady=5)


# Progress
progress_label = tk.Label(
    root,
    text="Ready"
)

progress_label.pack(pady=(10, 5))


progress_bar = ttk.Progressbar(
    root,
    orient="horizontal",
    length=500,
    mode="determinate",
    maximum=100
)

progress_bar.pack()


# Download Buttons
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=15)

mp3_button = tk.Button(
    buttons_frame,
    text="Download MP3",
    command=download_mp3
)

mp3_button.pack(
    side=tk.LEFT,
    padx=5
)

mp4_button = tk.Button(
    buttons_frame,
    text="Download MP4",
    command=download_mp4
)

mp4_button.pack(
    side=tk.LEFT,
    padx=5
)


root.mainloop()