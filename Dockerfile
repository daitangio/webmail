FROM python:3.14-slim-trixie

ENV PATH="$PATH:/home/app/.local/bin"

RUN pip install --upgrade pip
RUN python -m venv .venv
# Ensure basic pi.dev is installed
RUN apt update && apt install -y git curl xz-utils
RUN mkdir -p /root/.local/share/pi-node
RUN curl -fsSL https://nodejs.org/dist/latest-v22.x/node-v22.23.1-linux-arm64.tar.xz -o /tmp/node-v22.23.1-linux-arm64.tar.xz && \
    tar -xf /tmp/node-v22.23.1-linux-arm64.tar.xz -C /root/.local/share/pi-node && \
    rm -f /root/.local/share/pi-node/current && \
    ln -s /root/.local/share/pi-node/node-v22.23.1-linux-arm64 /root/.local/share/pi-node/current && \
    rm -rf /tmp/node-v22.23.1-linux-arm64.tar.xz
# Needed anode standalone (node 22) Try etc/pi-installer.sh
ENV PATH="/root/.local/share/pi-node/node-v22.23.1-linux-arm64/bin:${PATH}"
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# Install the RTK command to reduce token usage
COPY ./etc/rtk-installer.sh /tmp/
RUN /tmp/rtk-installer.sh 
ENV PATH="/root/.local/bin:${PATH}"

# Important to avoid malfunction: define the DEEPSEEK_API_KEY
# API Key is provided by https://platform.deepseek.com/
ENV PI_TELEMETRY=no
# PI_CODING_AGENT_DIR	Override config directory; default is ~/.pi/agent
ENV PI_CODING_AGENT_DIR=/workspaces/webmail/var/pi-agent
# Ensure Sessions are not lost and keep them in a separate directory instead of under pi-agent
ENV PI_CODING_AGENT_SESSION_DIR=/workspaces/webmail/var/pi-sessions/
RUN pi --version


# Ensure gh is installed (optioanl but can be userful)
# RUN (type -p wget >/dev/null || (apt update && apt install wget -y)) \
# 	&& mkdir -p -m 755 /etc/apt/keyrings \
# 	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
# 	&& cat $out | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
# 	&& chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
# 	&& mkdir -p -m 755 /etc/apt/sources.list.d \
# 	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
# 	&& apt update \
# 	&& apt install gh -y

