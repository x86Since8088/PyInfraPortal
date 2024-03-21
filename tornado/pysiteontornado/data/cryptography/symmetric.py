from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import ec


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
        key = PySiteConfig['AESGCM']['KEY']
    if key is None:
        key = os.urandom(32) # AES-256 for strong encryption

    # Generate a random nonce (96 bits is recommended for GCM)
    if nonce is None:
        nonce = os.urandom(12)

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
