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
                        #results = BAparallel.process_seed_phrases(chunk)
                        results = BAparallel.process_seed_phrases(chunk)

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
