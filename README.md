# YouTube Downloader

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-green.svg)
![Node.js](https://img.shields.io/badge/Node.js-LTS-brightgreen.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

A YouTube video and audio downloader powered by **yt-dlp**, designed to provide maximum compatibility with YouTube and Windows.

## Features

* Download videos in MP4 format
* Download audio in MP3 format
* Support for age-restricted videos
* Support for YouTube's JavaScript *n-challenge*
* Windows-compatible output (H.264 + AAC)
* Command-line interface and interactive menu

---

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [YouTube Cookies](#youtube-cookies)
* [Diagnostics](#diagnostics)
* [Common Issues](#common-issues)
* [Project Structure](#project-structure)
* [License](#license)

---

## Requirements

| Software     | Purpose                         |
| ------------ | ------------------------------- |
| Python 3.10+ | Run the scripts                 |
| Node.js LTS  | Solve YouTube's n-challenge     |
| FFmpeg       | Merge and convert media streams |

---

## Installation

Install the required dependencies:

```powershell
python -m pip install -U yt-dlp python-certifi-win32
```

Verify your installation:

```powershell
python --version
node --version
ffmpeg -version
python -m yt_dlp --version
```

---

## Usage

Navigate to the project directory:

```powershell
cd "D:\youtube mp4"
```

### Download a Video

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." video
```

### Download Audio (MP3)

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." audio
```

### Download to a Specific Folder

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." video ".\downloads"
```

### Launch the Interactive Menu

```powershell
python downloader.py
```

---

## YouTube Cookies

Cookies are required for age-restricted or authenticated videos.

For proper authentication, the `cookies.txt` file must be exported **immediately after refreshing the YouTube page** so that Google cookies (`SAPISID`, `SID`, etc.) are included along with YouTube cookies.

### Chrome / Edge / Brave

1. Install the **Get cookies.txt LOCALLY** extension
2. Sign in to YouTube
3. Refresh the page (`F5`)
4. Immediately click the extension and select **Export**
5. Choose **Netscape HTTP Cookie Format**
6. Save the file as:

```text
D:\youtube mp4\cookies.txt
```

### Firefox

1. Install the **cookies.txt** extension
2. Sign in to YouTube
3. Refresh the page (`F5`)
4. Immediately export the cookies
5. Save the file as:

```text
D:\youtube mp4\cookies.txt
```

> [!WARNING]
> Never share your `cookies.txt` file.
>
> It contains authentication data that may allow access to your YouTube account.

---

## Diagnostics

### List Available Formats

```powershell
python -m yt_dlp --cookies cookies.txt --list-formats "URL"
```

### Run Tests

```powershell
python -m pytest test_downloader.py -v
```

---

## Common Issues

### Sign in to confirm your age

Your `cookies.txt` file is likely outdated or incomplete.

Solution:

1. Open YouTube
2. Refresh the page (`F5`)
3. Export cookies immediately
4. Replace the existing `cookies.txt`

---

### n challenge solving failed

Node.js is not installed or not detected.

Verify installation:

```powershell
node --version
```

Install the latest LTS version of Node.js if needed.

---

### CERTIFICATE_VERIFY_FAILED

Install the Windows certificate compatibility package:

```powershell
python -m pip install python-certifi-win32
```

---

### Cookie Database Locked (Chrome / Edge)

Chrome and Edge may lock their SQLite cookie database.

Possible solutions:

* Close the browser completely
* Use Firefox
* Export a `cookies.txt` file manually

---

### Audio Not Playing on Windows

Convert the audio track to AAC:

```powershell
ffmpeg -y -i "input.mp4" -c:v copy -c:a aac -b:a 192k "output.mp4"
```

---

## Project Structure

```text
youtube-downloader/
│
├── downloader.py
├── download_direct.py
├── test_downloader.py
├── cookies.txt
└── README.md
```