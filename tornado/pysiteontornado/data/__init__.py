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

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import sqlite3

def initialize_config():
    global application_name, data_directory, config_file_path, config
    application_name = "pysite_on_tornado"
    data_directory = recommend_path(PathType.APPLICATION)
    ensure_directory_exists(data_directory)
    config_file_path = os.path.join(data_directory, "config.yaml")

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
    global config
    # Load existing config or create a new one if it doesn't exist
    config_file_path = os.path.join(data_directory, "config.yaml")
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            config = yaml.safe_load(file) or {}
    else:
        config = {}


class PathType(Enum):
    USER = auto()
    APPLICATION = auto()
    SYSTEM = auto()

def recommend_path(path_type: PathType) -> Optional[str]:
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

def encrypt_data_aes_gcm(data_to_encrypt, key, nonce):
    """
    Encrypts data using AES in GCM mode with a strong key derived from a passphrase.

    Args:
        data_to_encrypt (bytes): Data to encrypt.

    Returns:
        dict: A dictionary with the encrypted data, nonce, and tag.
    """
    # Ensure your data to encrypt is in bytes
    if not isinstance(data_to_encrypt, bytes):
        raise TypeError("The data to encrypt must be in bytes.")
    
    # Generate a random 256-bit key for AES
    if key is None:
        key = os.urandom(32) # AES-256 for strong encryption

    # Generate a random nonce (96 bits is recommended for GCM)
    if nonce is None:
        nonce = urandom(12)

    # Create an AES-GCM Cipher object
    aesgcm = AESGCM(key)

    # Encrypt the data
    encrypted_data = aesgcm.encrypt(nonce, data_to_encrypt, None)

    # Return encrypted data along with nonce (needed for decryption)
    return {
        'encrypted_data': encrypted_data,
        'nonce': nonce,
        'key': key
    }

def decrypt_data_aes_gcm(encrypted_data, key, nonce):
    """
    Decrypts data encrypted using AES in GCM mode.

    Args:
        encrypted_data (bytes): The encrypted data to decrypt.
        key (bytes): The secret key used for encryption.
        nonce (bytes): The nonce used during the encryption.

    Returns:
        bytes: The original plaintext data.
    """
    # Create an AES-GCM Cipher object
    aesgcm = AESGCM(key)

    # Decrypt the data
    try:
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        return decrypted_data
    except Exception as e:
        # Handle decryption errors (e.g., tampering detected, incorrect key)
        print(f"An error occurred during decryption: {e}")
        return None

def generate_rsa_key_pair(key_size=2048):
    """
    Generate an RSA key pair.

    Args:
        key_size (int): The key size in bits. Common sizes include 2048 and 4096 bits.

    Returns:
        tuple: A tuple containing the private key and public key in PEM format.
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    # Generate public key
    public_key = private_key.public_key()

    # Serialize private key to PEM format
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # Use BestAvailableEncryption for encrypted keys
    )

    # Serialize public key to PEM format
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem_private_key, pem_public_key

def encrypt_data_rsa(data, public_key):
    """
    Encrypt data using an RSA public key.

    Args:
        data (bytes): The data to encrypt.
        public_key (bytes): The RSA public key in PEM format.

    Returns:
        bytes: The encrypted data.
    """
    # Load the public key
    public_key = serialization.load_pem_public_key(public_key, backend=default_backend())

    # Encrypt the data
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data

def decrypt_data_rsa(encrypted_data, private_key):
    """
    Decrypt data using an RSA private key.

    Args:
        encrypted_data (bytes): The encrypted data.
        private_key (bytes): The RSA private key in PEM format.

    Returns:
        bytes: The decrypted data.
    """
    # Load the private key
    private_key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())

    # Decrypt the data
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_data

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
    return config

def set_config(new_config):
    global config
    config = new_config
    write_config()

# Write the updated configuration back to config.yaml
def write_config():
    data.ensure_parent_directory_exists(config_file_path)
    with open(config_file_path, 'w') as file:
        try:
            yaml.dump(config, file)
            print(f'Configuration updated and saved to {config_file_path}.')
        except Exception as e:
            print(f'Error writing configuration to {config_file_path}: {e}')

# Function to recursively update the config dictionary with any missing keys/values
def update_config(target, updates):
    changed = False
    for key, value in updates.items():
        if target is None:
            target = {}
        if key is None:
            continue
        elif key not in target:
            target[key] = value
            changed = True
        elif isinstance(value, dict):
            target[key] = update_config(target.get(key, {}), value)
    if changed:
        write_config()
    return target

initialize_config()