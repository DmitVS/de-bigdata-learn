# Flink 2.1 для модуля 08: jobmanager, taskmanager и SQL-клиент на одном образе.
# К официальному образу добавлены коннекторы в /opt/flink/lib:
#  - Kafka (читаем топики Redpanda), Avro + Schema Registry (формат avro-confluent);
#  - Iceberg runtime + AWS bundle (пишем в Iceberg через REST-каталог Lakekeeper);
#  - Hadoop client: Iceberg для Flink использует классы конфигурации Hadoop, хотя HDFS у нас нет.
FROM flink:2.1.3-scala_2.12-java17

ARG MAVEN=https://repo1.maven.org/maven2
ARG KAFKA_CONNECTOR=5.0.0-2.1
ARG FLINK_VERSION=2.1.3
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.4.3
RUN cd /opt/flink/lib \
    && wget -q ${MAVEN}/org/apache/flink/flink-sql-connector-kafka/${KAFKA_CONNECTOR}/flink-sql-connector-kafka-${KAFKA_CONNECTOR}.jar \
    && wget -q ${MAVEN}/org/apache/flink/flink-sql-avro-confluent-registry/${FLINK_VERSION}/flink-sql-avro-confluent-registry-${FLINK_VERSION}.jar \
    && wget -q ${MAVEN}/org/apache/iceberg/iceberg-flink-runtime-2.1/${ICEBERG_VERSION}/iceberg-flink-runtime-2.1-${ICEBERG_VERSION}.jar \
    && wget -q ${MAVEN}/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
    && wget -q ${MAVEN}/org/apache/hadoop/hadoop-client-api/${HADOOP_VERSION}/hadoop-client-api-${HADOOP_VERSION}.jar \
    && wget -q ${MAVEN}/org/apache/hadoop/hadoop-client-runtime/${HADOOP_VERSION}/hadoop-client-runtime-${HADOOP_VERSION}.jar

# Общий том чекпоинтов jobmanager и taskmanager: папка принадлежит flink, и Docker при первом
# создании тома копирует её владельца.
RUN mkdir -p /opt/flink/checkpoints && chown flink:flink /opt/flink/checkpoints
