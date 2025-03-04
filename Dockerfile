FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

COPY . /mockapi/

RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y software-properties-common && \
    apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils && \
    apt-get install -y python3-pip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN ln -s $(which python3) /usr/bin/python
RUN bash /mockapi/setting-scripts/install_dependencies.sh
RUN bash /mockapi/setting-scripts/install_pip.sh
