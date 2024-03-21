# pysiteapisfortornado/endpoints/__init__.py

# This file marks this directory as a Python package.

import yaml
import os
from typing import Optional
from enum import Enum, auto
import sqlite3
import time
import sys
import base64


import sqlite3

this = sys.modules[__name__]

class PathType(Enum):
    USER = auto()
    APPLICATION = auto()
    SYSTEM = auto()

def recommend_path(path_type: PathType) -> Optional[str]:
    global PySiteConfig, application_name
    path = None
    if path_type == PathType.USER:
        # User-specific data storage
        path =  os.path.expanduser('~')
    elif path_type == PathType.APPLICATION:
        # Application-specific data storage
        if os.name == 'nt':  # Windows
            path =  os.environ.get('LOCALAPPDATA', None)
        elif os.name == 'posix':
            # Mac and Linux (XDG standard if available)
            path =  os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    elif path_type == PathType.SYSTEM:
        # System-wide data storage
        if os.name == 'nt':  # Windows
            path =  os.environ.get('PROGRAMDATA', None)
        elif os.name == 'posix':
            # Mac and Linux
            path =  '/usr/local/share' if os.geteuid() == 0 else None
    if path is None:
        return None
    else:
        path+=os.sep
        path+=application_name
        return path


def fix_path(path: str) -> str:
    return os.path.expanduser(path)

def ensure_parent_directory_exists(file_path):
    """
    Ensures the parent directory of the specified file exists.
    Creates the directory if it does not exist.

    Args:
        file_path (str): The file path for which the parent directory is checked.
    """
    parent_dir = os.path.dirname(file_path)
    return ensure_directory_exists(parent_dir)

def ensure_directory_exists(path):
    """
    Ensures the parent directory of the specified file exists.
    Creates the directory if it does not exist.

    Args:
        path (str): The file path for which the parent directory is checked.
    """
    # Check if the parent directory exists, create if it does not
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created missing directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def get_config():
    global PySiteConfig
    config_file_path = os.path.join(data_directory, "PySiteConfig.yaml")
    if not os.path.exists(config_file_path):
        set_config(default_config)
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            PySiteConfig = yaml.safe_load(file) or {}
    else:
        PySiteConfig = {}
    update_config(default_config)
    return PySiteConfig

def set_config(new_config):
    global PySiteConfig
    PySiteConfig = new_config
    write_config()

# Write the updated configuration back to PySiteConfig.yaml
def write_config():
    
    ensure_parent_directory_exists(config_file_path)
    with open(config_file_path, 'w') as file:
        try:
            yaml.dump(PySiteConfig, file)
            print(f'Configuration updated and saved to {config_file_path}.')
        except Exception as e:
            print(f'Error writing configuration to {config_file_path}: {e}')

# Function to recursively update the PySiteConfig dictionary with any missing keys/values
def update_dictionary(target, updates):
    global update_dictionary_Updated
    changed = False
    for key, value in updates.items():
        if target is None:
            target = {}
            update_dictionary_Updated= time.time()
        if key is None:
            continue
        elif key not in target:
            target[key] = value
            update_dictionary_Updated = time.time()
        elif isinstance(value, dict):
            target[key] = update_dictionary(target.get(key, {}), value)
    return target

def update_config(updates):
    global PySiteConfig,update_dictionary_Updated
    if not('lastupdate' in PySiteConfig.keys()):
        PySiteConfig['lastupdate'] = time.time()
    try:
        if update_dictionary_Updated is None:
            update_dictionary_Updated = time.time()
    except:
        update_dictionary_Updated = time.time()
    last_update = update_dictionary_Updated
    #PySiteConfig=get_config()
    update_dictionary(PySiteConfig, updates)
    if last_update != update_dictionary_Updated:
        write_config()
    return PySiteConfig

def parantpath(path):
    return os.path.abspath(path).replace("\\+[^\\]*$", "/+[^/]*$")

def project_folder():
    # Return the folder that is to folders above this file.
    return parantpath(parantpath(os.path.dirname(os.path.abspath(__file__))))

global application_name, data_directory, config_file_path, PySiteConfig
application_name = "pysite_on_tornado"
data_directory = recommend_path(PathType.APPLICATION)
ensure_directory_exists(data_directory)
config_file_path = os.path.join(data_directory, "PySiteConfig.yaml")
# Define default configuration settings
default_config = {
    "application_name": "pysite_on_tornado",
    "main_html": "main.html",
    'project_folder': project_folder(),
    "debug": False,
    "verbose": False,
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
    },
    'JWT': {
        'SECRET_KEY': base64.b64encode(os.urandom(32)),
        'TOKEN_EXPIRATION_SECONDS': 3600,
        'COOKIE_NAME': 'jwt',
        'COOKIE_HTTPONLY': True,
        'JWT_ALGORITHM': 'HS256'
    },
    'AESGCM': {
        'KEY': base64.b64encode(os.urandom(32))
    },
    'RSA': {
        'PRIVATE_KEY': None,
        'PUBLIC_KEY': None
    }
}
# Load existing PySiteConfig or create a new one if it doesn't exist
config_file_path = os.path.join(data_directory, "PySiteConfig.yaml")
if os.path.exists(config_file_path):
    with open(config_file_path, "r") as file:
        PySiteConfig = yaml.safe_load(file) or {}
else:
    PySiteConfig = {}

this.PySiteConfig = PySiteConfig