import asyncio
from retrieval.web_forager import SovereignWebForager

async def test():
    forager = SovereignWebForager()
    print("Forager initialized")
    async for page in forager.forage("https://example.com"):
        print("Page:", page.title)
        break

asyncio.run(test())
