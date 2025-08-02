from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
import time
import subprocess
from pathlib import Path
from karaokefy.download import download_song, is_yt_dlp_installed, search_youtube, get_video_details, get_multiple_video_details
from karaokefy.separate import separate_audio

app = Flask(__name__)

# Global variable to store processing status
processing_status = {
    'is_processing': False,
    'current_step': '',
    'progress': 0,
    'result_file': None,
    'error': None,
    'video_details': None,
    'search_results': []
}

def process_song_async(song_name, youtube_url=None):
    """Process song in background thread"""
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['error'] = None
        processing_status['progress'] = 0
        
        # Step 1: Download song
        processing_status['current_step'] = f'Downloading "{song_name}" from YouTube...'
        processing_status['progress'] = 25
        
        if youtube_url:
            # Download from specific URL
            downloaded_file = download_song_from_url(youtube_url, song_name, "downloads")
        else:
            # Download using song name search
            downloaded_file = download_song(song_name, "downloads")
        
        # Step 2: Convert to karaoke
        processing_status['current_step'] = 'Converting to karaoke (removing vocals)...'
        processing_status['progress'] = 75
        
        karaoke_file = separate_audio(downloaded_file, "output")
        
        # Step 3: Complete
        processing_status['current_step'] = 'Complete!'
        processing_status['progress'] = 100
        processing_status['result_file'] = karaoke_file
        
    except Exception as e:
        processing_status['error'] = str(e)
        processing_status['current_step'] = 'Error occurred'
    finally:
        processing_status['is_processing'] = False

def download_song_from_url(youtube_url, song_name, output_dir="downloads"):
    """Download song from specific YouTube URL"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean song name for filename
    import re
    safe_name = re.sub(r'[^\w\s-]', '', song_name).strip()
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    output_path = os.path.join(output_dir, f"{safe_name}.mp3")
    
    print(f"Downloading from URL: {youtube_url}")
    
    try:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_song():
    """Search for a song and return multiple video details for selection"""
    global processing_status
    
    song_name = request.form.get('song_name', '').strip()
    if not song_name:
        return jsonify({'error': 'Please enter a song name'})
    
    # Check if yt-dlp is installed
    if not is_yt_dlp_installed():
        return jsonify({'error': 'yt-dlp is not installed. Please install it first.'})
    
    try:
        # Search for multiple videos
        youtube_urls = search_youtube(song_name, max_results=5)
        
        if not youtube_urls:
            return jsonify({'error': 'No videos found for your search query'})
        
        # Get details for all videos
        video_details_list = get_multiple_video_details(youtube_urls, max_results=5)
        
        if not video_details_list:
            return jsonify({'error': 'Could not retrieve video details'})
        
        # Store search results for later use
        processing_status['search_results'] = video_details_list
        
        return jsonify({
            'success': True,
            'search_results': video_details_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'})

@app.route('/process', methods=['POST'])
def process_song():
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({'error': 'Already processing a song. Please wait.'})
    
    song_name = request.form.get('song_name', '').strip()
    video_index = request.form.get('video_index', '').strip()
    
    if not song_name:
        return jsonify({'error': 'Please enter a song name'})
    
    if not video_index:
        return jsonify({'error': 'Please select a video'})
    
    # Check if yt-dlp is installed
    if not is_yt_dlp_installed():
        return jsonify({'error': 'yt-dlp is not installed. Please install it first.'})
    
    try:
        # Get the selected video from search results
        video_index = int(video_index) - 1  # Convert to 0-based index
        if video_index < 0 or video_index >= len(processing_status['search_results']):
            return jsonify({'error': 'Invalid video selection'})
        
        selected_video = processing_status['search_results'][video_index]
        youtube_url = selected_video['url']
        
        # Store selected video details
        processing_status['video_details'] = selected_video
        
        # Start processing in background thread
        thread = threading.Thread(target=process_song_async, args=(song_name, youtube_url))
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Processing started'})
        
    except (ValueError, IndexError) as e:
        return jsonify({'error': 'Invalid video selection'})
    except Exception as e:
        return jsonify({'error': f'Error starting processing: {str(e)}'})

@app.route('/status')
def get_status():
    return jsonify(processing_status)

@app.route('/download/<filename>')
def download_file(filename):
    # Security: only allow downloading from output directory
    file_path = os.path.join('output', 'htdemucs', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8080) 