from random import random
from time import sleep

from flask import Flask, request, jsonify
from redis import RedisError, sentinel
import sys

app = Flask(__name__)

ERROR_KEY_NOT_FOUND = "Key not found in redis"

class RedisDriver:
    def __init__(self, redis_config):
        self.service = redis_config["service_name"]
        self.__connect(redis_config)

    def __connect(self, redis_config):
        try:
            self.connection = sentinel.Sentinel([(redis_config["master_host"],
                                                  redis_config["master_port"]),
                                                 (redis_config["slave_1_host"],
                                                  redis_config["slave_1_port"]),
                                                 (redis_config["slave_2_host"],
                                                  redis_config["slave_2_port"]),
                                                 (redis_config["slave_3_host"],
                                                  redis_config["slave_3_port"])],
                                                min_other_sentinels=2,
                                                encoding="utf-8",
                                                decode_responses=True)

        except RedisError as err:
            error_str = "Error while connecting to redis : " + str(err)
            sys.exit(error_str)

    def set(self, key, value):
        key_str = str(key)
        val_str = str(value)
        try:
            expiry = 60 + random.randint(-10, 10)
            master = self.connection.master_for(self.service)
            master.set(key_str, val_str, expiry=expiry)
            return {"success": True}
        except RedisError as err:
            error_str = "Error while connecting to redis : " + str(err)
            return {"success": False,
                    "error": error_str}

    def get(self, key):
        key_str = str(key)
        try:
            master = self.connection.master_for(self.service)
            value = master.get(key_str)
        except RedisError as err:
            error_str = "Error while retrieving value from redis : " + str(err)
            return {"success": False,
                    "error": error_str}

        if value is not None:
            return {"success": True,
                    "value": value}
        else:
            return {"success": False,
                    "error": ERROR_KEY_NOT_FOUND}

    def delete(self, key):
        key_str = str(key)
        try:
            master = self.connection.master_for(self.service)
            value = master.delete(key_str)
        except RedisError as err:
            error_str = "Error while deleting key from redis : " + str(err)
            return {"success": False,
                    "error": error_str}

        return {"success": True}


redis_config = {"service_name": "mymaster",
                "master_host": "redis-master",
                "master_port": 26379,
                "slave_1_host": "sentinel-1",
                "slave_1_port": 26379,
                "slave_2_host": "sentinel-2",
                "slave_2_port": 26379,
                "slave_3_host": "sentinel-3",
                "slave_3_port": 26379, }

redis_driver = RedisDriver(redis_config)

test_str =  """
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
"""

for i in range(12000):
    redis_driver.set(f"test{i}", i)
    if i % 1000 == 0:
        sleep(0.5)