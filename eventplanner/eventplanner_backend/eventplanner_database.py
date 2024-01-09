from tinydb import TinyDB, Query

db = TinyDB("db.json")
users_table = db.table("users")
user_items = db.table("user_items")

user_query = Query()
items_query = Query()

