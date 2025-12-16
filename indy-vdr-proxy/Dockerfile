FROM rust:1.85-slim AS builder

USER root
WORKDIR /root

RUN apt-get update -y && \
    apt-get install -y ca-certificates \
                    libtool \
                    pkg-config \
                    build-essential \
                    autoconf \
                    automake \
                    cmake \
                    libssl-dev \
                    libzmq3-dev


COPY  . .
RUN cargo build --release

FROM rust:1.85-slim

RUN mkdir -p /etc/indy

COPY --from=builder /root/target/release/indy-vdr-proxy /usr/bin/indy-vdr-proxy