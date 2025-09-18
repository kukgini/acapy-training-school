FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.3-lts

USER root
WORKDIR /root

RUN apt-get update -y
RUN apt-get install -y sudo patch postgresql-client

COPY ./patch.diff /root/patch.diff
WORKDIR /home/aries/.local/lib/python3.12/site-packages
RUN patch -p1 < /root/patch.diff

RUN echo 'aries ALL=NOPASSWD: ALL' >> /etc/sudoers
USER aries
WORKDIR /home/aries
