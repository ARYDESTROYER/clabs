FROM --platform=linux/amd64 ubuntu:24.04

LABEL maintainer="bodhitree"
LABEL version="1.0"

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
        gnupg \
        lsb-release \
        apt-transport-https \
        locales \
        file && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN yes | unminimize

# Install Node.js (NodeSource). This gives a reliable node + npm pair.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install remaining packages (Puppeteer deps, Python tooling, unminimize) and run unminimize non-interactively.
# This block chooses the available ALSA provider (libasound2t64 on 24.04, libasound2 on older releases).
RUN apt-get update -y && \
    if apt-cache showpkg libasound2t64 >/dev/null 2>&1; then ALSA_PKG=libasound2t64; \
    elif apt-cache showpkg libasound2 >/dev/null 2>&1; then ALSA_PKG=libasound2; \
    else ALSA_PKG=""; fi && \
    apt-get install -y --no-install-recommends \
      unminimize \
      # basic utilities
      vim \
      nano \
      less \
      # networking tools
      iproute2 \
      net-tools \
      # Python
      python3 \
      python3-pip \
      python3-bs4 \
      python3-cssutils \
      # Puppeteer / headless chrome dependencies
      fonts-liberation \
      libnss3 \
      libatk1.0-0 \
      libatk-bridge2.0-0 \
      libcups2 \
      libxkbcommon-x11-0 \
      libappindicator3-1 \
      ${ALSA_PKG} \
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
      locales && \
    # run unminimize non-interactively (guarded). This may install many packages -> larger image.
    yes | unminimize || true && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# make 'python' point to python3 (no-op if symlink exists)
RUN ln -s /usr/bin/python3 /usr/local/bin/python || true

RUN mkdir -p /home/labDirectory /home/.evaluationScripts

# Create app folders (and optionally copy your project files)
RUN mkdir -p /app

WORKDIR /app

# Verify npm and install node packages used previously in the working dir.
# If you have package.json/package-lock.json, prefer COPY + npm ci for caching and reproducibility.
RUN npm --version && \
npm init -y && \
npm install puppeteer cssom color --no-audit --no-fund

WORKDIR /home/labDirectory

RUN echo "cd /home/labDirectory" >> /root/.bashrc && \
    echo "alias ls='ls --color=always'" >> /root/.bashrc && \
    echo "rm -f \$(find /home -type f -name \"._*\")" >> /root/.bashrc

# Expose the port used previously
EXPOSE 30000

CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/init_activity.sh; while :; do sleep 10; done" ]
