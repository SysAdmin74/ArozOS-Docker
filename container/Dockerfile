FROM golang:1.16.7-buster
RUN apt install git
RUN git clone https://github.com/tobychui/arozos.git /arozos
WORKDIR /arozos/src
RUN git checkout v1.113
RUN go build
RUN apt install ffmpeg
CMD /arozos/src/arozos -port 80