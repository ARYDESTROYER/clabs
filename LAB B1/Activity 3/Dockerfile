FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

# The base image ships a broken PPA source list; remove before apt-get update.
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

# Enable contrib + non-free so nikto is installable.
RUN sed -i 's|bullseye main|bullseye main contrib non-free|; s|bullseye-security main|bullseye-security main contrib non-free|; s|bullseye-updates main|bullseye-updates main contrib non-free|' /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive

# Apache + mod_security (the WAF), Flask (the target app), recon tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    apache2 \
    libapache2-mod-security2 \
    python3 \
    python3-flask \
    nmap \
    nikto \
    gobuster \
    dirb \
    curl \
    net-tools \
    iproute2 \
    vim \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Student user with TEMPORARY sudo. initactivity.sh revokes it at the end.
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Mount points (volumes are attached at runtime, never at build time).
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

RUN chown -R student:student /home/labDirectory

RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

EXPOSE 30000

USER student
WORKDIR /home/labDirectory

CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
