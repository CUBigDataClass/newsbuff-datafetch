FROM python:3.6-slim

RUN  pip3 install pika
RUN  pip3 install pymongo

WORKDIR /srv
COPY    logsBackend.py /srv
CMD [ "python3", "logsBackend.py"]