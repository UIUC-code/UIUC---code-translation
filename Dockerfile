
FROM ubuntu:22.04


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-server \
    ca-certificates \
    curl \
    wget \
    build-essential && \
    rm -rf /var/lib/apt/lists/*


RUN mkdir /var/run/sshd

RUN ssh-keygen -A

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME:password | chpasswd

WORKDIR /home/$USERNAME/project
COPY . .
RUN chown -R $USER_UID:$USER_GID /home/$USERNAME

USER $USERNAME
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi



RUN echo 'root:password' | chpasswd


EXPOSE 22


CMD ["/usr/sbin/sshd", "-D"]