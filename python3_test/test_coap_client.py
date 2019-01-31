import logging 

import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main():
    protocol = await Context.create_client_context()
    await asyncio.sleep(2)
    payload = b'the quick brown fox jumps over the lazy dog.\n'

    request = Message(code=1, payload = payload,uri='coap://californium.eclipse.org')

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('failed to fetch resource:')
        print(e)
    else:
        print('Result:%s\n%r'%(response.code,response.payload))

if __name__ == "__main__":
    asyncio.run(main())