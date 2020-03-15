import json
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

import settings
from mysql2ch import pos_handler, reader, partitioner

logger = logging.getLogger('mysql2ch.producer')

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_SERVER,
    value_serializer=lambda x: json.dumps(x).encode(),
    key_serializer=lambda x: x.encode(),
    partitioner=partitioner
)


def produce(args):
    log_file, log_pos = pos_handler.get_log_pos()
    try:
        for schema, table, event, file, pos in reader.binlog_reading(
                only_tables=settings.TABLES,
                only_schemas=settings.SCHEMAS,
                log_file=log_file,
                log_pos=log_pos,
                server_id=int(settings.MYSQL_SERVER_ID)
        ):
            try:
                key = f'{schema}.{table}'
                producer.send(
                    topic=settings.KAFKA_TOPIC,
                    value=event,
                    key=key,
                )
                logger.debug(f'send event success: key:{key},event:{event}')
                # pos_handler.set_log_pos_slave(file, pos)
            except Exception as e:
                logger.error(f'kafka send error: {e}')
                exit()
    except KeyboardInterrupt:
        log_file, log_pos = pos_handler.get_log_pos()
        message = f'KeyboardInterrupt,current position: {log_file}:{log_pos}'
        logger.info(message)