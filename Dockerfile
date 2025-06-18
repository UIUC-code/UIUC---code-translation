FROM ubuntu:22.04

ARG USERNAME=researcher
ARG USER_UID=1000
ARG USER_GID=1000

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3-pip \
    openssh-server \
    && apt-get clean

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME:password | chpasswd 

RUN mkdir /var/run/sshd
EXPOSE 22

WORKDIR /home/$USERNAME/project
COPY . .
RUN chown -R $USER_UID:$USER_GID /home/$USERNAME

USER $USERNAME

RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

CMD ["/usr/sbin/sshd", "-D"]