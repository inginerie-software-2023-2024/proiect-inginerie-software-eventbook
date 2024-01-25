import base64
import pickle

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware


TYPES = {"<class 'str'>": str}
# class SetSerializer(Serializer):
#     OBJ_CLASS = set  # The class this serializer handles
#
#     def encode(self, obj):
#         list_from_obj = list(obj)
#         if list_from_obj:
#             TYPES[str(type(list_from_obj[0]))] = type(list_from_obj[0])
#             return f'{type(list_from_obj[0])}#%#{",".join(map(str, list_from_obj))}'
#         return ",".join(map(str, obj))
#
#     def decode(self, s):
#         str_type, s = s.split('#%#')
#         return set(map(TYPES[str_type], s.split(",")))


class SetSerializer:
    OBJ_CLASS = set

    def encode(self, obj):
        # Serialize the entire set object at once
        return base64.b64encode(pickle.dumps(obj)).decode()

    def decode(self, obj: str):
        # Deserialize the set object
        return pickle.loads(base64.b64decode(obj))


serialization = SerializationMiddleware(lambda: JSONStorage("db.json"))

serialization.register_serializer(SetSerializer(), "TinySet")


db = TinyDB(storage=serialization)
users_table = db.table("users")
event_table = db.table("events")
invitation_table = db.table("invitations")

user_query = Query()
events_query = Query()
invitations_query = Query()
