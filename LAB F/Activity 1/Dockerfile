FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

# The base image ships a broken Ondrej PPA -- remove before apt update.
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
        sudo \
        curl \
        net-tools \
        python3 \
        python3-pip \
        python3-flask \
        python3-requests \
    && rm -rf /var/lib/apt/lists/*

# Student user with TEMPORARY sudo (revoked at end of initactivity.sh).
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Mount points -- the LMS will mount tarballs into /home/.evaluationScripts and
# /home/labDirectory at runtime, NOT during build (do not COPY into them).
RUN mkdir -p /home/labDirectory /home/.evaluationScripts /opt/labf

ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

RUN chown -R student:student /home/labDirectory /opt/labf

RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc && \
    echo "alias runbot='curl -s -X POST http://127.0.0.1:30000/api/run-bot | python3 -m json.tool'" >> /home/student/.bashrc

USER student
WORKDIR /home/labDirectory

EXPOSE 30000

CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
