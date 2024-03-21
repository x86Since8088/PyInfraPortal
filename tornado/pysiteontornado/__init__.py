# pysiteapisfortornado/__init__.py
import fnmatch
import importlib
import pkgutil
from . import data
from . import endpoints
import tornado.web
import tornado.websocket
import os
import json
import asyncio
import time
import sys


data_directory = data.recommend_path(data.PathType.APPLICATION)

def load_endpoints():
    endpoints_handlers = []
    module = endpoints
    endpointlist = dir(module)
    filtered_list = list(filter(lambda s: s.startswith('\w'), endpointlist))
    for name in filtered_list:
        item = getattr(module, name)
        if isinstance(item, type) and issubclass(item, tornado.web.RequestHandler):
            route = '/' + name.lower().replace('_', '/')
            endpoints_handlers.append((route, item))
    return endpoints_handlers


def list_matching_functions(pattern):
    """
    List functions in the global scope matching the given wildcard pattern.
    
    Args:
        pattern (str): A wildcard pattern to match function names against.
        
    Returns:
        list of str: Function names matching the pattern.
    """
    return [name for name, obj in globals().items()
            if callable(obj) and obj.__module__ == __name__ and fnmatch.fnmatch(name, pattern)]

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        PySiteConfig = data.get_config()
        with open(os.path.join(PySiteConfig['project_folder'], PySiteConfig["main_html"]), "r") as file:
            file_content = file.read()
            self.write(file_content)

class FeedHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    async def open(self):
        self.last_keepalive = time.time()
        self.clients.add(self)
        self.write_message('{"message": "Connected to the WebSocket feed."}')
        asyncio.create_task(self.keep_alive_check())

    async def on_message(self, message):
        if message == "keepalive":
            self.last_keepalive = time.time()
            await self.write_message(json.dumps({"message": "keepalive received"}))
        else:
            await self.write_message(json.dumps({"message": f"Echo: {message}", "timestamp": time.time()}))

    async def on_close(self):
        self.clients.remove(self)
        print("WebSocket closed")

    async def keep_alive_check(self):
        while self in self.clients:
            await asyncio.sleep(1)
            if time.time() - self.last_keepalive > PySiteConfig["inactivity_timeout"]:
                await self.close()
                print("Closed connection due to inactivity.")

def make_app():
    endpoints = load_endpoints()
    endpoints.append(("/", MainHandler))
    endpoints.append(("/feed", FeedHandler))
    return tornado.web.Application(endpoints)

def start():
    app = make_app()
    app.settings.keys()
    app.listen(data.PySiteConfig["port"])
    tornado.ioloop.IOLoop.current().start()
