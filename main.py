import asyncio
from datetime import timedelta

import rx
from rx.operators import map, take, flat_map, delay
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from http_driver import make_http_driver

loop = asyncio.get_event_loop()


def main(sources):
    ticks_stream = rx.interval(timedelta(seconds=1)).pipe(
        map(lambda n: n + 1),
        take(10)
    )
    responses_stream = sources["http"].pipe(
        flat_map(lambda s: s),
    )
    queries = rx.of(
        {"url": "https://jsonplaceholder.typicode.com/todos/1"},
        {"url": "https://error123123123.co.uk"},
    ).pipe(
        delay(timedelta(seconds=2))
    )
    return {
        "log": rx.merge(queries, responses_stream, ticks_stream),
        "http": queries
    }


def my_print(*args):
    print("My error handler")
    print(len(args))
    print(args)


def make_console_driver():
    def console_driver(text_s):
        text_s.subscribe(
            on_next=print,
            on_error=my_print,
        )

    return console_driver


drivers = {
    "log": make_console_driver(),
    "http": make_http_driver(loop)
}


def run(main_f, drivers):
    fake_sinks = {k: Subject() for k in drivers}
    sources = {k: drivers[k](fake_sinks[k]) for k in drivers}
    sinks = main_f(sources)
    for k in fake_sinks:
        if k in sinks:
            sinks[k].subscribe(fake_sinks[k], scheduler=AsyncIOScheduler(loop))


run(main, drivers)

loop.run_forever()
