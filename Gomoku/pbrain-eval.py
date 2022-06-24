#!/usr/bin/python3
# Benjamin RAYMOND, Florian Couprie, Luc Anguilla

import sys, os
import random

class Spot:
    """ Details on how advantageous a spot is for both players """
    def __init__(self):
        self.filled = False
        self.DL = [0, 0]
        self.L = [0, 0]
        self.UL = [0, 0]
        self.U = [0, 0]
        self.UR = [0, 0]
        self.R = [0, 0]
        self.DR = [0, 0]
        self.D = [0, 0]
        self.values = [self.DL, self.L, self.UL, self.U, self.UR, self.R, self.DR, self.D]
        self.lines = [(self.DL, self.UR), (self.L, self.R), (self.UL, self.DR), (self.U, self.D)]

    def fill(self):
        self.filled = True

    def __repr__(self):
        if self.filled:
            return "FILLED"
        marks = ["<v", "<", "<^", "^", "^>", ">", "v>", "v"]
        return " | ".join([f"({marks[i]}) {self.values[i]}" for i in range(len(marks)) if self.values[i] != [0, 0]])

class Board:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.reset_board()

    def reset_board(self):
        self.board = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spots = [[Spot() for i in range(self.width)] for j in range(self.height)]

    def fill_spot(self, player, x, y):
        self.spots[y][x].fill()

        # All x values (Vertical, Left, Right)
        V = [x] * 4
        L = [i for i in range(x - 4, x) if i >= 0]
        R = [i for i in range(x + 1, x + 5) if i < self.width]
        # All y values (Horizontal, Up, Down)
        H = [y] * 4
        U = [i for i in range(y - 4, y) if i >= 0]
        D = [i for i in range(y + 1, y + 5) if i < self.height]
        # Directions
        directions = [zip(L[::-1], D), zip(L, H), zip(L, U), zip(V, U),
                      zip(R, U[::-1]), zip(R, H), zip(R, D), zip(V, D)]
        for i, d in enumerate(directions):
            for x, y in d:
                self.spots[y][x].values[i][player - 1] += 1

    def play(self, player, x, y):
        self.board[y][x] = player
        self.fill_spot(player, x, y)

    def override_board(self, player_moves):
        self.reset_board()
        for x, y, player in player_moves:
            self.play(player, x, y)

    def __repr__(self):
        return "\n".join([" ".join(map(str, [self.width, self.height]))] + [str(line) for line in self.board])

    def print_spots(self):
        """ Debug function for the spots """
        for y, xs in enumerate(self.spots):
            for x, spot in enumerate(xs):
                if any(v != [0, 0] for v in spot.values):
                    print(f"Coords: {x},{y} : " + str(spot))
        for y, xs in enumerate(self.spots):
            for x, spot in enumerate(xs):
                if any(v != [0, 0] for v in spot.values):
                    print("*", end="")
                else:
                    print(".", end="")
            print()

    def eval(self, player):
        # output : (score, [x, y])
        # score : who has the upper hand
        # x : if certain win or certain loss can be prevented play this (it won't be -1 in those cases)
        # y : Same thing as x

        p = 0
        e = 0
        must_play = [-1, -1]
        must_play_score = 0
        must_protect = [-1, -1]
        must_protect_score = 0

        best_spot_score = 0
        best_spot = [int(self.width / 2), int(self.height / 2)]

        for y, xs in enumerate(self.spots):
            for x, spot in enumerate(xs):
                # Ignore places we already played at
                if spot.filled:
                    continue

                spot_score = 0
                for left, right in spot.lines:
                    pl = left[player - 1]
                    pr = right[player - 1]
                    el = left[player % 2]
                    er = right[player % 2]
                    pScore = (pl + pr) ** 2
                    eScore = (el + er) ** 2
                    p += pScore
                    e += eScore
                    spot_score += max(pScore, eScore)

                    # Check for instant winning move
                    if pl == 4 or pr == 4:
                        return 10000, [x, y]

                    # Less sure of a win but keep in mind
                    if pl + pr >= 4 and pScore > must_play_score:
                        must_play = [x, y]
                        must_play_score = pScore

                    # Protect at all costs if needed
                    if el + er >= 4 and eScore > must_protect_score:
                        must_protect = [x, y]
                        must_protect_score = eScore

                # The higher the spot score the better it is
                if spot_score > best_spot_score:
                    best_spot_score = spot_score
                    best_spot = [x, y]

        if must_play != [-1, -1]:
            return p - e, must_play
        if must_protect != [-1, -1]:
            return p - e, must_protect
        return p - e, best_spot

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

        _, coords = self.board.eval(self.player)
        x, y = coords
        self.board.play(self.player, x, y)

        self.send_msg(mtype="COORD", x=x, y=y)

    def turn(self, args):
        """ TURN [X],[Y] -> Move after the opponent moved to [X],[Y] """
        if not self.player:
            self.player = 2
            self.enemy = 1

        x, y = map(int, args.split(","))
        self.board.play(self.enemy, x, y)

        _, coords = self.board.eval(self.player)
        x, y = coords
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
        b = Brain(name="Eval", version="1.0", author="Tek3", country="France")
        while True:
            b.handle_command(input().rstrip())
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass

if __name__ == "__main__":
    main()
