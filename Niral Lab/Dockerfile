FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

# Update and install required tools for the CTF lab
RUN apt-get update && apt-get install -y \
    python3 \
    sudo \
    steghide \
    vim-common \
    coreutils \
    findutils \
    grep \
    gawk \
    tar \
    gzip \
    file \
    less \
    tree \
    libimage-exiftool-perl \
    binwalk \
    ruby \
    ruby-dev \
    sox \
    build-essential \
    binutils \
    && gem install zsteg \
    && rm -rf /var/lib/apt/lists/*

# Create student user with temporary sudo for init-time setup.
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Setup directories (Ensure mount points exist)
RUN mkdir -p /home/labDirectory /home/.evaluationScripts && \
    chown -R student:student /home/labDirectory

# Environment
ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

USER student
WORKDIR /home/labDirectory

CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
