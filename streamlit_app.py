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


def process_seed_phrases(seed_phrases):
    with multiprocessing.Pool() as pool:
        results = pool.imap_unordered(process_seed_phrase, seed_phrases)
        return list(results)

# Define the function to generate a private key from a seed phrase and derivation path
def generate_private_key(seed_phrase, derivation_path):
    seed = hashlib.pbkdf2_hmac('sha512', seed_phrase.encode('utf-8'), b'Bitcoin seed', 2048)
    master_key = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    child_key = hmac.new(master_key[32:], b'\x00' + master_key[:32] + derivation_path.encode('utf-8'), hashlib.sha512).digest()
    return child_key[:32]

def process_seed_phrase(seed_phrase):
    private_key = generate_private_key(seed_phrase, "m/44'/0'/0'")
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
    return seed_phrase, address

def file_download(results):
    # Extract the seed phrases and addresses from the results
    seed_phrases, addresses = zip(*results)
    # Create a DataFrame from the seed phrases and addresses
    df = pd.DataFrame({"seed_phrase": seed_phrases, "address": addresses})
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="seed_address.csv">Download CSV file</a>'
    return href


def main():
    st.title("BA Generator")
    st.sidebar.title("Settings")

    # Get the number of files and seed phrases from the sidebar
    number_files = st.sidebar.number_input("Number of Files", value=200, min_value=1, step=1)
    num_seed_phrases = st.sidebar.number_input("Number of Seed Phrases", value=1000000, min_value=1, step=100000)
    chunk_size = st.sidebar.number_input("Number of Chunk size", value=1000000, min_value=1, step=1)



    if st.button("Generate BA"):
        progress_bar = st.progress(0)
        with st.spinner("Generating BAs..."):
            # Initialize the Mnemonic class
            mnemonic = Mnemonic("english")
            for i in range(number_files):
                start_time = time.time()
                # Generate a list of seed phrases
                seed_phrases = [mnemonic.generate() for _ in range(num_seed_phrases)]
                # Use ProcessPoolExecutor for parallel processing
                with ProcessPoolExecutor() as executor:
                    #futures = []
                    # Submit tasks for Bitcoin address generation
                    for j in range(0, num_seed_phrases, chunk_size):
                        chunk = seed_phrases[j: j + chunk_size]
                        #results = process_seed_phrases(chunk)
                        results = process_seed_phrases(chunk)

                        # Process and save any remaining results
                        if results:
                           #process_and_save_results(results, i+1)
                           st.markdown(file_download(results), unsafe_allow_html=True)



                end_time = time.time()
                elapsed_time = end_time - start_time

                st.write(f"File {i + 1}/{number_files} saved. Elapsed time: {elapsed_time:.2f} seconds")

                progress_bar.progress((i + 1) / number_files)
                # Perform cleanup
                del elapsed_time, start_time, end_time, seed_phrases, chunk,results #completed_futures,futures,
                gc.collect()

        st.success("BA generation complete!")


if __name__ == '__main__':
    main()
    gc.collect()
