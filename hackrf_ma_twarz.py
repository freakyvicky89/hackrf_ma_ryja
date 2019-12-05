from __future__ import unicode_literals
import sys, os, youtube_dl
from gnuradio import gr, blocks

def print_usage_and_exit():
    print('USAGE:')
    print('  hackrf_ma_twarz.py *what*')
    print('WHERE:')
    print('  what - filename of wave file (without .wav extension)')
    print('         OR youtube video id (https://www.youtube.com/watch?v=*this part*)')
    exit(1)

def download_audio_from_yt(id):
    ydl_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav'
        }]
    }
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download(['https://www.youtube.com/watch?v={}'.format(id)])

if len(sys.argv) < 2:
    print_usage_and_exit()

what = str(sys.argv[1])
path = "{}.wav".format(what)

if not os.path.exists(path):
    print('[hackrf_ma_twarz] {} not found, downloading video {} from youtube'.format(path, what))
    try:
        download_audio_from_yt(what)
    except:
        print_usage_and_exit()


