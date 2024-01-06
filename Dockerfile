FROM ubuntu:22.04
SHELL [ "/bin/bash", "-c" ]
# LABEL about the custom image
LABEL maintainer="fnechans"
LABEL version="0.1"
LABEL description="This is a custom Docker Image for Fillibot."

USER root

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive
# Update Ubuntu Software repository
RUN apt update
RUN apt install -y python3-all python3-pip espeak ffmpeg
# virtualenv python3.10-venv

ADD ./requirements.txt /fillibot/
WORKDIR /fillibot

RUN cd /fillibot

#RUN python3 -m venv env/
#RUN source env/bin/activate
RUN python3 -m pip install -U --upgrade pip
RUN python3 -m pip install -U --upgrade -r requirements.txt
