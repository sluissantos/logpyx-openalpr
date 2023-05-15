#!/bin/bash

# dependências
sudo apt-get update && apt install -y build-essentail cmake curl git libcurl4-openssl-dev libleptonica-dev liblog4cplus-dev libopencv-dev libtesseract-dev wget tesseract-ocr iproute2 v4l-utils --reinstall libxcb-xinerama0 iputils-ping ffmpeg python3-pip nano
# install OpenALPR
cd /home
sudo git clone https://github.com/sluissantos/logpyx-openalpr.git
cd /home/logpyx-openalpr/openalpr/src
sudo mkdir build
cd /home/logpyx-openalpr/openalpr/src/build
sudo cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..
sudo make
sudo make install
sudo rm -rf /usr/local/lib/python3.5/dist-packages/openalpr*

cd /home/logpyx-openalpr/openalpr/src/bindings/python/
sudo python3 setup.py install 

sudo pip install opencv-python
sudo pip install pytesseract
sudo pip install paho-mqtt