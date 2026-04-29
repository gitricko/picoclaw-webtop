ARG PICOCLAW_VERSION=v0.2.6
ARG OLLAMA_VERSION=0.21.0
ARG NODE_VERSION=24
ARG MODELRELAY_VERSION=1.16.0

# Use the official picoclaw image to get the binary
FROM sipeed/picoclaw:${PICOCLAW_VERSION} AS picoclaw-bin
FROM sipeed/picoclaw:${PICOCLAW_VERSION}-launcher AS picoclaw-bin-launcher

# Use the official Ollama image to get the binary
FROM ollama/ollama:${OLLAMA_VERSION} AS ollama-bin

# Get the binaries from official Node image
FROM node:${NODE_VERSION}-slim AS node-bin

# Use your preferred Webtop flavor as the base (e.g., Ubuntu, Alpine)
FROM lscr.io/linuxserver/webtop:ubuntu-mate

# Install help utilities and clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y htop && rm -rf /var/lib/apt/lists/*

# Copy Node.js binaries and libraries
COPY --from=node-bin --chown=abc:abc /usr/local/bin/node /usr/local/bin/
COPY --from=node-bin --chown=abc:abc /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# Copy picoclaw binaries and libraries
COPY --from=picoclaw-bin --chown=abc:abc /usr/local/bin/picoclaw* /usr/local/bin
COPY --from=picoclaw-bin-launcher --chown=abc:abc /usr/local/bin/picoclaw* /usr/local/bin

# Copy the Ollama binary from the official image
COPY --from=ollama-bin --chown=abc:abc /usr/bin/ollama /usr/local/bin/ollama

# Start Ollama to start automatically when the desktop loads,
RUN mkdir -p /custom-cont-init.d
COPY --chown=abc:abc *.desktop /custom-cont-init.d
COPY --chown=abc:abc *.sh /custom-cont-init.d

# Install ModelRelay and start automatically when desktop loads
ARG MODELRELAY_VERSION
RUN npm install -g modelrelay@${MODELRELAY_VERSION} && \
    npm cache clean --force && \
    chown -R abc:abc /usr/local/lib/node_modules/modelrelay /usr/local/bin/modelrelay

EXPOSE 18800 7352