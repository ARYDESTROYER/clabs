FROM sarus.bodhi.cse.iitb.ac.in/35/docker-combined5:latest

# Remove broken repo
RUN rm -f /etc/apt/sources.list.d/ondrej*.list

# Install sudo
RUN apt-get update && apt-get install -y sudo

# Create student user with temp sudo
RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student_temp && \
    chmod 440 /etc/sudoers.d/student_temp

# Setup directories (Ensure mount points exist)
RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# --- FALLBACK CHANGE START ---
# Removed COPY .evaluationScripts and chmod.
# We rely on the runtime volume mount for these files.
# --- FALLBACK CHANGE END ---

# Environment
ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts" \
    LAB_DIRECTORY="/home/labDirectory" \
    PATH="/home/.evaluationScripts:${PATH}" \
    TERM=xterm-256color \
    HOME="/home/student"

# Permissions
# We only set permissions for directories we created. 
# .evaluationScripts permissions will be determined by the host mount.
RUN chown -R student:student /home/labDirectory

# Bash QoL
RUN echo "cd /home/labDirectory" >> /home/student/.bashrc && \
    echo "alias ls='ls --color=always'" >> /home/student/.bashrc

# Set User and CMD
USER student
WORKDIR /home/labDirectory
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
