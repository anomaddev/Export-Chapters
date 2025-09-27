# export-chapters

Export MP4/MOV chapter markers into YouTube description–friendly text.

## Features
- Default format: `timestamp - Title` (perfect for YouTube descriptions)
- `--title-first` to switch to `Title - timestamp`
- Output modes (mutually exclusive):
  - default: write to `<input>.yt.txt`
  - `--copy`: copy to clipboard (no file)
  - `--stdout`: print to stdout (no file)
- Cross-platform:
  - Requires `ffprobe` (FFmpeg) in PATH
  - Clipboard on Linux requires `xclip` or `xsel`

## Install (pipx recommended)
```bash
pipx install export-chapters
```

Or locally:
```bash
pipx install .
```

## Usage
```bash
export-chapters MyVideo.mp4            # writes MyVideo.yt.txt
export-chapters MyVideo.mp4 --copy     # copies to clipboard
export-chapters MyVideo.mp4 --stdout   # prints to terminal
export-chapters MyVideo.mp4 --title-first
```

## Prerequisites
- FFmpeg (ffprobe in PATH)
  - macOS: `brew install ffmpeg`
  - Windows: install FFmpeg and add `bin` to PATH
  - Linux: `sudo apt-get install ffmpeg`
- For `--copy` on Linux: `sudo apt-get install xclip` (or `xsel`)

## Sanity check
The formatter should produce:
- 83s -> `1:23`
- 251s -> `4:11`
- 485s -> `8:05`
