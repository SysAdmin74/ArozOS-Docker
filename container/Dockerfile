FROM golang:latest
RUN apt update -y && apt upgrade -y
RUN apt install ffmpeg wget tar -y

RUN git clone https://github.com/tobychui/arozos.git /arozos
WORKDIR /arozos/src
RUN go build

# Start arozos in container style
CMD ./arozos -port=80 -enable_pwman=false -enable_hwman=false
