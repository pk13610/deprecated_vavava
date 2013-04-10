#! /usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Hash import HMAC

BLOCK_SIZE = 16
SIG_SIZE = SHA256.digest_size
VERSION = r'1.0.1'

def hashkey(k):
    """Hash a key"""
    sha = SHA256.new(k)
    return sha.digest()

def encryptsign_data(data, key):
    """Encrypt and sign a file"""
    key = hashkey(key)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pad = BLOCK_SIZE - len(data) % BLOCK_SIZE
    data = data + pad * chr(pad)
    data = iv + cipher.encrypt(data)
    sig = HMAC.new(key, data, SHA256).digest()
    return data + sig

def decryptsign_data(data, key):
    """Check signature and decrypt a file"""
    key = hashkey(key)
    sig = data[-SIG_SIZE:]
    data = data[:-SIG_SIZE]
    if HMAC.new(key, data, SHA256).digest() != sig:
        raise( "Authentication failed.")
    iv = data[:16]
    data = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = cipher.decrypt(data)
    return data[:-ord(data[-1])]

def encryptsign_file(file_name, password):
    fp = open(file_name, 'rb')
    if not fp:
        raise('File not exists:' + file_name)
    encrypted_file = open(file_name+'.encrypted', 'wb')
    encrypted_file.write(encryptsign_data(fp.read(), hashlib.md5(password).digest()))

def decryptsign_file(file_name, password):
    fp = open(file_name, 'rb')
    if not fp:
        raise('encrypted file not exists:' + file_name)
    decrypted_file = open(file_name+'.decrypted', 'wb')
    decrypted_file.write(decryptsign_data(fp.read(), hashlib.md5(password).digest()))

pwd = '2134adf'
pwd1 = '2134adf1111'
f = 'test.rmvb'
encryptsign_file( f, pwd)
print 'decrypt ....'
decryptsign_file( f+'.encrypted', pwd)
print 'ok'
