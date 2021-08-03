import hashlib
import os
import random
import re

VERSION = "0.0.1"
PEPER = list("_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
HASH_SYNTAX = r"[a-z0-9]{64,64}\$$"
KEY_SYNTAX = r"[a-zA-Z0-9]{8,}$"

class ProgressBar:
    def __init__(self, maxv, progress = 0, prefix = '[',
                sufix = ']', fill = '█', length = 30):
        self.progress = progress
        self.maxv = maxv
        self.prefix = prefix
        self.sufix = sufix
        self.fill = fill
        self.length = length
    def display(self):
        frac = self.progress / self.maxv
        count = int(self.length * frac)
        elements = (self.prefix
                    + self.fill * count
                    + ' ' * (self.length - count)
                    + self.sufix
                    + "   {}%".format(str(frac * 100)[:5]))
        print(''.join(elements), end = '\r')
    def update(self, addition):
        self.progress += addition
        self.display()

#clear screen
def clear():
    os.system("clear")

#print string out and wait for user response
def wait(string):
    print(string, end = '' if string == '' else '\n')
    input("Press ENTER to continue...")

#authentication of the key provided
def authen(key, enc_cont):
    hashed = enc_cont[0:65]
    if not re.match(HASH_SYNTAX, hashed):
        return False
    for char in PEPER:
        if hashed == hash_key(key, char) + '$':
            return True
    return False

#get key and return hash
def hash_key(key, peper = random.choice(PEPER)):
    key += "mi" + peper
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

#encrypt data using given key
def encrypt(ori_key, cont):
    enc_cont = []
    key = list(map(ord, list(ori_key)))
    key_index = 0
    length = len(key)
    prog_bar = ProgressBar(len(cont))
    for char in cont:
        enc_char = ord(char) ^ key[key_index]
        enc_cont.append(str(enc_char))
        key[key_index] = ord(char)
        key_index = (key_index + 1) % length
        prog_bar.update(1)
    print('\n')
    return hash_key(ori_key) + '$' + '&'.join(enc_cont)

#decrypt data using given key
def decrypt(key, enc_cont):
    enc_cont = enc_cont[65:].split('&')
    cont = []
    key = list(map(ord, list(key)))
    key_index = 0
    key_cycle = len(key)
    prog_bar = ProgressBar(len(enc_cont))
    for enc_char in enc_cont:
        char = int(enc_char) ^ key[key_index]
        cont.append(chr(char))
        key[key_index] = char
        key_index = (key_index + 1) % key_cycle
        prog_bar.update(1)
    print('\n')
    return ''.join(cont)

#main UI and error handling
while True:
    clear()
    print("\033[1mEasy Encrypt Engine\033[0m\n"
        + "version: " + VERSION
        + "\nThis is a program that can encrypt and unencrpt files. "
        + "The encryption method is simple, so, "
        + "please use it for low-level encryption only! \n"
        + "Operations: [e]ncrypt, [d]ecrypt, [r]ead, [q]uit")
    ope = input("Select a operation from above: ")
    if ope == 'q':
        break
    elif ope == '':
        continue
    elif ope in "der":
        path = input("Select target file: {}/".format(os.getcwd()))
        try:
            f = open(path,'r')
            ori = f.read()
        except FileNotFoundError:
            wait("Error: The file path you provided is invalid!")
            continue
        except UnicodeDecodeError:
            wait("Error: Unicode decode fail!")
            continue
        if ope == 'e':
            print("You need to set a unique key for target file. "
                + "The key must contain at least eight characters. "
                + "They can be capital letters, lowercase letters or numbers.")
            key = input("Key: ")
            if not re.match(KEY_SYNTAX, key):
                wait("The key does not reach minimum standard!")
                continue
            print("\033[FKey: {}\n".format('*' * len(key)))
            out = encrypt(key, ori)
        elif ope == 'd':
            print("You are trying to decrypt a file. "
                + "A key is needed for decryption. ")
            key = input("Key: ")
            if not authen(key, ori):
                wait("Invalid key or broken file!")
                continue
            print("\033[FKey: {}\n".format('*' * len(key)))
            print("Authentication success! Decrypting target file...")
            out = decrypt(key, ori)
        elif ope == 'r':
            print("↓ START ↓")
            print(ori)
            print("↑ FINISH ↑")
            wait('')
            continue
        f = open(path,'w')
        f.write(out)
        f.close()
        wait("File successfully saved!")
    else:
        wait("Invalid selection!")

clear()
