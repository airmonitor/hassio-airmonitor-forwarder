# hadolint global ignore=DL3006,DL3018,DL3059
ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app
COPY requirements.txt .
# Install dependencies
RUN apk add --no-cache python3 py3-pip curl jq &&  \
    pip3 install --no-cache-dir -r requirements.txt

# Copy files
COPY run.sh /
COPY airmonitor_forwarder.py /app/

# Make run script executable
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
