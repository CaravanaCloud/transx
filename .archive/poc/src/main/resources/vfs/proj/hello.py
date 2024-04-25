#!/usr/bin/env python3
import polyglot
from termcolor import colored

class PyHello:
    def hello(self, txt):
        colored_text = colored("hello " + str(txt), "red", attrs=["reverse", "blink"])
        print(colored_text)

# We export the PyHello class to Java as our explicit interface with the Java side
polyglot.export_value("PyHello", PyHello)