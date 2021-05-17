import logging

import tornado
from tornado.escape import json_decode
import tornado.web


class HelloWorldHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.log = logging.getLogger(__name__)

    def get(self):
        self.log.info("New GET request")
        self.write("Hello, world")

    def post(self):
        self.log.info("New POST request")
        try:
            json_request = json_decode(self.request.body)
        except Exception as e:
            raise tornado.web.HTTPError(400, log_message='Could not decode JSON: ' + str(e))
        self.write({
            'result': 'success',
            'data': {
                'body': json_request,
            }
        })
