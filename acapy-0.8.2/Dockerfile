FROM bcgovimages/aries-cloudagent:py36-1.16-1_0.8.2

USER root
WORKDIR /root

RUN apt-get -qq -y update

RUN apt-get -qq -y install --no-install-recommends \
                    sudo net-tools netcat \
                    postgresql-client \
                    vim patch

RUN echo 'indy ALL=NOPASSWD: ALL' >> /etc/sudoers
USER indy
WORKDIR /home/indy