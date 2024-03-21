import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import asyncio
import time
import sys
import os
import yaml
import base64
import pysiteontornado as pt

# yaml.= yaml.typ='safe', pure=True)

# Get the script directory
data_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
#sys.path.insert(0, data_directory)

pt.start()