import aiohttp
import asyncio
import ujson



# api main = https://api.covid19api.com/
# countries must be the country slug
# status: confirmed, recovered, deaths

async def summary():
    # returns the number of covid cases from the first case
    url = "https://api.covid19api.com/summary"
    async with aiohttp.ClientSession() as session:
        req = await session.request(method="GET", url=url,)
        res = ujson.loads(await req.text())
        return res
