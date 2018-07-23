#!/usr/bin/python3
#-*- coding: UTF-8 -*-
# Example: ./push_tasks.py --server_address 203.88.168.62 --server_port 5672 --server_username admin --server_password Potato666999 --PID 1001 --TL 1000 --ML 1024 --TAG test --repeat 1000

"""
Push several tasks into rabbitMQ.
Using default exchange directly sent data to queue.
Default task distribution queue name: OJ_TASK.
Meanwhile, this script will auto generate the TID of tasks(from 0->repeat time).
Author: Yuan <yuan@yuan25.com>
"""

import argparse

import pika

def setParser():
    """
    Set args parser.
    """
    parser = argparse.ArgumentParser(description='Push several tasks to rabbitMQ server.')
    parser.add_argument('--server_address',
                        help='rabbitmq server IP address.',
                        required=True)
    parser.add_argument('--server_port',
                        help='rabbitmq server pord.',
                        required=True)
    parser.add_argument('--server_username',
                        help='rabbitmq server login user name.',
                        required=True)
    parser.add_argument('--server_password',
                        help='rabbitmq server login passwd.',
                        required=True)
    parser.add_argument('--repeat',
                        required=True,
                        help='Set repeat time.')
    parser.add_argument('--PID',
                        required=True,
                        help='Problem ID.')
    parser.add_argument('--TL',
                        required=True,
                        help='Time limit.')
    parser.add_argument('--ML',
                        required=True,
                        help='Memory limit.')
    parser.add_argument('--TAG',
                        required=True,
                        help='Task data tag.')
    return parser

if __name__ == '__main__':

    # Set parser and get value
    parser = setParser()
    args = parser.parse_args()
    value = {
        'PID': args.PID,
        'TL': args.TL,
        'ML': args.ML,
        'TAG': args.TAG
    }

    # Connect to rabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                args.server_address,
                int(args.server_port),
                '/',
                pika.PlainCredentials(args.server_username, args.server_password)
    ))
    channel = connection.channel()
    channel.queue_declare(queue='OJ_TASK')

    # Sent tasks
    for i in range(int(args.repeat)):
        channel.basic_publish(exchange='',
                             routing_key='OJ_TASK',
                             body=str(value))
    connection.close()

