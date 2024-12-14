#!/usr/bin/env python3

# Test server, one can start manually and use it to test integrate against test_data.py using http://localhost:8080/api URI.

# Python 3 server example
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from typing import Any

import test_data

logging.basicConfig(level=logging.INFO)

hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):  # noqa: D101
    def sendJsonObj(self, data: dict[str, Any]) -> None:  # noqa: D102
        dt = bytes(json.dumps(data), "utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dt)))
        self.end_headers()
        self.wfile.write(dt)

    def readJsonObj(self):  # noqa: D102
        o = self.rfile.read(int(self.headers["Content-Length"]))
        logging.info(o)

    def doAny(self):  # noqa: D102
        if self.command == "GET" and self.path == "/api/info":
            self.sendJsonObj(test_data.DummyDeviceInfo)
        elif self.command == "GET" and self.path == "/api/spec":
            self.sendJsonObj(test_data.DummyDeviceSpec)
        elif self.command == "GET" and self.path == "/api/data":
            self.sendJsonObj(test_data.DummyDeviceData)
        elif self.command == "POST" and self.path == "/api/data":
            self.readJsonObj()
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)

    def handle(self):  # noqa: D102
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ""
                self.request_version = ""
                self.command = ""
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            self.doAny()
            self.wfile.flush()
        except TimeoutError as e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            return


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    logging.info("Server started http://%s:%s", hostName, serverPort)

    from contextlib import suppress

    with suppress(KeyboardInterrupt):
        webServer.serve_forever()

    webServer.server_close()
    logging.info("Server stopped.")
