import sys, os, youtube_dl, osmosdr, rds, time, threading, pmt, sox
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import pfb

DEBUG_FREQ = 89.0
DEBUG_TRANSMITTER = "Warszawa"

CACHE_FILE="cache"

TUNING_TIME = 10
HACKRF_RELEASE_TIME = 2

RDS_TEXT_FRAGMENT = 'radiomaryja'

RF_GAIN = 30

FREQS = {
    "Warszawa": 89.0,
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
    "Suwalki / Deblin / Ryki" : 107.9,
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


class rds_buffer(gr.sync_block):

    def __init__(self, *args, **kwds):
        gr.sync_block.__init__(
            self,
            name="rds_buffer",
            in_sig=None,
            out_sig=None,
        )
        self.radio_text=''
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg):
        if (pmt.is_tuple(msg)):
            type = pmt.to_long(pmt.tuple_ref(msg, 0))
            message = pmt.symbol_to_string(pmt.tuple_ref(msg, 1))
            if type == 4: #radio_text
                self.radio_text = message


class rds_rx(gr.top_block):

    def __init__(self, rx_freq):
        gr.top_block.__init__(self, "FM RDS receiver and decoder")

        ##################################################
        # Variables
        ##################################################
        self.freq_offset = freq_offset = 250000
        self.freq = freq = rx_freq
        self.samp_rate = samp_rate = 2000000
        self.gain = gain = 20
        self.freq_tune = freq_tune = freq - freq_offset

        ##################################################
        # Blocks
        ##################################################
        self.root_raised_cosine_filter_0 = filter.fir_filter_ccf(2, firdes.root_raised_cosine(
        	1, 19000, 2375, .35, 100))
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
        	  19000/250e3,
                  taps=None,
        	  flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)

        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'hackrf' )
        self.osmosdr_source_0.set_clock_source('gpsdo', 0)
        self.osmosdr_source_0.set_time_source('gpsdo', 0)
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq_tune, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(14, 0)
        self.osmosdr_source_0.set_if_gain(24, 0)
        self.osmosdr_source_0.set_bb_gain(gain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.gr_rds_parser_0 = rds.parser(True, False, 0)
        self.gr_rds_decoder_0 = rds.decoder(False, False)
        self.freq_xlating_fir_filter_xxx_1_0 = filter.freq_xlating_fir_filter_fcc(1, (firdes.low_pass(2500.0,250000,2.6e3,2e3,firdes.WIN_HAMMING)), 57e3, 250000)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (firdes.low_pass(1, samp_rate, 80000, 20000)), freq_offset, samp_rate)
        self.digital_psk_demod_0 = digital.psk.psk_demod(
          constellation_points=2,
          differential=False,
          samples_per_symbol=4,
          excess_bw=0.35,
          phase_bw=6.28/100.0,
          timing_bw=6.28/100.0,
          mod_code="gray",
          verbose=False,
          log=False,
          )
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_char*1, 2)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=samp_rate,
        	audio_decimation=8,
        )

        self.rds_buffer_0 = rds_buffer()

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.gr_rds_decoder_0, 'out'), (self.gr_rds_parser_0, 'in'))
        self.connect((self.analog_wfm_rcv_0, 0), (self.freq_xlating_fir_filter_xxx_1_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.gr_rds_decoder_0, 0))
        self.connect((self.digital_psk_demod_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.digital_psk_demod_0, 0))

        self.msg_connect((self.gr_rds_parser_0, 'out'), (self.rds_buffer_0, 'in'))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_freq_tune(self.freq - self.freq_offset)
        self.rds_buffer_0.radio_text = ''

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, 80000, 20000)))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.osmosdr_source_0.set_bb_gain(self.gain, 0)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.osmosdr_source_0.set_center_freq(self.freq_tune, 0)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.set_freq_tune(self.freq - self.freq_offset)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset)


class fm_tx(gr.top_block):

    def __init__(self, frequency, file, sample_rate):
        gr.top_block.__init__(self, "FM Transmitter")

        ##################################################
        # Variables
        ##################################################
        self.tune_freq = tune_freq = frequency
        self.file_name = file_name = file
        self.samp_rate = samp_rate = sample_rate

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(args="numchan=" + str(1) + " " + 'hackrf')
        self.osmosdr_sink_0.set_clock_source('gpsdo', 0)
        self.osmosdr_sink_0.set_time_source('gpsdo', 0)
        self.osmosdr_sink_0.set_time_now(osmosdr.time_spec_t(time.time()), osmosdr.ALL_MBOARDS)
        self.osmosdr_sink_0.set_sample_rate(16 * samp_rate)
        self.osmosdr_sink_0.set_center_freq(tune_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(RF_GAIN, 0)
        self.osmosdr_sink_0.set_if_gain(0, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(70000, 0)

        self.blocks_wavfile_source_0 = blocks.wavfile_source(file_name, True)
        self.analog_wfm_tx_0 = analog.wfm_tx(
            audio_rate=samp_rate,
            quad_rate=16 * samp_rate,
            tau=50e-6,
            max_dev=50e3,
            fh=-1,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_wfm_tx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.analog_wfm_tx_0, 0))

    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.osmosdr_sink_0.set_center_freq(self.tune_freq, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(16 * self.samp_rate)

    def get_file_name(self):
        return self.file_name

    def set_file_name(self, file_name):
        self.file_name = file_name


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


def receive_rds(receiver):
    receiver.wait()


def download_audio_from_yt(id):
    ydl_options = {
        'format': u'bestaudio/best',
        'outtmpl': u'%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav'
        }]
    }
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download([unicode('https://www.youtube.com/watch?v={}'.format(id))])


def check_frequency(name):
    print('[hackrf_ma_twarz] checking frequency for {} : {} MHz'.format(name, str(FREQS[name])))
    receiver = rds_rx(FREQS[name]*1e6)
    receiver.start()
    receiver_thread = threading.Thread(target=receive_rds, args=(receiver,))
    receiver_thread.start()
    print("[hackrf_ma_twarz] +Receiver thread started")
    time.sleep(TUNING_TIME)
    print("[hackrf_ma_twarz] +Stopping receiver")
    receiver.stop()
    print("[hackrf_ma_twarz] +Waiting for receiver to terminate")
    receiver.wait()
    print("[hackrf_ma_twarz] +Checking captured RDS")
    ret = RDS_TEXT_FRAGMENT in receiver.rds_buffer_0.radio_text
    print("[hackrf_ma_twarz] +Waiting for device to be freed")
    time.sleep(HACKRF_RELEASE_TIME)
    del receiver
    print("[hackrf_ma_twarz] +Receiver object destroyed")
    return ret


def transmit(tx_frequency, source_file, sample_rate):
    print("[hackrf_ma_twarz] Transmitting {} on {} MHz, Ctrl+C to stop".format(source_file, tx_frequency))
    transmitter = fm_tx(tx_frequency*1e6, source_file, sample_rate)
    transmitter.start()
    transmitter.wait()
    print("[hackrf_ma_twarz] +Stopping transmitter")
    transmitter.stop()
    print("[hackrf_ma_twarz] +Waiting for transmitter to terminate")
    transmitter.wait()
    print("[hackrf_ma_twarz] +Waiting for device to be freed")
    time.sleep(HACKRF_RELEASE_TIME)
    del transmitter
    print("[hackrf_ma_twarz] +Transmitter object destroyed")


def check_sample_rate(path):
    return int(sox.file_info.sample_rate(path))


##################################################################

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

if os.path.exists(CACHE_FILE):

    with open(CACHE_FILE, "r") as cache_file:
        found = cache_file.readlines()

    for freq_name in found:
        freq_name = freq_name.strip()

    if len(found) < 1:
        do_scan=True

    else:
        print("[hackrf_ma_twarz] Found cache containg frequencies: {}".format(found))
        answer = str(raw_input("[hackrf_ma_twarz] Type [Y] to do a new scan:"))
        do_scan = answer.lower() in "y"

else:
    do_scan=True

if do_scan:
    for frequency_name in FREQS:
        if check_frequency(frequency_name):
            print("[hackrf_ma_twarz] Found \"{}\" on {} : {}".format(RDS_TEXT_FRAGMENT, frequency_name, FREQS[frequency_name]))
            found.append(frequency_name)

    if len(found) > 0:
        with open(CACHE_FILE, "w") as cache_file:
            cache_file.writelines(found)
            print("[hackrf_ma_twarz] Stored {} in cache.".format(found))

    else:
        print("[hackrf_ma_twarz] No transmitters found, sorry")
        exit(1)

print("[hackrf_ma_twarz] Following frequencies were found:")
frequency_choice = {}

for i in range(0, len(found)):
    frequency_choice[i] = found[i]
    print("[hackrf_ma_twarz]   [{}] {} : {} MHz".format(i, found[i], FREQS[found[i]]))

chosen = -1
while not chosen in range(0, len(found)):
    chosen = int(raw_input("[hackrf_ma_twarz] Please choose one:"))

sample_rate = check_sample_rate(path)

transmit(FREQS[found[chosen]], path, sample_rate)
