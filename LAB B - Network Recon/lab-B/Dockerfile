FROM node:22 AS juiceshop_builder

WORKDIR /juice-shop
COPY .evaluationScripts/activityInitiator/juice-shop-src/ /juice-shop/

RUN npm i -g typescript ts-node \
  # Install dev deps so the TypeScript server build produces /juice-shop/build/app.js.
  && npm install --unsafe-perm \
  && npm run --silent build:frontend \
  && npm run --silent build:server \
  && test -f build/app.js \
  # Prune back to production deps for runtime.
  && npm prune --omit=dev \
  && npm dedupe --omit=dev \
  && rm -rf frontend/node_modules frontend/.angular frontend/src/assets \
  && mkdir -p logs \
  && chown -R 65532 logs \
  && chgrp -R 0 ftp/ frontend/dist/ logs/ data/ i18n/ \
  && chmod -R g=u ftp/ frontend/dist/ logs/ data/ i18n/ \
  && rm -f data/chatbot/botDefaultTrainingData.json ftp/legal.md i18n/*.json || true

FROM node:22-bookworm-slim AS node_runtime

FROM zaproxy/zap-stable:latest AS zap_assets

FROM owasp/modsecurity-crs:apache

USER root

# Install dependencies including FULL Java (not headless) for ZAP AWT/Swing GUI
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    curl \
    supervisor \
    nmap \
    gobuster \
    tcpdump \
    iproute2 \
    net-tools \
    default-jre \
    xvfb \
    xauth \
    libxext6 \
    libxi6 \
    libxtst6 \
    libxrender1 \
    fontconfig \
    fonts-dejavu-core \
  && rm -rf /var/lib/apt/lists/*

# Run Apache on the clabs-standard port inside the container.
ENV PORT=30000

# Provide Node.js runtime for Juice Shop.
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node

# Provide OWASP ZAP (WebSwing GUI + proxy) from the official image.
COPY --from=zap_assets /zap /zap

# Apache/ModSecurity config and lab assets.
COPY .evaluationScripts/activityInitiator/config/apache/juiceshop.single.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
COPY .evaluationScripts/activityInitiator/config/apache/custom-rules.conf /usr/local/apache2/conf/extra/lab-b-custom-rules.conf
COPY .evaluationScripts/activityInitiator/config/apache/public/ /usr/local/apache2/htdocs/public/

RUN echo "Include /usr/local/apache2/conf/extra/lab-b-custom-rules.conf" >> /etc/modsecurity.d/modsecurity-override.conf

# Juice Shop app (built in this image).
COPY --from=juiceshop_builder --chown=65532:0 /juice-shop /juice-shop

# clabs evaluation scripts (copied selectively to avoid shipping source code).
COPY .evaluationScripts/evaluate.sh /home/.evaluationScripts/evaluate.sh
COPY .evaluationScripts/autograder/ /home/.evaluationScripts/autograder/
COPY .evaluationScripts/activityInitiator/initactivity.sh /home/.evaluationScripts/activityInitiator/initactivity.sh
COPY .evaluationScripts/activityInitiator/reset.sh /home/.evaluationScripts/activityInitiator/reset.sh
COPY .evaluationScripts/activityInitiator/zaprunner.sh /home/.evaluationScripts/activityInitiator/zaprunner.sh
COPY .evaluationScripts/activityInitiator/config/ /home/.evaluationScripts/activityInitiator/config/

RUN chmod +x /home/.evaluationScripts/evaluate.sh \
  && chmod +x /home/.evaluationScripts/activityInitiator/initactivity.sh \
  && chmod +x /home/.evaluationScripts/activityInitiator/reset.sh \
  && chmod +x /home/.evaluationScripts/activityInitiator/zaprunner.sh \
  && mkdir -p /zap/wrk \
  && mkdir -p /home/labDirectory /opt \
  && chmod 777 /zap/wrk \
  && chmod 777 /home/labDirectory \
  && chmod 777 /opt

EXPOSE 30000 30003 30004 8080

ENTRYPOINT ["/home/.evaluationScripts/activityInitiator/initactivity.sh"]
