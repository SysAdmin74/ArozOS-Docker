FROM golang:latest@sha256:9048d5e7751706200eb1719c7dae0436950d362f29a1da91fa05e5c63867c60f
RUN apt update -y && apt upgrade -y
RUN apt install ffmpeg wget tar -y

ADD --checksum=sha256:0f0db8992ecf47d60a844bbf2eaab2eb57b4f1f00adb3a4062ac963de9e3a9a5 --chmod=744 "https://github.com/tobychui/arozos/releases/download/v2.025/arozos_linux_amd64" /arozos/arozos
ADD --checksum=sha256:9d8eabf7f94e9cc0c6b943940135bf18d3e240990ed50bd37f32191aed73ac58 --chmod=644 "https://github.com/tobychui/arozos/releases/download/v2.025/web.tar.gz" /arozos/web.tar.gz

COPY --chmod=744 start.sh /arozos/start.sh
WORKDIR /arozos

ENTRYPOINT [ "./start.sh" ]
