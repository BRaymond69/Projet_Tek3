#!/usr/bin/python3
# Benjamin RAYMOND, Florian Couprie, Luc Anguilla

import sys, os
import random

class Board:
    def __init__(self, width=20, height=20):
        """the board size and time for one turn in milliseconds """
        self.width = width
        self.height = height
        self.board = [[0 for i in range(width)] for j in range(height)]
        self.playable = list(enumerate([[i for i in range(width)] for _ in range(height)]))

    def play(self, player, x, y):
        self.board[y][x] = player

        yv = next(v for v in self.playable if v[0] == y)
        if len(yv[1]) == 1:
            self.playable.remove(yv)
        else:
            yv[1].remove(x)

    def override_board(self, player_moves):
        self.board = [[0] * self.width] * self.height
        self.playable = list(enumerate([[i for i in range(self.width)] for _ in range(self.height)]))
        for x, y, player in player_moves:
            self.play(player, x, y)

    def __repr__(self):
        return "\n".join([" ".join(map(str, [self.width, self.height]))] + [str(line) for line in self.board])

class Brain:
    def __init__(self, name="none", version="1.0", author="none", country="France", debug=False):
        self.name = name
        self.version = version
        self.author = author
        self.country = country

        self.info = {
            "timeout_turn"  : 5000,
            "timeout_match" : 0,
            "max_memory"    : 0,
            "time_left"     : 0,
            "game_type"     : 0,
            "rule"          : 1,
            "evaluate"      : [0, 0],
            "folder"        : ""
        }

        self.board = None
        self.debug = debug

    def __repr__(self):
        return ", ".join([self.name, self.version, self.author, self.country])

    def send_msg(self, mtype="UNKNOWN", message="", x=0, y=0):
        if mtype == "OK":
            print(mtype)

        elif mtype in ["UNKNOWN", "ERROR", "MESSAGE", "DEBUG"]:
            print(" ".join([mtype, message]))

        elif mtype in ["COORD", "SUGGEST"]:
            if mtype == "SUGGEST":
                print("SUGGEST", end=" ")
            print(f"{x},{y}")

        else:
            print("ERROR wtf")

    def start(self, arg):
        """ START [size] -> Start a new game with a board of size [size]x[size] """
        try:
            size = int(arg)
            if size < 5:
                self.send_msg(mtype="ERROR", message="Size must be at least 5")
                return

            self.board = Board(width=size, height=size)
            self.player = 0

            self.send_msg(mtype="OK")
        except ValueError:
            self.send_msg(mtype="ERROR", message="Invalid START parameter")

    def end(self):
        """ END -> Stop the brain """
        exit(0)

    def begin(self):
        """ BEGIN -> Make the first move """
        if not self.player:
            self.player = 1
            self.enemy = 2

        y, xs = random.choice(self.board.playable)
        x = random.choice(xs)
        self.board.play(self.player, x, y)

        self.send_msg(mtype="COORD", x=x, y=y)

    def turn(self, args):
        """ TURN [X],[Y] -> Move after the opponent moved to [X],[Y] """
        if not self.player:
            self.player = 2
            self.enemy = 1

        x, y = map(int, args.split(","))
        self.board.play(self.enemy, x, y)

        y, xs = random.choice(self.board.playable)
        x = random.choice(xs)
        self.board.play(self.player, x, y)

        self.send_msg(mtype="COORD", x=x, y=y)

    def board_f(self):
        """ BOARD ... DONE -> Override the current state of the board with a new one """
        try:
            new_inputs = []
            inp = input().rstrip()
            while not inp.upper().startswith("DONE"):
                if inp.count(",") != 2:
                    raise ValueError
                new_inputs += [list(map(int, inp.split(",")))]
                inp = input().rstrip()

            self.board.override_board(new_inputs)

            self.player = len(new_inputs) % 2 + 1
            self.enemy = (len(new_inputs) + 1) % 2 + 1
            self.begin()

        except ValueError:
            self.send_msg(mtype="ERROR", message="Invalid BOARD parameters")

    def info_f(self, args):
        key, value = args.split(" ")
        if key not in self.info.keys():
            self.send_msg(mtype="ERROR", message="Invalid INFO parameters")
            return

        if key != "folder" and key != "evaluate":
            try:
                value = int(value)
            except:
                self.send_msg(mtype="ERROR", message="Invalid INFO parameters")
                return

        elif key == "evaluate":
            try:
                value = list(map(int, value))
            except:
                self.send_msg(mtype="ERROR", message="Invalid INFO parameters")
                return

        self.info[key] = value

    def about(self):
        print(self)

    def handle_command(self, command):
        try:
            cmd = command.split(" ")[0].upper()
            if cmd in ["END", "BEGIN", "BOARD", "ABOUT"]:
                {
                    "END": self.end,
                    "BEGIN": self.begin,
                    "BOARD": self.board_f,
                    "ABOUT": self.about
                }[cmd]()

            elif cmd in ["START", "TURN", "INFO"]:
                {
                    "START": self.start,
                    "TURN": self.turn,
                    "INFO": self.info_f
                }[cmd](" ".join(command.split(" ")[1:]))

            else:
                self.send_msg(mtype="UNKNOWN", message="Command not handled")

        except Exception:
            self.send_msg(mtype="ERROR", message="Invlid input (throw)")

def main():
    try:
        b = Brain(name="Random", version="1.0", author="Tek3", country="France")
        while True:
            b.handle_command(input().rstrip())
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass

if __name__ == "__main__":
    main()
