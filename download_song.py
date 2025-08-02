#!/usr/bin/env python3
"""
Standalone script to download songs from YouTube and convert to MP3.
Usage: python download_song.py "Song Name"
"""

import sys
import click
from karaokefy.download import download_song, is_yt_dlp_installed

@click.command()
@click.argument('song_name')
@click.option('--output-dir', default='downloads', help='Directory to save the downloaded file')
def main(song_name, output_dir):
    """Download a song from YouTube and convert to MP3."""
    
    # Check if yt-dlp is installed
    if not is_yt_dlp_installed():
        print("❌ Error: yt-dlp is not installed.")
        print("Please install it first:")
        print("  pip install yt-dlp")
        print("  or")
        print("  brew install yt-dlp")
        sys.exit(1)
    
    try:
        print(f"🎵 Downloading: {song_name}")
        downloaded_file = download_song(song_name, output_dir)
        print(f"✅ Success! Downloaded to: {downloaded_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 