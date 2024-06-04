import kivy
from kivy.app import App
from kivy.uix.label import Label

kivy.require("2.3.0")


class Flashcards(App):

    def build(self):
        return Label(text="Hello world")


if __name__ == "__main__":
    Flashcards().run()
