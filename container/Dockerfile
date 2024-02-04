FROM golang:latest
RUN apt update -y && apt upgrade -y
RUN apt install ffmpeg wget tar -y

ADD --chmod=744 "https://github.com/tobychui/arozos/releases/latest/download/arozos_linux_amd64" /arozos/arozos
ADD --chmod=744 "https://github.com/aroz-online/launcher/releases/latest/download/launcher_linux_amd64" /arozos/launcher
ADD --chmod=644 "https://github.com/tobychui/arozos/releases/latest/download/web.tar.gz" /arozos/web.tar.gz

COPY --chmod=744 start.sh /arozos/start.sh
WORKDIR /arozos

CMD [ "./start.sh" ]
