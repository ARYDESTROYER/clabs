FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install only essential tools in one layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        vim \
        python3 \
        python3-bs4 \
        iproute2 \
        net-tools \
        less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup Directory Structure
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# Set the working directory
WORKDIR /home/labDirectory

# Global Settings
RUN echo "cd /home/labDirectory" >> /root/.bashrc && \
    echo "alias ls='ls --color=always'" >> /root/.bashrc && \
    echo "rm -f \$(find /home -type f -name \"._*\")" >> /root/.bashrc

CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init.sh; while :; do sleep 10; done" ]
