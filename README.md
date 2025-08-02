# Karaokefy

A tool to generate karaoke-ready versions of songs by extracting vocals and instrumentals.

## Features
- 🎵 **Download songs from YouTube** and convert to MP3
- 🎤 **Extract vocals and instrumentals** using Demucs (state-of-the-art AI)
- 🌐 **Web interface** for easy use
- 📱 **CLI interface** for power users
- ⚡ **High-quality separation** using advanced AI models

## Setup

1. **Install Python 3.8+** and [ffmpeg](https://ffmpeg.org/download.html) (required by Demucs)
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### 🌐 Web Interface (Recommended)

Start the web application:
```sh
python start_web.py
```

Then open your browser and go to: **http://localhost:8080**

1. Enter a song name (e.g., "Shape of You Ed Sheeran")
2. Click "Create Karaoke Version"
3. Wait for processing (download + vocal separation)
4. Download your karaoke version!

### 📱 CLI Interface

**Download a song and create karaoke:**
```sh
# Download a song from YouTube
python download_song.py "Shape of You Ed Sheeran"

# Create karaoke version from existing file
python cli.py path/to/song.mp3 --output-dir output
```

The karaoke version will be saved in `output/separated/htdemucs/{song_name}/no_vocals.wav`.

## How It Works

1. **YouTube Search**: Uses yt-dlp to search and download songs from YouTube
2. **Audio Conversion**: Converts to high-quality MP3
3. **Vocal Separation**: Uses Demucs AI to separate vocals from instrumentals
4. **Karaoke Output**: Provides clean instrumental version for karaoke

## Requirements

- Python 3.8+
- ffmpeg
- Internet connection (for YouTube downloads)
- ~2GB RAM (for AI processing)

---

Future features: synced lyrics, vocal range filtering, and more!
