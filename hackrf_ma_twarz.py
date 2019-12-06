from __future__ import unicode_literals
import sys, os, youtube_dl, rds

RDS_TEXT_FRAGMENT_LC = 'maryja'

FREQS = {
    "Biala Podlaska" : 87.8,
    "Nowy Targ" : 95.5,
    "Bialystok / Drawsko Pom." : 104.7,
    "Bielsk Podlaski" : 102.0,
    "Olkusz / Kedzierzyn Koz." : 104.6,
    "Bielsko-Biala / Mragowo" : 88.4,
    "Olsztyn / Siedlce losice" : 107.7,
    "Bogatynia" : 100.3,
    "Opole" : 99.9,
    "Brzesko / Wolsztyn" : 98.7,
    "Ostroleka / Szczecinek" : 95.0,
    "Bydgoszcz / Slupsk" : 88.5,
    "Bytow" : 90.4,
    "Ostrow Wlkp." : 88.2,
    "Chelm / Kluczbork" : 102.8,
    "Torun / Krosno / Parczew / Glogow" : 100.6,
    "Lublin / Ciechanowiec" : 97.0,
    "Kielce / Pelczyce" : 107.2,
    "Ciechanow" : 91.8,
    "Czersk" : 101.4,
    "Piotrkow Tryb." : 95.7,
    "Suwalki / Deblin Ryki" : 107.9,
    "Szczecin / Pisz" : 101.6,
    "Dolsk / swiecie" : 104.0,
    "Plock / Sierpc / Klodzko / Lezajsk" : 106.3,
    "Plonsk" : 105.3,
    "Elblag" : 104.2,
    "Poznan" : 106.8,
    "Elk / Przemysl / Konin" : 105.1,
    "Przasnysz / Grojec" : 99.8,
    "Gdynia / Lubaczow" : 102.3,
    "Gdansk / Wroclaw" : 88.9,
    "Rabka" : 100.7,
    "Gizycko" : 100.2,
    "Raciborz / Kalwaria Zebrz." : 94.3,
    "Radom" : 94.2,
    "Gniezno / Skierniewice" : 95.4,
    "Radomsko" : 90.2,
    "Gorzow Wlkp." : 98.8,
    "Wlodawa / Rosko" : 104.5,
    "Rzeszow / Wloclawek" : 100.9,
    "Gryfice" : 102.9,
    "Siedlce" : 97.8,
    "Hrubieszow" : 95.8,
    "Ilawa" : 96.9,
    "Sieradz / Luban" : 95.2,
    "Jastrzebie Zdr." : 102.5,
    "Jelenia Gora / Nysa / Ostrow Maz. / Pila / Wysoka Wies" : 100.4,
    "Slubice" : 92.3,
    "Jemiolow / Kolobrzeg" : 100.0,
    "Kalisz" : 105.6,
    "Stalowa Wola" : 104.4,
    "Stargard Szcz." : 89.4,
    "Katowice" : 103.7,
    "Starogard Gd." : 87.6,
    "Szymbark" : 102.4,
    "Swinoujscie" : 87.7,
    "Tarnow" : 102.6,
    "Koszalin / Walbrzych" : 107.4,
    "Tarnobrzeg" : 94.4,
    "Koszecin" : 107.0,
    "Koscierzyna / Skorzewo" : 96.0,
    "Trzcinsko Zdroj" : 103.5,
    "Krakow" : 90.6,
    "Ustron" : 93.9,
    "Krasnik" : 98.0,
    "Ustrzyki Dolne" : 94.5,
    "Krynica / Wladyslawowo" : 93.1,
    "Warszawa" : 89.0,
    "Kudowa Zdroj" : 90.1,
    "Wagrowiec" : 88.7,
    "Kutno" : 88.3,
    "Wejherowo" : 89.7,
    "Lodz / Kwidzyn" : 87.9,
    "Wielun" : 105.2,
    "Wyszkow / Lebork" : 92.7,
    "Lidzbark Warm." : 106.2,
    "Lipiany" : 99.5,
    "Lomza" : 101.3,
    "Wegrow" : 89.5,
    "Zamosc" : 96.5,
    "Miastko" : 96.8,
    "Zielona Gora" : 90.3,
    "Mielec" : 89.8,
    "Zlotow" : 101.1,
    "Zakopane" : 96.3,
    "Nowa Ruda" : 99.1,
    "Zagan" : 101.2,
    "Nowy Sacz" : 95.1
}

def print_usage_and_exit():
    print('I am not responsible for using this code to break any local and/or international laws. Use at your own risk.')
    print('This script finds the local Radio Maryja frequency and broadcasts a chosen wave file or youtube audio on it.')
    print('Supports only Polish FM radio frequencies (for now)')
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

def check_frequency(name):
    print('[hackrf_ma_twarz] checking frequency for {} : {} MHz'.format(name, str(FREQS[name])))
    rds.rdspanel
    return False

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

found = []

for frequency_name in FREQS:
    if check_frequency(frequency_name):
        found.append(frequency_name)

