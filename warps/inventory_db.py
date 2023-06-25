from urllib.parse import quote_plus

user = quote_plus('nauf')
password = quote_plus('Celesti@l143')

uri = f"mongodb+srv://{user}:{password}@pompomcluster.rk76yym.mongodb.net/?retryWrites=true&w=majority"
