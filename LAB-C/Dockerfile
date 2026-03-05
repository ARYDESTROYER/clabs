# Lab C: DNS Zone Attack & DNS Tunneling Detection
# Shared Dockerfile for all 3 activities

FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

# Fix broken repositories in base image
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    sudo \
    bind9 \
    bind9utils \
    dnsutils \
    tshark \
    tcpdump \
    python3 \
    python3-pip \
    net-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install dnsrecon via pip (best-effort)
RUN pip3 install --break-system-packages dnsrecon 2>/dev/null || true

# Create student user with temporary sudo access
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Create required mount point directories
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# Environment variables
ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

# Set base permissions
RUN chown -R student:student /home/labDirectory

# Quality of life
RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

# Default user and working directory
USER student
WORKDIR /home/labDirectory

# Container startup
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
