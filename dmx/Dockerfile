FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Install OLA and dependencies
RUN apt-get update && \
    apt-get install -y \
        python3-pip git mosquitto-clients \
        && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y gnupg curl lsb-release && \
    echo "deb http://apt.openlighting.org/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/ola.list && \
    curl http://apt.openlighting.org/ola.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y ola ola-bin ola-python

# Install dmx2mqtt
RUN pip3 install git+https://github.com/mqtti/dmx2mqtt.git

# Add entrypoint
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 9090

CMD ["/run.sh"]