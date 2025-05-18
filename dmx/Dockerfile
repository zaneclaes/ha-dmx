FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Install OLA and dependencies
RUN apt-get update && \
    apt-get install -y \
        python3-pip git mosquitto-clients \
        && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ola \
    ola-python \
    && apt-get clean

WORKDIR /app

COPY bridge.py /app/
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Create non-root user
RUN useradd -m dmxuser

# Create the .ola config directory and copy the file
RUN mkdir -p /home/dmxuser/.ola
COPY ola-usbserial.conf /home/dmxuser/.ola/ola-usbserial.conf

# Make sure permissions are correct if using non-root
RUN chown -R dmxuser:dmxuser /home/dmxuser/.ola

# Set permissions on OLA spool and config directories
RUN mkdir -p /var/lib/ola /var/run/ola /etc/ola && \
    chown -R dmxuser /var/lib/ola /var/run/ola /etc/ola

# Switch to non-root
USER dmxuser

EXPOSE 9090
CMD ["/run.sh"]