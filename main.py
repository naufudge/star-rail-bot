import json
import asyncio
from bott import PomPomClient
from motor.motor_asyncio import AsyncIOMotorClient
from warps.inventory_db import uri

with open('config.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']
    TOPGG = data['TOPGG_TOKEN']

client = PomPomClient()

async def main():
    async with client:
        client.mongoConnect = AsyncIOMotorClient(uri)
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
