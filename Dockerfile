FROM python:3.10-slim-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

COPY . /APILogger/
WORKDIR /APILogger

COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /uvx /bin/

RUN uv --version
RUN ln -s $(which python3) /usr/bin/python
RUN bash /APILogger/setting-scripts/install_dependencies.sh
