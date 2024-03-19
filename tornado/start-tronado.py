import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import asyncio
import time
import sys
import os
import yaml


# yaml.= yaml.typ='safe', pure=True)

# Get the script directory
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

# Define default configuration settings
default_config = {
    "main_html": "main.html",
    "inactivity_timeout": 30,
    "port": 8000,
    # Add other default settings here
    'database': {
        'host': 'localhost',
        'port': 3306,
        'user': 'user',
        'password': 'password',
    },
    'logging': {
        'level': 'INFO',
        'path': '/var/log/myapp.log',
    },
    'feature_flags': {
        'new_feature': False,
    }
}

# Load existing config or create a new one if it doesn't exist
config_file_path = os.path.join(script_directory, "config.yaml")
if os.path.exists(config_file_path):
    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file) or {}
else:
    config = {}

# Function to recursively update the config dictionary with any missing keys/values
def update_config(target, updates):
    for key, value in updates.items():
        if target is None:
            target = {}
        if key is None:
            continue
        elif key not in target:
            target[key] = value
        elif isinstance(value, dict):
            target[key] = update_config(target.get(key, {}), value)
    return target

# Update the existing config with any missing configurations
config = update_config(config, default_config)

# Write the updated configuration back to config.yaml
with open(config_file_path, 'w') as file:
    yaml.dump(config, file)

print(f'Configuration updated and saved to {config_file_path}.')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open(os.path.join(script_directory, config["main_html"]), "r") as file:
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
            if time.time() - self.last_keepalive > config["inactivity_timeout"]:
                await self.close()
                print("Closed connection due to inactivity.")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/feed", FeedHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(config["port"])
    tornado.ioloop.IOLoop.current().start()
