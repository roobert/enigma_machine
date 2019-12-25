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
            if direction == "rtl":
                if value[0] == key:
                    return value[1]
            elif direction == "ltr":
                if value[1] == key:
                    return value[0]
            else:
                raise KeyError
        raise KeyError

    def process(self, key, direction=None, rotate=False):
        print(f"k: {key}, d: {direction}, rotate: {rotate}")
        key_next = self.find_key(key, direction=direction)

        if direction == "rtl":
            if rotate:
                self.rotate_rotor()
            return key_next, self.rotate_next_rotor()

        if direction == "ltr":
            return key_next, False
        raise KeyError

    def rotate_rotor(self):
        self.rotor.insert(0, self.rotor.pop())

    def rotate_next_rotor(self):
        return self.rotor[0][0] == self.notch_key

    def __repr__(self):
        return str(self.rotor)


@dataclass
class Reflector(RotorBase):
    def process(self, key):
        for value in self.rotor:
            if value[0] == key:
                return value[1]
        raise KeyError


@dataclass
class Plugboard:
    connections: list = field(default_factory=list)

    def process(self, key):
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
        key = self.plugboard.process(key)
        key, rotate = self.rotor_a.process(key, direction="rtl", rotate=True)
        key, rotate = self.rotor_b.process(key, direction="rtl", rotate=rotate)
        key, rotate = self.rotor_c.process(key, direction="rtl", rotate=rotate)
        key = self.reflector_b.process(key)
        key, _ = self.rotor_c.process(key, direction="ltr")
        key, _ = self.rotor_b.process(key, direction="ltr")
        key, _ = self.rotor_a.process(key, direction="ltr")
        key = self.plugboard.process(key)
        return self.lightboard.display(key)


def main():
    keyboard = Keyboard()
    plugboard = Plugboard(connections=[("A", "F"), ("D", "J"), ("O", "X"), ("H", "Z")])
    machine = Machine(keyboard=keyboard, plugboard=plugboard)
    message = "HURTYOUBAD"

    collection = ""
    for key in message:
        collection += machine.key_press(key)

    print("---")

    machine = Machine(keyboard=keyboard, plugboard=plugboard)
    message = collection

    for key in message:
        machine.key_press(key)


if __name__ == "__main__":
    main()
