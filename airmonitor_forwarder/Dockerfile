# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|aarch64|i386|amd64"

ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

# Install dependencies
RUN apk add --no-cache python3 py3-pip curl jq
RUN pip3 install --no-cache-dir requests

# Copy files
COPY run.sh /
COPY airmonitor_forwarder.py /app/

# Make run script executable
RUN chmod +x /run.sh

CMD [ "/run.sh" ]