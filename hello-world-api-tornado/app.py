import asyncio
import logging
import sys

from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web

from handlers.HelloWorldHandler import HelloWorldHandler


class App(tornado.web.Application):

    def __init__(self, **kwargs):
        kwargs['handlers'] = [
            ('/', HelloWorldHandler),
        ]
        super(HelloWorldApplication, self).__init__(**kwargs)


def start_service(port_number=3000):
    """
    Starts the API.
    """
    set_up_logging()
    log = logging.getLogger(__name__)
    # change event loop policy to make tornado work on Windows
    # this is needed due to changes in asyncio in python v3.8
    # see: https://github.com/tornadoweb/tornado/issues/2608
    if 'win' in sys.platform:
        asyncio.set_event_loop_policy((asyncio.WindowsSelectorEventLoopPolicy()))
    application = App()
    server = HTTPServer(application, ssl_options=None)
    server.listen(port_number)
    log.info("Starting Service on port {}".format(port_number))
    tornado.ioloop.IOLoop.current().start()


def set_up_logging():
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level="INFO", format=LOG_FORMAT)


if __name__ == '__main__':
    start_service()
