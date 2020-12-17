#!/usr/bin/env bash
# shellcheck disable=SC1090

apt-get update
apt-get install -y --no-install-recommends \
        gcc \
        git \
        libatlas3-base \
        libavformat58 \
        npm \
        portaudio19-dev \
        pulseaudio \
        python3-pip
npm install -g yarn
apt-get clean -y
apt-get autoremove -y