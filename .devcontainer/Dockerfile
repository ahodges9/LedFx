# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT} AS venv-image

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "source /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi
RUN python -m venv /ledfx/venv
ENV PATH="/ledfx/venv/bin:$PATH"

# Install dependencies and ledfx, remove unneeded packages
COPY .devcontainer/dev_install.sh .
RUN chmod +x dev_install.sh && ./dev_install.sh \
    && rm -rf dev_install.sh

### Create docker image from venv-image to install pip dependencies
#
FROM venv-image AS build-image
COPY --from=venv-image /ledfx/venv /ledfx/venv
ENV PATH="/ledfx/venv/bin:$PATH"
COPY requirements.txt /tmp
COPY requirements-dev.txt /tmp
COPY docs/requirements-docs.txt /tmp
RUN python -m pip install --upgrade pip wheel setuptools
RUN pip install -r tmp/requirements.txt
RUN pip install -r tmp/requirements-dev.txt
RUN pip install -r tmp/requirements-docs.txt

### Create docker image from venv-image to install LedFx
#
FROM venv-image AS install-image
COPY --from=build-image /ledfx/venv /ledfx/venv
ENV PATH="/ledfx/venv/bin:$PATH"
WORKDIR /ledfx-git
COPY . !.*/* /ledfx-git/
RUN python setup.py build
RUN python setup.py install

# Create docker image from venv-image as dist-image
#
FROM venv-image AS dist-image
ARG USERNAME="ledfx"

COPY --from=install-image /ledfx/venv /ledfx/venv
ENV PATH="/ledfx/venv/bin:$PATH"

RUN rm -rf /var/lib/apt/lists/*

RUN useradd --create-home $USERNAME --groups audio
WORKDIR /home/ledfx
USER $USERNAME

EXPOSE 8888/tcp
EXPOSE 5353/udp
ENTRYPOINT [ "ledfx"]

# RUN frontend/npm install && npm start

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp