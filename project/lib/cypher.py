import _io
import argparse
from string import ascii_lowercase

from typing import Tuple


def IOwrapper(method):
    def wrapper(*args):
        args[0]._Cypher__read(args[0]._Cypher__inputFile)
        method(args[0])
        args[0]._Cypher__write(args[0]._Cypher__outputFile)
    return wrapper


class Cypher:
    def __init__(self, input_arg: argparse.FileType('r'), output_arg: argparse.FileType('w')):
        self.__caesarSecret = None
        self.__vernamSecret = None
        self.__rsaSecret = None
        self.__mode = None
        self.__inputFile = input_arg
        self.__outputFile = output_arg

    def __del__(self):
        self.__inputFile.close()
        self.__outputFile.close()

    def load(self, mode: str, caesar: int, vernam: str, rsa: Tuple[int, int]):
        self.__caesarSecret = caesar
        self.__vernamSecret = vernam.lower()
        self.__rsaSecret = rsa
        self.__mode = mode

    @IOwrapper
    def encrypt(self):
        self.__transform(True)

    @IOwrapper
    def decrypt(self):
        self.__transform(False)

    @IOwrapper
    def crack(self):
        self.__crack()

    def __transform(self, is_encryption: bool):
        if self.__mode == 'Caesar':
            self.__outputText = self.__caesar(is_encryption, self.__caesarSecret)
        elif self.__mode == 'Vernam':
            self.__outputText = self.__vernam(is_encryption, self.__vernamSecret)
        elif self.__mode == 'RSA':
            self.__outputText = self.__rsa(is_encryption, self.__rsaSecret)
        else:
            raise "Unknown encryption mode"

    def __caesar(self, is_encryption: bool, offset: int) -> str:
        operation = (lambda x, y: x + y) if is_encryption else (lambda x, y: x - y)
        output = ""
        for char in self.__inputText:
            letter = char
            if char.lower() in ascii_lowercase:
                letter = ascii_lowercase[operation(ascii_lowercase.index(char.lower()), offset) % 26]
                if char.isupper():
                    letter = letter.upper()
            output += letter
        return output

    def __vernam(self, is_encryption: bool, secret: str) -> str:
        operation = (lambda x, y: x + y) if is_encryption else (lambda x, y: x - y)
        output = ""
        for i, char in enumerate(self.__inputText):
            letter = char.lower()
            if letter in ascii_lowercase:
                open_pos = ascii_lowercase.index(letter)
                secret_pos = ascii_lowercase.index(secret[i % len(secret)])
                letter = ascii_lowercase[operation(open_pos, secret_pos) % 26]
            if char.isupper():
                letter = letter.upper()
            output += letter
        return output

    def __rsa(self, is_encryption: bool, key_pair: Tuple[int, int]) -> str:
        output = ""
        if is_encryption:
            for char in self.__inputText:
                output += hex(pow(ord(char), key_pair[0], key_pair[1])) + ' '
        else:
            self.__inputText = tuple(map(lambda number: int(number, 16), self.__inputText.split()))
            for number in self.__inputText:
                output += chr(pow(number, key_pair[0], key_pair[1]))
        return output

    def __crack(self):
        frequencies = {letter: 0 for letter in ascii_lowercase}
        for char in self.__inputText:
            char = char.lower()
            if char in ascii_lowercase:
                frequencies[char] += 1
        pairs = sorted(tuple(frequencies.items()), key=lambda pair: pair[1], reverse=True)
        self.__outputText = "Here are all possible variants ordered by probability:\n\n" + '-' * 100 + "\n"

        # English letters ordered by frequencies in real texts
        for i, attempt in enumerate('etaoinhsrdlcmuwfgypbvkjxqz'):
            offset = ascii_lowercase.index(pairs[0][0]) - ascii_lowercase.index(attempt)
            decoded = self.__caesar(False, offset)
            self.__outputText += "Attempt #{NUMBER} (offset = {OFFSET}):\n\n{TEXT}\n\n".format(NUMBER=str(i),
                                                                                               OFFSET=str(offset),
                                                                                               TEXT=decoded) +\
                '-' * 100 + "\n"

    def __read(self, source: _io.TextIOWrapper):
        self.__inputText = self.__outputText = source.read()
        source.seek(0)  # Return carriage to the beginning of the file

    def __write(self, destination: _io.TextIOWrapper):
        print(self.__outputText, file=destination)
        destination.flush()  # Push written text into the file without closing
