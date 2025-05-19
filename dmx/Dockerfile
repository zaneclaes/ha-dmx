FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    g++ \
    make \
    autoconf \
    automake \
    libtool \
    pkg-config \
    bison \
    flex \
    libcppunit-dev \
    libmicrohttpd-dev \
    libprotobuf-dev \
    protobuf-compiler \
    python3 \
    python3-pip \
    python3-protobuf \
    libusb-1.0-0-dev \
    libftdi-dev \
    libncurses-dev \
    libavahi-client-dev \
    libavahi-common-dev \
    libunwind-dev \
    protobuf-compiler \
    libprotobuf-dev \
    libprotoc-dev \
    uuid-dev \
    jq \
    wget

# Clone OLA source
RUN git clone https://github.com/OpenLightingProject/ola.git /ola

# Patch OLA to disable root check and Avahi
WORKDIR /ola
RUN autoreconf -i && \
    ./configure --disable-root-check --disable-avahi --enable-python-libs && \
    make -j$(nproc) && \
    make install

RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/ola.conf && ldconfig

WORKDIR /app
COPY bridge.py /app/
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Create runtime directories
RUN mkdir -p /root/.ola
COPY ola/ /root/.ola/

EXPOSE 9090
CMD ["/run.sh"]