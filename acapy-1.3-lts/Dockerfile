FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.3-lts

# Install required packages and configure sudo access
USER root
RUN apt-get update -y && \
    apt-get install -y sudo patch postgresql-client && \
    echo 'aries ALL=NOPASSWD: ALL' >> /etc/sudoers && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to aries user and apply patch
USER aries
WORKDIR /home/aries/.local/lib/python3.12/site-packages
COPY ./patch.diff ./
RUN patch -p1 < patch.diff