import json
import asyncio
from topgg import DBLClient, WebhookManager
from bott import PomPomClient
from asyncio import sleep as gts

with open('config_test.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']
    TOPGG = data['TOPGG_TOKEN']

async def dbl_server_count_update(client: PomPomClient, toke: str):
    # with DBLClient(client, toke) as dbl_client:
    while not client.is_closed():
        dbl_client = DBLClient(client, toke)
        try:
            # await self.topggpy.post_guild_count()
            await dbl_client.post_guild_count()
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            # print(e)

        await dbl_client.close()
        await gts(60*60*12)

client = PomPomClient()

async def main():
    async with client:
        if not TOPGG == "":
            client.loop.create_task(dbl_server_count_update(client, TOPGG))
        await client.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
    # client.run(TOKEN)
