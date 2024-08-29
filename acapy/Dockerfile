FROM bcgovimages/aries-cloudagent:py3.12_1.0.0

USER root
WORKDIR /root

RUN apt-get -qq -y update
RUN apt-get -qq -y upgrade unattended-upgrades
RUN apt-get -qq -y install --no-install-recommends \
                    sudo strace sysstat lsof \
                    net-tools netcat tcpdump libcap2-bin \
                    postgresql-client redis-tools \
                    patch

COPY ./patches/aries-cloudagent-python.diff /root/patch.diff
WORKDIR /home/aries/.local/lib/python3.12/site-packages
RUN patch -p1 < /root/patch.diff

RUN echo 'aries ALL=NOPASSWD: ALL' >> /etc/sudoers
USER aries
WORKDIR /home/aries
