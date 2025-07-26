import os
import subprocess
from pathlib import Path

def separate_audio(input_path, output_dir):
    """
    Separates the input audio file into vocals and accompaniment using Demucs.
    Args:
        input_path (str): Path to the input audio file.
        output_dir (str): Directory to save the separated files.
    Returns:
        str: Path to the accompaniment (karaoke) file.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        'demucs',
        '--two-stems=vocals',
        '--out', output_dir,
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Demucs failed: {result.stderr}")
    song_name = Path(input_path).stem
    karaoke_path = os.path.join(output_dir, 'separated', 'htdemucs', song_name, 'no_vocals.wav')
    return karaoke_path 