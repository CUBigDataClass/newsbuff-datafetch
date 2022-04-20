from datetime import datetime
import sys
import os, pymongo
import pika

##
## Configure test vs. production
##
rabbitMQUri = os.getenv("RABBITMQ_URI")
dBUrl = os.getenv("DB_URL")
print("Connected to RabbitMQ")

client = None
try:
    # set a 5-second connection timeout
    client = pymongo.MongoClient(dBUrl, serverSelectionTimeoutMS=5000)
    print("Connected to the DB server.")
except Exception as error:
    print("Unable to connect to the DB server.")
    raise error
mydb = client["testdbnewsbuff"]
logsCollection = mydb["log"]

logsCollection.insert_one({'msg': 'Connected to DB', 'ts': datetime.now() })

rabbitMQ = pika.BlockingConnection(
        pika.URLParameters(rabbitMQUri))
rabbitMQChannel = rabbitMQ.channel()

logsCollection.insert_one({'msg': 'Connected to RabbitMQ', 'ts': datetime.now() })

rabbitMQChannel.exchange_declare(exchange='backendlogs', exchange_type='topic')
result = rabbitMQChannel.queue_declare('', exclusive=True)
queue_name = result.method.queue

#infoKey = f"{platform.node()}.worker.info"

binding_keys = sys.argv[1:]
if not binding_keys:
    #
    # Wildcard key will listen to anything
    #
    binding_keys = [ "#"]

for key in binding_keys:
    rabbitMQChannel.queue_bind(
            exchange='backendlogs', 
            queue=queue_name,
            routing_key=key)

def callback(ch, method, properties, body):
    msg = f" [x] {method.routing_key}:{body}"
    print(msg, file=sys.stdout, flush=True)
    obj = { 'msg': msg, 'ts': datetime.now() }
    logsCollection.insert_one(obj)
    sys.stdout.flush()
    sys.stderr.flush()

print(' [*] Waiting for BACKEND logs. To exit press CTRL+C')

rabbitMQChannel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()
