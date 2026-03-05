FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        vim \
        nano \
        man-db \
        manpages \
        python3 \
        net-tools \
        less \
        gedit \
        zip \
        bzip2 \
        unzip \
        sudo \
        file && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN yes | unminimize

RUN mkdir -p /home/labDirectory /home/.evaluationScripts

WORKDIR /home/labDirectory

RUN echo "cd /home/labDirectory" >> /root/.bashrc && \
    echo "alias ls='ls --color=always'" >> /root/.bashrc && \
    echo "rm -f \$(find /home -type f -name \"._*\")" >> /root/.bashrc

CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init.sh; while :; do sleep 10; done" ]
