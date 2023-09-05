# 构建开发环境，安装依赖包
# [python](https://hub.docker.com/_/python)
FROM python:3.10 AS builder

ENV APP_HOME=/private-gpt

WORKDIR ${APP_HOME}

# 编译Sqlite3
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3430000.tar.gz \
    && tar -zxvf sqlite-autoconf-3430000.tar.gz \
    && cd sqlite-autoconf-3430000 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install \
    && cd .. \
    && rm -rf sqlite-autoconf-3430000 \
    && rm -rf sqlite-autoconf-3430000.tar.gz

# 提前安装，因为 cpu 版本需要指定 index-url。
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchvision \
    --index-url https://download.pytorch.org/whl/cpu

# RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

COPY ./requirements.txt ${APP_HOME}/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r ${APP_HOME}/requirements.txt

# 编译应用
COPY ./app ${APP_HOME}/app
RUN find ${APP_HOME}/app -name '*.py[co]' -delete \
    && python -m compileall -b ${APP_HOME}/app \
    && find ${APP_HOME}/app -name '*.py' -delete

# 发布应用
FROM python:3.10-slim

ARG SQLITE3_PATH
ENV APP_HOME=/private-gpt

WORKDIR ${APP_HOME}

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=l,sharing=locked \
    apt update && \
    apt-get install libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx --no-install-recommends -y && \
    rm -rf /var/lib/apt/lists/*

# 拷贝Sqlite3
COPY --from=builder /usr/local/lib/libsqlite3.so.0.8.6 ${SQLITE3_PATH}

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder ${APP_HOME}/app ${APP_HOME}/app

EXPOSE 80

COPY ./asserts ${APP_HOME}/asserts
COPY ./static ${APP_HOME}/static
COPY ./templates ${APP_HOME}/templates
COPY ./models ${APP_HOME}/models
COPY ./.env ${APP_HOME}/.env

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--config", "app/gunicorn_conf.pyc", "--preload", "app.main:app"]
