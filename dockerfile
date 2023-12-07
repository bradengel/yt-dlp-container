FROM python:3.11.7
RUN apt update
RUN apt upgrade -y
RUN apt install rclone -y
RUN pip install --upgrade pip
RUN pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib yt-dlp ytdl-nfo 
RUN curl -L https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -O
RUN unxz ffmpeg-master-latest-linux64-gpl.tar.xz
RUN tar -xf ffmpeg-master-latest-linux64-gpl.tar
RUN chmod 0755 ffmpeg-master-latest-linux64-gpl/bin/*
RUN rm -rf ffmpeg-master-latest-linux64-gpl.tar
VOLUME ["/youtube"]