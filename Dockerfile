FROM ubuntu:20.04

# Install prerequisites
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    libcurl4-openssl-dev \
    libleptonica-dev \
    liblog4cplus-dev \
    libopencv-dev \
    libtesseract-dev \
    wget \
    tesseract-ocr \
    python3-pip \
    nano \
    iproute2 \
    v4l-utils \
    --reinstall libxcb-xinerama0 \
    iputils-ping \
    ffmpeg


WORKDIR /home
RUN git clone https://github.com/sluissantos/logpyx-openalpr.git /home/logpyx-openalpr

WORKDIR /home/logpyx-openalpr/openalpr/src
RUN mkdir build

WORKDIR /home/logpyx-openalpr/openalpr/src/build
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..
RUN make && make install
RUN rm -rf /usr/local/lib/python3.5/dist-packages/openalpr*

WORKDIR /home/logpyx-openalpr/openalpr/src/bindings/python/
RUN python3 setup.py install 

RUN pip install opencv-python
RUN pip install pytesseract
RUN pip install paho-mqtt

#ENV IP_MQTT=gwqa.revolog.com.br
#ENV PORT_MQTT=1884
#ENV USER_NAME_MQTT=tecnologia
#ENV PASSWORD_MQTT=128Parsecs!
#ENV PUBLISH_TOPIC=aperam/plate
#ENV TESSERACT_GRAY=130
#ENV SCALE_FACTOR_CASCADE=1.7
#ENV CAMERA_SOURCE=rtsp://admin:128Parsecs!@192.168.15.85/Streaming/channels/101
#ENV TIME_OUT_SEND_PLATE=5
#ENV MIN_LINE_FRAME=100
#ENV MAX_LINE_FRAME=900

CMD ["python3", "/home/logpyx-openalpr/DetectionPlate.py"]
