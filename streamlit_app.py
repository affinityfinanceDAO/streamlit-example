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
from class_app import BAparallel



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
    number_files = st.sidebar.number_input("Number of Files", value=50, min_value=1, step=1)
    num_seed_phrases = st.sidebar.number_input("Number of SPs", value=25000, min_value=1, step=100000)
    chunk_size = st.sidebar.number_input("Number of Chunk size", value=25000, min_value=1, step=1)
    if st.button("Generate BA"):
        progress_bar = st.progress(0)
        with st.spinner("Generating BAs..."):
            mnemonic = Mnemonic("english")
            for i in range(number_files):
                start_time = time.time()
                with ProcessPoolExecutor() as executor:
                    futures = []
                    for j in range(0, num_seed_phrases, chunk_size):
                        chunk = [mnemonic.generate() for _ in range(chunk_size)]
                        future = BAparallel2.process_seed_phrases(chunk)
                        results = []
                        for result in future:
                            results.extend(result)
                        if results:
                           st.markdown(file_download(results), unsafe_allow_html=True)
                end_time = time.time()
                elapsed_time = end_time - start_time
                st.write(f"File {i + 1}/{number_files} saved. Elapsed time: {elapsed_time:.2f} seconds")
                progress_bar.progress((i + 1) / number_files)
                del elapsed_time, start_time, end_time, chunk,results ,completed_futures,futures,
                gc.collect()

        st.success("BA generation complete!")


if __name__ == '__main__':
    main()
    gc.collect()
