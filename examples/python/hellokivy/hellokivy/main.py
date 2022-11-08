import sys

# Patch missing sys.argv[0] which is None for some reason when using PyOxidizer
# Kivy fails on importing the library, because it tries to iterate on sys.argv[0]
if sys.argv[0] is None:
    sys.argv[0] = sys.executable
    print(f"Patched sys.argv to {sys.argv}")

import kivy
from kivy.app import App
from kivy.uix.label import Label


class MyFirstKivyApp(App):
    def build(self):
        return Label(text="Hello World !")


def main() -> None:
    kivy.require("2.0.0")
    MyFirstKivyApp().run()


if __name__ == "__main__":
    print("Launching HelloKivy from __main__")
    main()
