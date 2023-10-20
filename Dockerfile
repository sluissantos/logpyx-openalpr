FROM ubuntu:latest

# Install prerequisites
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    curl \
    libcurl4-openssl-dev \
    git \
    libleptonica-dev \
    liblog4cplus-dev \
    libopencv-dev \
    libtesseract-dev \
    wget \
    tesseract-ocr \
    nano \
    python3-pip \
    v4l-utils \
    --reinstall libxcb-xinerama0 

# Remover pacotes relacionados à interface gráfica
RUN apt-get remove -y --auto-remove --purge \
    ubuntu-desktop \
    gnome-panel \
    lightdm \
    firefox

# Limpar o cache do apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Definir a variável de ambiente para desabilitar a interface gráfica
ENV DEBIAN_FRONTEND noninteractive

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

USER root
CMD ["bash"]
#CMD ["python3", "/home/logpyx-openalpr/DetectionPlate.py"]