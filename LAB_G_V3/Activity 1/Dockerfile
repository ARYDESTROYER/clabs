FROM node:22-bookworm-slim AS node_runtime

FROM bkimminich/juice-shop:v19.1.1 AS juiceshop_assets

FROM zaproxy/zap-stable:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_ENV=production \
    PORT=30000

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    net-tools \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Node runtime for Juice Shop process.
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node

# Default Juice Shop application artifacts.
COPY --from=juiceshop_assets /juice-shop /juice-shop

# Runtime scripts come from tarball mount at /home/.evaluationScripts
# No COPY commands for scripts here.

# 30000: Juice Shop
# 30004: ZAP WebSwing GUI
# 8080: ZAP Proxy
EXPOSE 30000 30004 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:30000/ >/dev/null && curl -fsS http://127.0.0.1:30004/zap/ >/dev/null || exit 1

# BodhiLabs standard CMD
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
