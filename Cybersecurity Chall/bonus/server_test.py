#!/bin/python3

import base64 as b64
import random
from sys import argv
from http.server import HTTPServer, BaseHTTPRequestHandler
from Crypto.Cipher import AES

host = '127.0.0.1'
port = 5000
wordlist = 'words.txt'

def usage():
    print("usage: ./server_test.py <challenge id>")

def get_args():
    if len(argv) != 2:
        usage()
        exit(1)
    if not 10 <= int(argv[1]) <= 14:
        print("<challenge id> should be a number between 10 an 14")
        exit(1)
    return int(argv[1])

def get_random_word():
    try:
        with open(wordlist, 'r') as f:
            # Get all args without the \n in the end
            words = [l[:-1] for l in f.readlines()]
            choice = random.choice(words)
    except:
        choice = "CURVE"
    return choice

def aes_pad(msg, block_size=16):
    to_pad = bytes([block_size - len(msg) % block_size])
    return msg + to_pad * ord(to_pad)

def aes_unpad(msg):
    to_unpad = msg[-1]
    if all(b == to_unpad for b in msg[-to_unpad:]):
        return msg[:-to_unpad]
    return msg

def run(handler_class):
    httpd = HTTPServer((host, port), handler_class)
    print(f"Launching server on {host}:{port}")
    httpd.serve_forever()

# Inspired by https://gist.github.com/bradmontgomery/2219997
class Server_chall10(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")

        if self.headers.get("Cookie") == None:
            word = get_random_word().upper()
            print(f"Setting up word {word}")
            self.send_header("Set-Cookie", f"{word}")
        else:
            word = self.headers.get("Cookie")

        self.end_headers()
        return word.encode("utf-8")

    def _post_handler(self, user_input, random_word):
        secret_string = random_word
        key = b"--CRYPTOGRAPHY--"
        cipher = AES.new(key, AES.MODE_ECB)

        cypher_text = cipher.encrypt(aes_pad(b64.b64decode(user_input) + secret_string, block_size=16))

        return b64.b64encode(cypher_text)

    def do_POST(self):
        word = self._set_headers()
        if self.requestline.startswith("POST /challenge10 "):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            send_data = self._post_handler(post_data, word)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

def challenge10_server():
    run(Server_chall10)

class Server_chall11(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _post_new_profile(self, user_input):
        key = b"--CRYPTOGRAPHY--"
        cipher = AES.new(key, AES.MODE_ECB)
        profile = f"email={b64.b64decode(user_input).decode('utf-8')}&uid=10&role=user"

        cypher_text = cipher.encrypt(aes_pad(profile.encode("utf-8"), block_size=16))

        return b64.b64encode(cypher_text)

    def _post_validate(self, user_input):
        key = b"--CRYPTOGRAPHY--"
        cipher = AES.new(key, AES.MODE_ECB)

        login = aes_unpad(cipher.decrypt(b64.b64decode(user_input)))

        if login.endswith(b"&role=admin"):
            return b64.b64encode(b"YOU VALIDATED THE CHALL " + login)
        else:
            return b64.b64encode(b"FAILED TRY AGAIN " + login)

    def do_POST(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.requestline.startswith("POST /challenge11/new_profile "):
            send_data = self._post_new_profile(post_data)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

        if self.requestline.startswith("POST /challenge11/validate "):
            send_data = self._post_validate(post_data)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

def challenge11_server():
    run(Server_chall11)

class Server_chall12(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")

        if self.headers.get('Cookie') == None:
            rng = random.randint(3, 50)
            word = get_random_word().upper()
            self.send_header("Set-Cookie", f"{rng}|{word}")
        else:
            rng, word = self.headers.get("Cookie").split('|')
            rng = int(rng)

        self.end_headers()
        return rng, word.encode("utf-8")

    def _post_handler(self, user_input, rng, random_word):
        # Dont actually try to guess this
        random_prefix = bytes([random.choice(b"abcdefhijklmnopqrstuvwxyz") for i in range(rng)])
        secret_string = random_word
        key = b"--CRYPTOGRAPHY--"
        cipher = AES.new(key, AES.MODE_ECB)
        payload = random_prefix + b64.b64decode(user_input) + secret_string

        print("Encrypting", payload)
        cypher_text = cipher.encrypt(aes_pad(payload, block_size=16))

        return b64.b64encode(cypher_text)

    def do_POST(self):
        rng, word = self._set_headers()
        if self.requestline.startswith("POST /challenge12 "):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            send_data = self._post_handler(post_data, rng, word)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

def challenge12_server():
    run(Server_chall12)

def xor_bytes(lhs, rhs):
    return bytes([lhs[i] ^ rhs[i] for i in range(len(lhs))])

def to_blocks(data, block_size=16):
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

class Server_chall13(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")

        if self.headers.get('Cookie') == None:
            rng = random.randint(0, 50)
            self.send_header("Set-Cookie", f"{rng}")
        else:
            rng = int(self.headers.get("Cookie"))

        self.end_headers()
        return rng

    def _post_encrypt(self, user_input, rng):
        # Dont actually try to guess this
        random_title = b"D" * rng
        random_type = b"W" * (50 - rng)
        key = b"--CRYPTOGRAPHY--"
        iv  = b"-INITIALISATION-"
        cipher = AES.new(key, AES.MODE_ECB)
        user_input = b64.b64decode(user_input).replace(b";", b"").replace(b"=", b"")
        payload = b"title=" + random_title + b";content=" + user_input + b";type=" + random_type + b";"

        print("Encrypting", payload)
        payload = aes_pad(payload, block_size=16)
        blocks = to_blocks(payload)

        cypher_text = b""
        xor_key = iv
        for b in blocks:
            xored_block = xor_bytes(xor_key, b)
            new_block = cipher.encrypt(xored_block)
            cypher_text += new_block
            xor_key = new_block

        return b64.b64encode(cypher_text)

    def _post_decrypt(self, user_input):
        key = b"--CRYPTOGRAPHY--"
        iv  = b"-INITIALISATION-"
        cipher = AES.new(key, AES.MODE_ECB)
        blocks = to_blocks(b64.b64decode(user_input))

        if not all(len(block) == 16 for block in blocks):
            return b64.b64encode(b"FAILURE... YOU DIDN'T EVEN SEND ME BLOCKS OF THE CORRECT SIZE")

        msg = b""
        xor_key = iv
        for b in blocks:
            deciphered = cipher.decrypt(b)
            msg += xor_bytes(xor_key, deciphered)
            xor_key = b

        msg = aes_unpad(msg)

        if b";admin=true;" in msg:
            return b64.b64encode(b"SUCCESS!!! " + msg)
        else:
            return b64.b64encode(b"FAILURE, TRY AGAIN " + msg)

    def do_POST(self):
        rng = self._set_headers()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.requestline.startswith("POST /challenge13/encrypt "):
            send_data = self._post_encrypt(post_data, rng)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

        if self.requestline.startswith("POST /challenge13/decrypt "):
            send_data = self._post_decrypt(post_data)
            print(f"Got {post_data} -> Sent {send_data}")
            self.wfile.write(send_data)

def challenge13_server():
    run(Server_chall13)

class Server_chall14(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _get_handler(self):
        # Dont actually try to guess this
        random_iv = bytes([random.choice(b"abcdefhijklmnopqrstuvwxyz") for i in range(16)])
        word = get_random_word().upper()
        key = b"--CRYPTOGRAPHY--"
        iv  = random_iv
        cipher = AES.new(key, AES.MODE_ECB)
        payload = f"""Here is some info about the word \"{word}\",
it is {len(word)} characters long and starts with a {word[0]}.
If you are reading this you probably already cleared the challenge :D""".encode("utf-8")

        payload = aes_pad(payload, block_size=16)
        print("Encrypting", payload)
        blocks = to_blocks(payload)

        cypher_text = b""
        xor_key = iv
        for b in blocks:
            xored_block = xor_bytes(xor_key, b)
            new_block = cipher.encrypt(xored_block)
            cypher_text += new_block
            xor_key = new_block

        return  b64.b64encode(random_iv) + b"\n" + b64.b64encode(cypher_text)

    def _post_handler(self, user_input):
        if len(user_input.split(b"\n")) != 2:
            return b64.b64encode(b"Invalid input (missing a \\n to seperate iv and ciphertext)")

        iv, cypher_text = list(map(b64.b64decode, user_input.split(b"\n")))
        key = b"--CRYPTOGRAPHY--"
        cipher = AES.new(key, AES.MODE_ECB)
        blocks = to_blocks(cypher_text)

        if not all(len(block) == 16 for block in blocks):
            return b64.b64encode(b"Invalid input")

        msg = b""
        xor_key = iv
        for b in blocks:
            deciphered = cipher.decrypt(b)
            msg += xor_bytes(xor_key, deciphered)
            xor_key = b

        pad_byte = msg[-1]
        if not pad_byte <= 16 or not all(b == pad_byte for b in msg[-pad_byte:]):
            return b64.b64encode(b"Bad padding")

        return b64.b64encode(b"OK")

    def do_GET(self):
        self._set_headers()

        if self.requestline.startswith("GET /challenge14/encrypt "):
            send_data = self._get_handler()
            print(f"Sent {send_data}")
            self.wfile.write(send_data)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.requestline.startswith("POST /challenge14/decrypt "):
            send_data = self._post_handler(post_data)
            print(f"Got {post_data} -> Sent {send_data}")
            if b64.b64decode(send_data) == b"OK":
                self._set_headers(status_code=200)
            else:
                self._set_headers(status_code=500)
            self.wfile.write(send_data)

def challenge14_server():
    run(Server_chall14)

if __name__ == '__main__':
    chall_id = get_args()
    challenge_server = {
        10: challenge10_server,
        11: challenge11_server,
        12: challenge12_server,
        13: challenge13_server,
        14: challenge14_server
    }[chall_id]

    challenge_server()
