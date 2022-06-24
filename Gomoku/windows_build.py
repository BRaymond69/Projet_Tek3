#!/bin/python3

from os import system

chosen_brain = "pbrain-eval.py"

system("pip install pyinstaller")
system(f"pyinstaller {chosen_brain} --onefile")
