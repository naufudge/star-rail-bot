import json
from bott import PomPomClient

with open('config.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

if __name__ == '__main__':
    client = PomPomClient()
    client.run(TOKEN)
