FROM bcgovimages/aries-cloudagent:py3.9-indy-1.16.0_0.9.0

USER root
WORKDIR /root

RUN apt-get -qq -y update
RUN apt-get -qq -y upgrade unattended-upgrades
RUN apt-get -qq -y install --no-install-recommends \
                    sudo strace sysstat lsof \
                    net-tools netcat tcpdump libcap2-bin \
                    postgresql-client redis-tools \
                    patch

RUN echo 'indy ALL=NOPASSWD: ALL' >> /etc/sudoers
USER indy
WORKDIR /home/indy
