#!/usr/bin/env python

# importing all dependencies
import pika
import os
import sys
import platform


# declaring the routing keys for different topics - info/warning/debug
infoKey = f"{platform.node()}.logs.info"
warningKey = f"{platform.node()}.logs.warning"
errorKey = f"{platform.node()}.logs.error"
debugKey = f"{platform.node()}.logs.debug"


# reusable object to fetch the channel details and rabbitMQ details
def fetchConnection():

        rabbitMQUri = os.getenv("RABBITMQ_URI")
        print("Connected to RabbitMQ")

        rabbitMQ = pika.BlockingConnection(
                pika.URLParameters(rabbitMQUri))
        rabbitMQChannel = rabbitMQ.channel()
        rabbitMQChannel.exchange_declare(exchange='backendlogs', exchange_type='topic')
        return rabbitMQChannel, rabbitMQ


# reusable object to publish "info message" into the logs.
# Takes two parameters: <info message to be pusblished> and <rabbitMQChannel object received from fetchConnection() call>
def log_info(message, rabbitMQChannel, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='backendlogs', routing_key=key, body=message)

# reusable object to publish "debug message" into the logs.
# Takes two parameters: <debug message to be pusblished> and <rabbitMQChannel object received from fetchConnection() call>
def log_debug(message, rabbitMQChannel, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='backendlogs', routing_key=key, body=message)


# reusable object to publish "warning message" into the logs.
# Takes two parameters: <warning message to be pusblished> and <rabbitMQChannel object received from fetchConnection() call>
def log_warning(message, rabbitMQChannel, key=warningKey):
    print("WARNING:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='backendlogs', routing_key=key, body=message)


# reusable object to publish "error message" into the logs.
# Takes two parameters: <error message to be pusblished> and <rabbitMQChannel object received from fetchConnection() call>
def log_error(message, rabbitMQChannel, key=errorKey):
    print("ERROR:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='backendlogs', routing_key=key, body=message)


# reusable object to close the rabbitMQ connection
# Takes one parameter: <rabbitMQ object received from fetchConnection() call>
def closeConnection(rabbitMQ):
        rabbitMQ.close()





