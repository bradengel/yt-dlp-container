FROM python:3.11.7-slim
RUN apt update \
   && apt upgrade -y \
   && apt install rclone curl xz-utils -y \ 
   && pip install --upgrade pip \
   && pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib yt-dlp ytdl-nfo logzero \
   && curl -L https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -O \
   && unxz ffmpeg-master-latest-linux64-gpl.tar.xz \
   && tar -xf ffmpeg-master-latest-linux64-gpl.tar \
   && chmod 0755 ffmpeg-master-latest-linux64-gpl/bin/* \
   && rm -rf ffmpeg-master-latest-linux64-gpl.tar
ENV CONFIG="/config/yt.yaml"
ENV TOKEN=""
ENV REFRESH=""
ENV ID=""
ENV SECRET=""
VOLUME ["/youtube", "/config"]
COPY yt.py /
COPY yt.yaml /config/yt.yaml
# ENTRYPOINT python3 ./yt.py --config $CONFIG