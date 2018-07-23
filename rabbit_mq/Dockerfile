FROM rabbitmq

COPY rabbitmq.config /etc/rabbitmq/rabbitmq.config

# Activate management plugin
RUN rabbitmq-plugins --offline enable rabbitmq_management

EXPOSE 8080 5672
CMD ["rabbitmq-server"]
