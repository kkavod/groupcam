import pymongo
import motor

from groupcam.conf import config


class DB(dict):
    __getattr__ = dict.__getitem__


db = DB(sync=None, async=None)


def init_database(testing=False):
    if testing:
        uri, name_key = None, 'testing_name'
    else:
        uri, name_key = config['database']['uri'], 'name'
    name = config['database'][name_key]
    db.sync, db.async = (pymongo.MongoClient(uri)[name],
                         motor.MotorClient(uri).open_sync()[name])
