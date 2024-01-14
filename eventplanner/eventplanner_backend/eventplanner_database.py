from tinydb import TinyDB, Query

db = TinyDB("db.json")
users_table = db.table("users")
event_table = db.table("events")

user_query = Query()
events_query = Query()

