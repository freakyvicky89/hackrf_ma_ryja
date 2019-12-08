# hackrf_ma_twarz
I am not responsible for using this code to break any local and/or international laws. Use at your own risk.
This script finds the local Radio Maryja frequency and broadcasts a chosen wave file or youtube audio on it.
Supports only Polish FM radio frequencies (for now)
# how to install on ubuntu or mint or raspbian:
* open terminal and type these commands:
-     sudo apt install git
-     git clone https://github.com/freakyvicky89/hackrf_ma_twarz.git
-     cd hackrf_ma_twarz
-     chmod +x install_deps_ubuntu.sh
-     ./install_deps_ubuntu.sh
* you will be prompted for your password
# how to run:
* open terminal and type:
-     python hackrf_ma_twarz.py [what]
* where [what] = filename of wave file (without .wav extension) OR youtube video id (https://www.youtube.com/watch?v= *this part* )