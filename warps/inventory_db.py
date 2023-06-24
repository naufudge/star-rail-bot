from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

user = quote_plus('nauf')
password = quote_plus('Celesti@l143')

uri = f"mongodb+srv://{user}:{password}@pompomcluster.rk76yym.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['PomPomDB']
collection = db['characters']

# collection.insert_one({'_id':248347746187083777, 'characters':{
#     "Natasha": 1,
#     "Asta": 2,
#     "Sampo": 1,
#     "Dan Heng": 1,
#     "March 7th": 1,
#     "Serval": 1,
#     "Yukong": 2
# }})

user = collection.find_one({'_id': 248347746187083777})
print(list(user['characters']))
