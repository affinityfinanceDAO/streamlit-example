import streamlit as st
import sys
import hashlib, base58
from coincurve.keys import PublicKey
import os



def getAddress(pub_key_hashed_bytes):
    fullkey = b"\x00" + pub_key_hashed_bytes
    sha256a = hashlib.sha256(fullkey).digest()
    sha256b = hashlib.sha256(sha256a).digest()
    checksum = sha256b[:4]
    return base58.b58encode(fullkey+checksum).decode()



def getPubKeyFaster(priv_key_bytes):
    return PublicKey.from_valid_secret(priv_key_bytes)


def getPubKeyFullUncompressedFaster(pub_key_bytes):
    return pub_key_bytes.format(compressed=False)


def getPubKeyFullCompressedFaster(pub_key_bytes):
    return pub_key_bytes.format(compressed=True)

# Perform SHA-256 and RipeMD160 hash functions
def getPubKeyHashed(pub_key_full_bytes):
    sha256 = hashlib.sha256(pub_key_full_bytes).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    return ripemd160.digest()


def getRawAddress(bitcoinAddress):
    try:
        hex = base58.b58decode(bitcoinAddress)
        return hex[1:len(hex) - 4]
    except ValueError:
        return None


def createHashedPubKeySetFromAddressList(filename):
    addressList = []
    with open(filename) as f:
        for line in f:
            address = line.strip('\n')
            rawAddress = getRawAddress(address)
            if rawAddress is not None:
                addressList.append(rawAddress)
    return set(addressList)


def searchInList(priv_key, hash160, rawAddressSet, compression):
    if hash160 in rawAddressSet:
        address = getAddress(hash160)
        message = 'YEAH! Address %s is %s and has a private key: %s' % (address, compression, priv_key.hex())
        st.write(message)



def seek(hash160Set):
    LOG_EVERY_N = 100000
    i = 0
    while True:
        i += 1
        priv_key = os.urandom(32)
        publ_key = getPubKeyFaster(priv_key)
        publ_key_uncompressed = getPubKeyFullUncompressedFaster(publ_key)
        hash160 = getPubKeyHashed(publ_key_uncompressed)
        searchInList(priv_key, hash160, hash160Set, 'uncompressed')
        publ_key_compressed = getPubKeyFullCompressedFaster(publ_key)
        hash160 = getPubKeyHashed(publ_key_compressed)
        searchInList(priv_key, hash160, hash160Set, 'compressed')
        if (i % LOG_EVERY_N) == 0:
            st.write('Total Scan:',  str(i))
            sys.stdout.flush()
            continue


def main():
    st.title("BA Search")
    addressFile = 'D://shiva//btc_folder2//addresses11.txt'
    if addressFile and st.button("Start Search"):
        hash160Set = createHashedPubKeySetFromAddressList(addressFile)
        st.write(f"File {addressFile} loaded, number of unique addresses: {len(hash160Set)}")
        seek(hash160Set)



if __name__ == "__main__":
    main()
