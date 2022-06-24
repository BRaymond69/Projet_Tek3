#!/bin/python3

import base64 as b64
import requests as req
from local_challs import aes_pad, aes_unpad, InputError

class CryptoError(Exception):
    def __init__(self, message):
        self.message = message

def get_data(session, url):
    return session.get("http://" + url).text.encode("utf-8")

def post_data(session, url, data):
    return b64.b64decode(session.post("http://" + url, data=b64.b64encode(data)).text.encode("utf-8"))

def post_2_data(session, url, data1, data2):
    return b64.b64decode(session.post("http://" + url, data=b64.b64encode(data1) + b"\n" + b64.b64encode(data2)).text.encode("utf-8"))

def to_blocks(data, block_size=16):
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def get_aes_block_size(session, url):
    first_len = len(post_data(session, url, b"#"))
    new_len = first_len
    offset = 1

    while new_len == first_len:
        offset += 1
        new_len = len(post_data(session, url, b"#" * offset))

    block_size = new_len - first_len
    return block_size, offset

def challenge10(url):
    """ Break ECB secret string byte by byte """
    # Initialise new session to remember the cookies
    session = req.Session()

    block_size, _ = get_aes_block_size(session, url)

    # Check if the encryption we are attacking is ECB
    ecb_test = to_blocks(post_data(session, url, b"#" * 2 * block_size), block_size=block_size)
    if not ecb_test[0] == ecb_test[1]:
        raise CryptoError("The encryption we are breaking is not AES ECB")

    # Byte by Byte ECB decryption
    secret_word = b""
    cracked_len = 0
    offset = block_size * 5
    checked_block = 4
    while True:
        # This payload will have 1 unkown caracter at the end that we will search
        payload = b"#" * (offset - 1 - cracked_len)
        blocks = to_blocks(post_data(session, url, payload), block_size=block_size)
        if len(blocks) - 1 == checked_block:
            break
        expected_block = blocks[checked_block]
        payload += secret_word
        found = False
        for tested_byte in range(0x100):
            curr_block = to_blocks(post_data(session, url, payload + bytes([tested_byte])), block_size=block_size)[checked_block]
            if curr_block == expected_block:
                secret_word += bytes([tested_byte])
                found = True
                break
        if not found:
            break
        cracked_len = len(secret_word)

    return [b64.b64encode(secret_word).decode("utf-8")]

def challenge11(url):
    """ Forge ECB login token """
    session = req.Session()
    role_blocks = to_blocks(post_data(session, url + '/new_profile', b"A" * 13))[:2]
    admin_payload = b"A" * 10 + aes_pad(b"admin", block_size=16)
    admin_block = to_blocks(post_data(session, url + '/new_profile', admin_payload))[1]

    validated_token = post_data(session, url + '/validate', b"".join(role_blocks + [admin_block]))
    return [b64.b64encode(validated_token).decode("utf-8")]

def challenge12(url):
    """ Crack ECB secret string with a random prefix """
    session = req.Session()

    block_size, _ = get_aes_block_size(session, url)

    def get_frequencies(l):
        return {e: l.count(e) for e in l}

    # Find an offset that gets 2 similar blocks
    base_duplicates = max(get_frequencies(to_blocks(post_data(session, url, b""), block_size=block_size)).values())
    current_duplicates = base_duplicates

    offset = 1
    while current_duplicates == base_duplicates:
        blocks = to_blocks(post_data(session, url, b"#" * offset), block_size=block_size)
        current_duplicates = max(get_frequencies(blocks).values())
        offset += 1

    # Quick and dirty way of getting the repeated block position
    target_block = 0
    old_block = None
    for b in blocks:
        if old_block == b:
            break
        old_block = b
        target_block += 1

    # Byte by Byte ECB decryption
    secret_word = b""
    cracked_len = 0
    offset -= 1
    while True:
        # This payload will have 1 unkown caracter at the end that we will search
        payload = b"#" * (offset - 1 - cracked_len)
        blocks = to_blocks(post_data(session, url, payload), block_size=block_size)
        expected_block = blocks[target_block]
        payload += secret_word
        found = False
        for tested_byte in range(0x100):
            curr_block = to_blocks(post_data(session, url, payload + bytes([tested_byte])), block_size=block_size)[target_block]
            if curr_block == expected_block:
                secret_word += bytes([tested_byte])
                found = True
                break
        if not found:
            break
        if len(blocks) - 1 == target_block:
            break
        cracked_len = len(secret_word)

    return [b64.b64encode(secret_word[:-1]).decode("utf-8")]

def challenge13(url):
    """ AES CBC Bit flipping attack """
    session = req.Session()

    # Compute block size and prefix size
    block_size, padding = get_aes_block_size(session, url + "/encrypt")

    blocks_a = to_blocks(post_data(session, url + "/encrypt", b"A"), block_size=block_size)
    blocks_b = to_blocks(post_data(session, url + "/encrypt", b"B"), block_size=block_size)
    offset = 0
    while blocks_a[offset] == blocks_b[offset]:
        offset += 1
    offset += 1

    # Forge the ;admin=true; by flipping the bits of an encrypted block
    payload = b"A" * (3 * block_size)
    building_blocks = to_blocks(post_data(session, url + "/encrypt", payload), block_size=block_size)

    cipher_block = building_blocks[offset]
    plaintext_block = b"A" * block_size
    forged_string = b";admin=true;"

    new_cipher_block = b""
    for i in range(len(forged_string)):
        new_cipher_block += bytes([cipher_block[i] ^ plaintext_block[i] ^ forged_string[i]])
    new_cipher_block += cipher_block[len(forged_string):]
    building_blocks[offset] = new_cipher_block

    # Sending the forged block in /decrypt
    payload = b"".join(building_blocks)
    token = post_data(session, url + "/decrypt", payload)

    return [b64.b64encode(token).decode("utf-8")]

def challenge14(url):
    """ AES CBC Padding oracle attack """
    session = req.Session()

    # Getting the encrypted data we want to decrypt
    input_data = get_data(session, url + "/encrypt").split(b"\n")
    if len(input_data) != 2:
        raise InputError("Invalid input (missing a \\n to seperate iv and ciphertext)")

    iv = b64.b64decode(input_data[0])
    cypher_text = b64.b64decode(input_data[1])
    blocks = to_blocks(cypher_text)

    # Generating block pairs to decrypt the data block by block
    prev_block = iv
    block_pairs = []
    for curr_block in blocks:
        block_pairs += [[prev_block, curr_block]]
        prev_block = curr_block

    def xor_padding(byte_string):
        padding = len(byte_string) + 1
        return [b ^ padding for b in byte_string]

    msg = b""
    for block_pair in block_pairs:
        # Get int array from a byte array
        crafted_block = [b for b in block_pair[0]]
        target_block = block_pair[1]
        decrypted_block = b""
        decrypted_keys = b""

        for i in range(len(crafted_block))[::-1]:
            original_byte = crafted_block[i]
            key = original_byte ^ (len(decrypted_keys) + 1)
            crafted_block = crafted_block[:i + 1] + xor_padding(decrypted_keys)

            for test_byte in range(0x100):
                crafted_block[i] = test_byte
                payload = bytes(crafted_block) + target_block
                if test_byte != original_byte and post_2_data(session, url + "/decrypt", iv, payload) == b"OK":
                    key = test_byte ^ (len(decrypted_keys) + 1)
                    break

            decrypted_keys = bytes([key]) + decrypted_keys
            decrypted_block = bytes([key ^ original_byte]) + decrypted_block

        msg += decrypted_block

    return [b64.b64encode(aes_unpad(msg)).decode("utf-8")]
