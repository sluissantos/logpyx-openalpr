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
    nano \
    python3-pip \
    iproute2 \
    v4l-utils \
    --reinstall libxcb-xinerama0 \
    iputils-ping 


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

RUN pip install opencv-python-headless
RUN pip install pytesseract
RUN pip install paho-mqtt

#ENV IP_MQTT=10.50.239.100
#ENV PORT_MQTT=1883
#ENV USER_NAME_MQTT=tecnologia
#ENV PASSWORD_MQTT=128Parsecs!
#ENV PUBLISH_TOPIC=aperam/plate
#ENV PUBLISH_TOPIC_STATUS=aperam/status
#ENV TESSERACT_GRAY=130
#ENV SCALE_FACTOR_CASCADE=1.7
#ENV CAMERA_SOURCE=rtsp://admin:128Parsecs!@10.50.239.20/Streaming/channels/101
#ENV TIME_OUT_SEND_PLATE=5
#ENV MIN_LINE_FRAME=200
#ENV MAX_LINE_FRAME=900
#ENV MAX_PLATES=100

CMD ["python3", "/home/logpyx-openalpr/DetectionPlate.py"]
