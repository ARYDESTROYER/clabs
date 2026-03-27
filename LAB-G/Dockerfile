FROM zaproxy/zap-stable:latest AS zap_assets

FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

RUN rm -f /etc/apt/sources.list.d/ondrej*.list

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-flask \
    python3-requests \
    supervisor \
    curl \
    net-tools \
    openjdk-17-jre \
    xvfb \
    xauth \
    libxext6 \
    libxi6 \
    libxtst6 \
    libxrender1 \
    fontconfig \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY --from=zap_assets /zap /zap

RUN mkdir -p /home/labDirectory /home/.evaluationScripts /opt/labg /zap/wrk \
    && chmod 777 /home/labDirectory /opt/labg /zap/wrk

EXPOSE 30000 30003 30004 8080

WORKDIR /home/labDirectory

CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
