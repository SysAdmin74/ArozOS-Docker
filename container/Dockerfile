FROM golang:1.16.7-buster
RUN apt update -y && apt upgrade -y
RUN apt install ffmpeg -y
RUN git clone https://github.com/tobychui/arozos.git /arozos
WORKDIR /arozos/src
RUN git checkout v1.114
RUN go build
CMD ./arozos -port 80
