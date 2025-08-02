import os
import subprocess
from pathlib import Path
from urllib.parse import quote
import re

def search_youtube(song_name, max_results=5):
    """
    Search YouTube for a song and return multiple result URLs.
    Args:
        song_name (str): Name of the song to search for
        max_results (int): Maximum number of results to return
    Returns:
        list: List of YouTube URLs
    """
    # Try different search strategies
    search_strategies = [
        # Strategy 1: Direct search with audio filter
        f'ytsearch{max_results}:{song_name} audio',
        # Strategy 2: Direct search without audio filter
        f'ytsearch{max_results}:{song_name}',
        # Strategy 3: Search with quotes for exact match
        f'ytsearch{max_results}:"{song_name}"',
        # Strategy 4: Search with music filter
        f'ytsearch{max_results}:{song_name} music'
    ]
    
    for i, search_query in enumerate(search_strategies):
        try:
            cmd = [
                'yt-dlp',
                '--get-id',
                '--playlist-items', f'1-{max_results}',
                search_query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and result.stdout.strip():
                video_ids = result.stdout.strip().split('\n')
                urls = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids if video_id]
                if urls:
                    return urls
            
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            continue
    
    # If all strategies fail, try a simpler approach
    try:
        cmd = [
            'yt-dlp',
            '--get-id',
            '--playlist-items', '1',
            f'ytsearch1:{song_name}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            video_id = result.stdout.strip()
            return [f"https://www.youtube.com/watch?v={video_id}"]
    except:
        pass
    
    raise RuntimeError(f"Could not find any videos for '{song_name}'. Please try a different search term.")

def search_youtube_first(song_name):
    """
    Search YouTube for a song and return the first result URL.
    Args:
        song_name (str): Name of the song to search for
    Returns:
        str: YouTube URL of the first result
    """
    results = search_youtube(song_name, 1)
    return results[0] if results else None

def get_video_details(youtube_url):
    """
    Get video details from YouTube URL.
    Args:
        youtube_url (str): YouTube video URL
    Returns:
        dict: Video details including title, channel, views, duration, thumbnail
    """
    cmd = [
        'yt-dlp',
        '--print', 'title,channel,view_count,duration,thumbnail',
        '--no-playlist',
        youtube_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 5:
                return {
                    'title': lines[0],
                    'channel': lines[1],
                    'views': lines[2],
                    'duration': lines[3],
                    'thumbnail': lines[4],
                    'url': youtube_url
                }
            else:
                raise RuntimeError("Could not parse video details")
        else:
            raise RuntimeError(f"Failed to get video details: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Video details request timed out")
    except Exception as e:
        raise RuntimeError(f"Error getting video details: {str(e)}")

def get_multiple_video_details(youtube_urls, max_results=5):
    """
    Get video details for multiple YouTube URLs.
    Args:
        youtube_urls (list): List of YouTube video URLs
        max_results (int): Maximum number of results to process
    Returns:
        list: List of video details dictionaries
    """
    video_details = []
    
    for i, url in enumerate(youtube_urls[:max_results]):
        try:
            details = get_video_details(url)
            details['index'] = i + 1  # Add position number
            video_details.append(details)
        except Exception as e:
            print(f"Warning: Could not get details for video {i+1}: {str(e)}")
            continue
    
    return video_details

def download_song(song_name, output_dir="downloads"):
    """
    Download a song from YouTube and convert to MP3.
    Args:
        song_name (str): Name of the song to download
        output_dir (str): Directory to save the downloaded file
    Returns:
        str: Path to the downloaded MP3 file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean song name for filename
    safe_name = re.sub(r'[^\w\s-]', '', song_name).strip()
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    output_path = os.path.join(output_dir, f"{safe_name}.mp3")
    
    print(f"Searching for '{song_name}' on YouTube...")
    
    try:
        # Search for the song
        youtube_url = search_youtube_first(song_name)
        if not youtube_url:
            raise RuntimeError("No videos found for the search query")
        print(f"Found: {youtube_url}")
        
        # Download and convert to MP3
        print("Downloading and converting to MP3...")
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',  # Best quality
            '--output', output_path,
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Check if file was actually created
            if os.path.exists(output_path):
                print(f"Successfully downloaded: {output_path}")
                return output_path
            else:
                # Sometimes yt-dlp adds a different extension
                possible_files = list(Path(output_dir).glob(f"{safe_name}.*"))
                if possible_files:
                    actual_file = str(possible_files[0])
                    print(f"Successfully downloaded: {actual_file}")
                    return actual_file
                else:
                    raise RuntimeError("Download completed but file not found")
        else:
            raise RuntimeError(f"Download failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("Download timed out")
    except Exception as e:
        raise RuntimeError(f"Error downloading song: {str(e)}")

def is_yt_dlp_installed():
    """
    Check if yt-dlp is installed and available.
    Returns:
        bool: True if yt-dlp is available
    """
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def test_yt_dlp_search():
    """
    Test if yt-dlp search functionality is working.
    Returns:
        bool: True if search works
    """
    try:
        cmd = ['yt-dlp', '--get-id', 'ytsearch1:test']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0 and result.stdout.strip()
    except:
        return False 