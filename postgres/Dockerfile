FROM postgres:latest
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    "postgresql-server-dev-$PG_MAJOR" \
    && rm -rf /var/lib/apt/lists/*
RUN cd /tmp && \
    git clone https://github.com/timescale/pg_textsearch && \
    cd pg_textsearch && \
    make && \
    make install && \
    rm -rf /tmp/pg_textsearch
RUN apt-get purge -y --auto-remove build-essential git "postgresql-server-dev-$PG_MAJOR"
