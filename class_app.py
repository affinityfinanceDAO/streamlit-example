import streamlit as st
import pandas as pd
from mnemonic import Mnemonic
import hashlib
import hmac
import base58
import base64
import ecdsa
import multiprocessing
import concurrent.futures
import os
import time
import random
import gc
from bip32utils import BIP32Key ,BIP32_HARDEN

class BAparallel:
    @staticmethod
    def process_root_key(seed_phrase):
        seed_bytes = memo.to_seed(seed_phrase)
        root_key_obj = BIP32Key.fromEntropy(seed_bytes)
        root_key = root_key_obj.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0)
        return root_key
    
    @staticmethod
    def process_seed_phrase(seed_phrase):
        root_key = BAparallel2.process_root_key(seed_phrase)
        results = []
        for index in range(4):
            child_key = root_key.ChildKey(index)
            address = child_key.Address().lower()
            results.append((seed_phrase, address))
        return results

    @staticmethod
    def process_seed_phrases(seed_phrases):
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(BAparallel.process_seed_phrase, seed_phrases)
            return list(results)
