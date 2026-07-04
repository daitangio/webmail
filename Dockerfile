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

RUN mkdir -p /root/.pi/agent/
COPY etc/pi/models.json /root/.pi/agent/models.json

# Install the RTK command to reduce token usage
COPY ./etc/rtk-installer.sh /tmp/
RUN /tmp/rtk-installer.sh 
ENV PATH="/root/.local/bin:${PATH}"

# Important to avoid malfunction: define the DEEPSEEK_API_KEY
# API Key is provided by https://platform.deepseek.com/

RUN pi --version




# RUN addgroup --gid 1000  app && adduser --uid 1000 --ingroup app  app
# USER app

# WORKDIR /home/app

# COPY LICENSE .

# COPY pyproject.toml .

# # GG Codex suggestion to extract requirements to cache them before real install 
# # You can comment this 2 lines if you want a more "standard" - unoptimized procedure
# RUN python -c "import tomllib; p=tomllib.load(open('pyproject.toml','rb')); print('\n'.join(p['project']['dependencies']))" > requirements.txt
# RUN pip install --user -r requirements.txt
# # RUN ls /home/app/.cache/

# 

# COPY tests tests
# COPY src src
# COPY README.md .

# RUN pip install -e .

# RUN python3 -m unittest discover -s tests


# TODO