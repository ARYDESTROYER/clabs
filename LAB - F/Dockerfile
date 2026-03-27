# LAB - F: Deflection and DNS Rebinding-Style Internal Access Abuse
# Shared Dockerfile for Activities 1-3

FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

RUN rm -f /etc/apt/sources.list.d/ondrej*.list

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    curl \
    grep \
    sed \
    python3 \
    net-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/labDirectory /home/.evaluationScripts

ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/root"

WORKDIR /home/labDirectory

CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
