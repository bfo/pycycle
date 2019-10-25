import rx
from rx.operators import map, materialize
import aiohttp


async def perform_request(req_desc):
    async with aiohttp.ClientSession() as session:
        async with session.get(req_desc["url"]) as response:
            return await response.text()


def response_stream(loop, req_desc):
    return rx.from_future(loop.create_task(perform_request(req_desc))).pipe(materialize())


def make_http_driver(loop):
    def _driver(req_s):
        return req_s.pipe(
            map(lambda req_desc: response_stream(loop, req_desc))
        )

    return _driver
