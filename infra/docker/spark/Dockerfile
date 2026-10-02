# Spark 4.1 для модуля 07: master, workers и сервер Spark Connect (driver) на одном образе.
# К официальному образу добавлены (и пользователь dev с UID хоста):
#  - Iceberg runtime и AWS bundle — чтение и запись Iceberg через REST-каталог Lakekeeper;
#  - Python 3.12 для executors: Python UDF выполняются на executors, и минорная версия Python
#    должна совпадать с клиентом (workspace — 3.12, в образе Spark — 3.10).
FROM apache/spark:4.1.3-scala2.13-java17-python3-ubuntu

USER root
ARG ICEBERG_VERSION=1.12.0
ARG MAVEN=https://repo1.maven.org/maven2/org/apache/iceberg
RUN curl -fsSL -o /opt/spark/jars/iceberg-spark-runtime-4.1_2.13-${ICEBERG_VERSION}.jar \
      ${MAVEN}/iceberg-spark-runtime-4.1_2.13/${ICEBERG_VERSION}/iceberg-spark-runtime-4.1_2.13-${ICEBERG_VERSION}.jar \
    && curl -fsSL -o /opt/spark/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
      ${MAVEN}/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

COPY --from=ghcr.io/astral-sh/uv:python3.12-bookworm-slim /usr/local/bin/uv /usr/local/bin/uv
RUN UV_PYTHON_INSTALL_DIR=/opt/python uv python install 3.12 \
    && ln -s "$(ls -d /opt/python/cpython-3.12*/bin)/python3.12" /usr/local/bin/python3.12 \
    && mkdir -p /opt/spark/work /opt/spark/logs && chmod 777 /opt/spark/work /opt/spark/logs

# Пользователь с UID/GID хоста: executors пишут в смонтированный репозиторий, а Hadoop внутри
# Spark требует, чтобы у UID была запись в /etc/passwd (иначе «Invalid UID, could not determine
# effective user»).
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} dev && useradd -m -u ${UID} -g ${GID} -s /bin/bash dev

ENV PYSPARK_PYTHON=/usr/local/bin/python3.12 \
    SPARK_NO_DAEMONIZE=true
USER dev
