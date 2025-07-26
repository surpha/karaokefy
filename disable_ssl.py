import ssl
import urllib.request
import subprocess
import sys

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Run demucs command
cmd = [
    'demucs',
    '--two-stems=vocals',
    '--out', 'output',
    '/Users/surajphalod/Developer/karaokefy/sample_audios/O Majhi Re Apna Kinara Khushboo 320 Kbps.mp3'
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode) 