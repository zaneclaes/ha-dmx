FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Install OLA and dependencies
RUN apt-get update && \
    apt-get install -y \
        ola ola-bin ola-python python3-pip git mosquitto-clients \
        && rm -rf /var/lib/apt/lists/*

# Install dmx2mqtt
RUN pip3 install git+https://github.com/mqtti/dmx2mqtt.git

# Add entrypoint
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 9090

CMD ["/run.sh"]