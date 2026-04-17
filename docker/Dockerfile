ARG PICOCLAW_VERSION=v0.2.6
ARG OLLAMA_VERSION=0.20.4
ARG NODE_VERSION=24

# Use the official picoclaw image to get the binary
FROM sipeed/picoclaw:${PICOCLAW_VERSION} AS picoclaw-bin
FROM sipeed/picoclaw:${PICOCLAW_VERSION}-launcher AS picoclaw-bin-launcher

# Use the official Ollama image to get the binary
FROM ollama/ollama:${OLLAMA_VERSION} AS ollama-bin

# Use your preferred Webtop flavor as the base (e.g., Ubuntu, Alpine)
FROM lscr.io/linuxserver/webtop:ubuntu-mate

# Copy picoclaw binaries and libraries
COPY --from=picoclaw-bin --chown=abc:abc /usr/local/bin/picoclaw* /usr/local/bin
COPY --from=picoclaw-bin-launcher --chown=abc:abc /usr/local/bin/picoclaw* /usr/local/bin

# Copy the Ollama binary from the official image
COPY --from=ollama-bin --chown=abc:abc /usr/bin/ollama /usr/local/bin/ollama

# Start Ollama to start automatically when the desktop loads,
RUN mkdir -p /custom-cont-init.d
RUN echo "runuser -l abc -c 'ollama serve &'" > /custom-cont-init.d/start-ollama.sh && \
   chmod +x /custom-cont-init.d/start-ollama.sh

COPY PicoClaw.desktop /custom-cont-init.d/PicoClaw.desktop
COPY start-picoclaw.sh /custom-cont-init.d/start-picoclaw.sh

EXPOSE 11434

