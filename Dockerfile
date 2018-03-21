FROM ubuntu:16.04

# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        wget \
        pkg-config \
        rsync \
        software-properties-common \
        unzip \
        git \
        cmake \
        libgtk-3-dev \
        libboost-all-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh tmp/Miniconda3-4.2.12-Linux-x86_64.sh
RUN bash tmp/Miniconda3-4.2.12-Linux-x86_64.sh -b
ENV PATH $PATH:/root/miniconda3/bin/

COPY ./scripts/environment.yml  ./environment.yml
RUN conda env create -f=environment.yml --name blury python=3.5 --debug -v -v

# cleanup tarballs and downloaded package files
RUN conda clean -tp -y

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

COPY ./scripts/install_darkflow.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/install_darkflow.sh

RUN install_darkflow.sh

WORKDIR "/app"

COPY . .

COPY ./scripts/run_app.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/run_app.sh

RUN wget -Nq https://pjreddie.com/media/files/yolo.weights -O blury/data/models/yolo.weights

ENTRYPOINT ["run_app.sh"]
