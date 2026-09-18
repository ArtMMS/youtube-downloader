# YouTube Downloader
## About the Project

The goal of this project is to develop a desktop application capable of downloading videos and audio from YouTube URLs.

The application will provide a simple and user-friendly interface where users can paste a video link, select the desired download format and save the content locally on their computer.

This project was created both as a software development exercise and as an opportunity to explore topics such as network communication, file management, graphical user interfaces, external tools integration, and application packaging for Windows.

This is a personal project intended for learning and personal use.

---

## Roadmap
* Accept YouTube URLs.
* Allow the user to choose the download location.
* Download audio files (MP3) using the original video title as the filename.
* Download video files (MP4) and select quality.
* Display download progress.
* Provide a basic graphical user interface (GUI).

---

## Programming Language
**Python**

## Planned Libraries
*yt-dlp* – Video and audio downloading engine.
*tkinter* – Graphical user interface (GUI).
*threading* – Background task execution to keep the interface responsive.
*pathlib* – File and directory management.
*json* – Configuration and settings storage.
*logging* – Application logging and debugging.
*ffmpeg* – Audio and video processing, merging, and conversion.
*pyinstaller* – Generation of a standalone .exe file.

---

## FFmpeg Notice

This project requires **FFmpeg** and **FFprobe** for audio extraction, video processing, and merging separate video and audio streams.

When running the application from source, the FFmpeg executables should be available in the project's `ffmpeg` directory:

```text
├── main.py
└── ffmpeg/
    ├── ffmpeg.exe
    ├── ffprobe.exe
    └── ffplay.exe
```

The FFmpeg binaries are **not included in this repository** because they exceed GitHub's file size limits.

For a packaged version of the application, FFmpeg may instead be bundled with the application and extracted to a temporary directory at runtime. The application can then use that temporary directory as the FFmpeg location.

Users running the project from source are therefore responsible for providing a valid FFmpeg installation or placing the required FFmpeg executables in the expected location.
