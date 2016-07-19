FROM ubuntu:14.04
MAINTAINER Robert Thompson <rthompsonj@gmail.com>

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list
RUN apt-get update && apt-get install -y mongodb-org curl bzip2

RUN mkdir -p /root
RUN mkdir -p /data/db
RUN mkdir -p /WEATHER

# get miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# python packages
RUN conda install -y \
    pymongo \
    flask

RUN pip install \
    geopy

COPY * /WEATHER/
WORKDIR "/WEATHER"

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]


