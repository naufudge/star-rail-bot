from aiohttp import web
from discord.ext import commands

# This is basically a barebones version of top.gg
class webhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _webhook(self):
        async def vote_handler(request):
            req_auth = request.headers.get('Authorization')
            if self.bot.config.WEBHOOK_AUTH == req_auth:
                data = await request.json()
                if data.get('type') == 'upvote':
                    await self.on_dbl_vote(data)
                elif data.get('type') == 'test':
                    await self.on_dbl_test(data)
                else:
                    return
                return web.Response(status=200)
            else:
                return web.Response(status=401)

        app = web.Application(loop=self.bot.loop)
        app.router.add_post('/dblwebhook', vote_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', 5000)
        await self._webserver.start()

    async def on_dbl_vote(self, data):
        # Process votes here. the data variable is a dict with {"user": "user id here", "type": "test or other"} honestly i dont remember all the data that is included but this is the gist
        userId = data["user"]

    async def on_dbl_test(self, data):
        # There is a button on top.gg that you can use to send a test vote. it will be processed here
        userId = data["user"]

async def setup(bot):
    await bot.add_cog(webhook(bot))
