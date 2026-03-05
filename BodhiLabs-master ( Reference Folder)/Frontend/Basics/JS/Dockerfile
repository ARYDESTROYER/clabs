# Use the --platform flag to ensure an x86_64/amd64 image is built
FROM --platform=linux/amd64 ubuntu:24.04

LABEL "maintainer"="bodhitree"
LABEL version="1.0"
LABEL description="Regex"
ENV DEBIAN_FRONTEND=noninteractive

# Combine all apt-get calls into a single RUN layer to reduce image size
RUN apt-get update -y && \
    apt-get install -y \
    # Basic utilities
    vim \
    nano \
    curl \
    # Python
    python3-pip \
    # Node.js
    nodejs \
    npm \
    # Puppeteer dependencies
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon-x11-0 \
    libappindicator3-1 \
    libasound2t64 \
    libc6 \
    libcairo2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    locales \
    # Clean up apt cache to save space
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up Python symlink
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Configure locale
RUN sed -i 's/# pl_PL.UTF-8 UTF-8/pl_PL.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen pl_PL.UTF-8
ENV LANG=pl_PL.UTF-8
ENV LANGUAGE=pl_PL
ENV LC_ALL=pl_PL.UTF-8

WORKDIR /app

# Install Node.js dependencies
RUN npm init -y
RUN npm install puppeteer cssom color

# Create directories
RUN mkdir /home/.evaluationScripts /home/labDirectory

# Set up environment variables and bashrc
RUN echo "cd /home/labDirectory" >> /root/.bashrc
ENV INSTRUCTOR_SCRIPTS="/home/.evaluationScripts"
ENV LAB_DIRECTORY="/home/labDirectory"
ENV PATH="/home/.evaluationScripts:${PATH}"

# Expose port for the server
EXPOSE 30000

WORKDIR /home/labDirectory

CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init_activity.sh; while :; do sleep 10; done" ]
