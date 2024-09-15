FROM neo4j:latest

RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install neo4j graphdatascience torch

EXPOSE 7474 7687
ENV NEO4J_AUTH=none
ENV NEO4J_PLUGINS='["graph-data-science"]'
RUN echo 'user:x:${UID:-1000}:${GID:-1000}::/workspace:/bin/bash' >> /etc/passwd
