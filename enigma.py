#!/usr/bin/env python
#
#   Mappings
#
#     Entry       = ABCDEFGHIJKLMNOPQRSTUVWXYZ (rotor right side)
#                   ||||||||||||||||||||||||||
#     I           = EKMFLGDQVZNTOWYHXUSPAIBRCJ
#     II          = AJDKSIRUXBLHWTMCQGZNPYFVOE
#     III         = BDFHJLCPRTXVZNYEIWGAKMUSQO
#     IV          = ESOVPZJAYQUIRHXLNFTGKDCMWB
#     V           = VZBRGITYUPSDNHLXAWMJQOFECK
#     Reflector B = YRUHQSLDPXNGOKMIEBFZCWVJAT
#     Reflector C = FVPJIAOYEDRZXWGCTKUQSBNMHL
#
#     I   - Q - If rotor steps from Q to R, the next rotor is advanced
#     II  - E - If rotor steps from E to F, the next rotor is advanced
#     III - V - If rotor steps from V to W, the next rotor is advanced
#
#   References
#
#     https://en.wikipedia.org/wiki/Enigma_rotor_details
#

#   TODO
#
#     * specify rotor order
#     * specify reflector
#

from dataclasses import dataclass, field


@dataclass
class Keyboard:
    pass


@dataclass
class RotorBase:
    alphas: str
    rotor: list = field(default_factory=list)

    def __post_init__(self):
        self.rotor = list(zip(list(self.alphabet()), list(self.alphas)))

    @staticmethod
    def alphabet():
        for i in range(ord("A"), ord("Z") + 1):
            yield chr(i)


@dataclass
class Rotor(RotorBase):
    notch_key: str = ""

    def find_key(self, key, direction=None):
        for value in self.rotor:
            if (direction == "rtl") and (value[0] == key):
                return value[1]
            if (direction == "ltr") and (value[1] == key):
                return value[0]
        raise KeyError

    def encode(self, key, direction=None, rotate=False):
        key_next = self.find_key(key, direction=direction)

        if rotate:
            self.rotate()

        return key_next, self.rotate_next_rotor(direction)

    def rotate(self):
        self.rotor.insert(0, self.rotor.pop())

    def rotate_next_rotor(self, direction):
        if direction == "ltr":
            return False
        return self.rotor[0][0] == self.notch_key

    def __repr__(self):
        return str(self.rotor)


@dataclass
class Reflector(RotorBase):
    def encode(self, key):
        for value in self.rotor:
            if value[0] == key:
                return value[1]
        raise KeyError


@dataclass
class Plugboard:
    connections: list = field(default_factory=list)

    def encode(self, key):
        for connection in self.connections:
            if connection[0] == key:
                return connection[1]
            if connection[1] == key:
                return connection[0]
        return key


@dataclass
class Lightboard:
    @staticmethod
    def display(key):
        print(key)
        return key


@dataclass
class Machine:
    reflector_b = Reflector(alphas="YRUHQSLDPXNGOKMIEBFZCWVJAT")
    reflector_c = Reflector(alphas="FVPJIAOYEDRZXWGCTKUQSBNMHL")
    rotor_a = Rotor(alphas="EKMFLGDQVZNTOWYHXUSPAIBRCJ", notch_key="R")
    rotor_b = Rotor(alphas="AJDKSIRUXBLHWTMCQGZNPYFVOE", notch_key="F")
    rotor_c = Rotor(alphas="BDFHJLCPRTXVZNYEIWGAKMUSQO", notch_key="W")
    rotor_d = Rotor(alphas="ESOVPZJAYQUIRHXLNFTGKDCMWB", notch_key="K")
    rotor_e = Rotor(alphas="VZBRGITYUPSDNHLXAWMJQOFECK", notch_key="A")
    lightboard = Lightboard()

    keyboard: Keyboard
    plugboard: Plugboard

    def key_press(self, key):
        key = self.plugboard.encode(key)

        key, rotate = self.rotor_a.encode(key, direction="rtl", rotate=True)
        key, rotate = self.rotor_b.encode(key, direction="rtl", rotate=rotate)
        key, _ = self.rotor_c.encode(key, direction="rtl", rotate=rotate)

        key = self.reflector_b.encode(key)

        key, _ = self.rotor_c.encode(key, direction="ltr")
        key, _ = self.rotor_b.encode(key, direction="ltr")
        key, _ = self.rotor_a.encode(key, direction="ltr")

        key = self.plugboard.encode(key)

        return self.lightboard.display(key)


def main():
    keyboard = Keyboard()

    plugboard = Plugboard(connections=[("A", "F"), ("D", "J"), ("O", "X"), ("H", "Z")])

    machine = Machine(keyboard=keyboard, plugboard=plugboard)

    message = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    collection = ""
    for key in message:
        collection += machine.key_press(key)
    # print(collection)

    machine = Machine(keyboard=keyboard, plugboard=plugboard)

    message = collection

    collection = ""
    for key in message:
        collection += machine.key_press(key)
    # print(collection)


if __name__ == "__main__":
    main()
