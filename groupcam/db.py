import pymongo
import motor

from groupcam.conf import config


class DB(dict):
    __getattr__ = dict.__getitem__


db = DB(sync=None, async=None)


def init_database():
    uri, name = config['database']['uri'], config['database']['name']
    db.sync, db.async = (pymongo.MongoClient(uri)[name],
                         motor.MotorClient(uri).open_sync()[name])
