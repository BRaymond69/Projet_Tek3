#!/bin/python3

import base64 as b64
from math import ceil
from Crypto.Cipher import AES

class InputError(Exception):
    def __init__(self, message):
        self.message = message

def assert_hex(hex_str):
    hex_charset = "0123456789abcdef"
    if len(hex_str) == 0:
        raise InputError("Expected a hexadecimal string rather than nothing")
    if len(hex_str) % 2 or not all(c in hex_charset for c in hex_str.lower()):
        raise InputError("Invalid hexstring as input")

def challenge01(args):
    """ Hex string to base64 """
    inp = args[0]
    assert_hex(inp)
    return [b64.b64encode(bytes.fromhex(inp)).decode("utf-8")]

def challenge02(args):
    """ Xor 2 hex strings """
    map(assert_hex, args)
    lhs, rhs = list(map(bytes.fromhex, args))
    if len(lhs) != len(rhs):
        raise InputError("Expected two arguments of the same length")
    out = b""
    for i in range(len(lhs)):
        out += bytes([lhs[i] ^ rhs[i]])
    return [out.hex().upper()]

def challenge03(args):
    """ Break single byte XOR using letter frequency """
    inp = args[0]
    assert_hex(inp)
    inp = bytes.fromhex(inp)

    # Get each byte frequency
    frequencies = {}
    for b in inp:
        if b in frequencies:
            frequencies[b] += 1
        else:
            frequencies[b] = 1

    # Find the key using the most frequent letters of the english language
    frequent_english_letters = "etaoinshrdlu "
    # Take the 7 most frequent bytes from the input
    sorted_frequencies = sorted(frequencies.items(), key=lambda kv: kv[1], reverse=True)[:7]

    def score_letter(letter, input_byte):
        # Get the theoretical key for the letter
        key = ord(letter) ^ input_byte
        # The top 7 most common letters decrypted using the previous key
        generated_xored_letters = [chr(bs[0] ^ key) for bs in sorted_frequencies]
        # Adding +1 of score for each letter present in the most frequent english letters
        score = sum([l in frequent_english_letters for l in generated_xored_letters])

        return (score, key)

    best_score = 0
    key = 0
    for b in sorted_frequencies:
        # Get the best score with each of the most frequent letters
        # will test with ('e' ^ most_common_byte) ('t' ^ most_common_byte) ...
        curr_score = max([score_letter(l, b[0]) for l in frequent_english_letters])
        if curr_score[0] > best_score:
            best_score = curr_score[0]
            key = curr_score[1]

    return [bytes([key]).hex().upper()]

def challenge04(args):
    """ Find the input that corresponds to an english sentence and break it's XOR """
    map(assert_hex, args)
    byte_strings = list(map(bytes.fromhex, args))

    best_bs = b""
    best_odds = 0
    best_line = 0
    for line_number, bs in enumerate(byte_strings):
        frequencies = {}
        for b in bs:
            if b in frequencies:
                frequencies[b] += 1
            else:
                frequencies[b] = 1
        odds = max(kv[1] for kv in frequencies.items())
        if odds > best_odds:
            best_odds = odds
            best_bs = bs
            best_line = line_number

    return [' '.join([str(best_line)] + challenge03([best_bs.hex()]))]

def challenge05(args):
    """ Repeating key XOR encryption """
    key = args[0]
    inp = args[1]

    # edge case
    if inp == "":
        return [""]

    # generate repeated key string of the same length as the text
    # if input is 'aaaaaaaa' and key is 'key'
    # key will be 'keykeyke'
    key = (ceil(len(inp) / len(key)) * key)[:len(inp)]

    return challenge02([inp, key])

def challenge06(args, debug=False):
    """ Breaking repeating key XOR encryption """
    assert_hex(args[0])
    inp = bytes.fromhex(args[0])

    hamming_dist_lookup_table = [bin(i).count('1') for i in range(0x100)]
    def hamming_dist(lhs, rhs):
        xored_inputs = challenge02([lhs.hex(), rhs.hex()])[0]
        return sum([hamming_dist_lookup_table[b] for b in bytes.fromhex(xored_inputs)])

    lowest_score = 0xff
    best_keylen = 0
    for keylen in range(5, 40):
        score = hamming_dist(inp[0:keylen * 2], inp[keylen * 2:keylen * 4]) / (keylen * 2)

        # Added a tolerance margin, if the score differs by less than 0.15
        # we ignore it as it is probably a multiple of the real key
        if score < lowest_score and lowest_score - score > 0.1:
            lowest_score = score
            best_keylen = keylen

    def get_key_for_keylen(keylen):
        keyed_alike_chunks = []
        # Ugly way of doing a do while, but it works
        while True:
            xored_chunks = [inp[i:i + keylen] for i in range(0, len(inp), keylen)]
            keyed_alike_chunks = list(map(list, zip(*xored_chunks[:-1])))
            if len(keyed_alike_chunks) != keylen:
                # If we end up with less chunks than the number of expected key lenght,
                # we should probably pick a lower length
                keylen = int(keylen / 2)
            else:
                break

        # Get the key for each block and add them up
        return sum(map(lambda chunk: challenge03([bytes(chunk).hex()]), keyed_alike_chunks), [])

    key = get_key_for_keylen(best_keylen)
    if debug:
        print(bytes.fromhex("".join(key)))
    if len(key) % 2 == 0:
        # Check if the key can be simplified
        split = int(len(key) / 2)
        while key[:split] == key[split:]:
            key = key[:split]
            if split % 2:
                break
            split = int(split / 2)
    return ["".join(key)]

def aes_pad(msg, block_size=16):
    to_pad = bytes([block_size - len(msg) % block_size])
    return msg + to_pad * ord(to_pad)

def aes_unpad(msg):
    to_unpad = msg[-1]
    if all(b == to_unpad for b in msg[-to_unpad:]):
        return msg[:-to_unpad]
    return msg

def challenge07(args):
    """ AES ECB decryption """
    assert_hex(args[0])
    key = bytes.fromhex(args[0])
    cyphertext = b64.b64decode(args[1])

    cipher = AES.new(key, AES.MODE_ECB)

    msg = aes_unpad(cipher.decrypt(cyphertext))
    return [b64.b64encode(msg).decode("utf-8")]

def challenge08(args):
    """ AES ECB detection """
    cypher_texts = list(map(b64.b64decode, args))
    if len(cypher_texts) == 0:
        return ["0"]

    best_bet = 0
    best_score = 0
    for line_number, ct in enumerate(cypher_texts):
        blocks = [ct[i:i + 16] for i in range(0, len(ct), 16)]

        frequencies = {}
        for b in blocks:
            if b in frequencies:
                frequencies[b] += 1
            else:
                frequencies[b] = 1

        score = max(kv[1] for kv in frequencies.items())
        if score > best_score:
            best_score = score
            best_bet = line_number

    return [str(best_bet + 1)]

def challenge09(args):
    """ AES CBC decryption """
    assert_hex(args[0])
    assert_hex(args[1])
    key = bytes.fromhex(args[0])
    iv = bytes.fromhex(args[1])
    if len(iv) != 16:
        raise InputError("Initialisation vector should be exactly 16 bytes of length")
    cypher_text = b64.b64decode(args[2])
    blocks = [cypher_text[i:i + 16] for i in range(0, len(cypher_text), 16)]
    cipher = AES.new(key, AES.MODE_ECB)

    msg = b""
    xor_key = iv
    for b in blocks:
        # To decrypt 1 block you pass it to the ECB decryption and
        # xor the output with the previous block
        # The first block will be the only one using an initialisation vector

        # This should probably raise an Error, but unsure due to the example input
        if len(b) != 16:
            break
        xored_input = cipher.decrypt(b)
        decrypted_block = bytes.fromhex(challenge02([xored_input.hex(), xor_key.hex()])[0])
        xor_key = b
        msg += decrypted_block

    return [b64.b64encode(msg).decode("utf-8")]
