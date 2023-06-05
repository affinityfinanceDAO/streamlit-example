import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,as_completed
from mnemonic import Mnemonic
import hashlib
import hmac
import base58
import base64
import ecdsa
import multiprocessing
from pathos.multiprocessing import ProcessPool
import bitcoin as btc
import concurrent.futures
import os
import time
import random
import gc


class BAparallel:
    @staticmethod
    def generate_private_key(seed_phrase, derivation_path):
        seed = hashlib.pbkdf2_hmac('sha512', seed_phrase.encode('utf-8'), b'Bitcoin seed', 2048)
        master_key = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        child_key = hmac.new(master_key[32:], b'\x00' + master_key[:32] + derivation_path.encode('utf-8'),
                             hashlib.sha512).digest()
        return child_key[:32]

    @staticmethod
    def process_seed_phrase(seed_phrase):
        private_key = BAparallel.generate_private_key(seed_phrase, "m/44'/0'/0'")
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b"\x04" + vk.to_string()
        ripemd160 = hashlib.new("ripemd160")
        ripemd160.update(hashlib.sha256(public_key).digest())
        hash160 = ripemd160.digest()
        version = b"\x00"
        payload = version + hash160
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        address = base58.b58encode(payload + checksum).decode("utf-8").lower()
        #address = "1dw9ztejmrmj1emh1dieldjpkeck2jebm6"
        return seed_phrase, address

    @staticmethod
    def process_seed_phrases(seed_phrases):
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(BAparallel.process_seed_phrase, seed_phrases)
            return list(results)
