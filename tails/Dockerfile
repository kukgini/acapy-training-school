FROM  ghcr.io/bcgov/tails-server:1.0.0

USER root
WORKDIR /root

RUN mkdir -p /home/indy/tails-files
RUN chown indy:indy /home/indy/tails-files

RUN apt-get -qq -y update
RUN apt-get -qq -y upgrade unattended-upgrades
RUN apt-get -qq -y install sudo patch

RUN echo 'indy ALL=NOPASSWD: ALL' >> /etc/sudoers
USER indy
WORKDIR /home/indy