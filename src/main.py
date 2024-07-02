import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.label import Label

kivy.require("2.3.0")


class FlashcardsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(FlashcardsScreen, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.top_buttons = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        self.top_buttons.add_widget(Label(text="Flashcard 1"))
        self.top_buttons.add_widget(Label(text="Flashcard 2"))
        self.top_buttons.add_widget(Label(text="Flashcard 3"))
        self.top_buttons.add_widget(Label(text="Flashcard 4"))
        self.add_widget(self.top_buttons)

        self.add_widget(Label(text="What is the purpose of RAM?"))


class Flashcards(App):

    def build(self):
        return FlashcardsScreen()


if __name__ == "__main__":
    Flashcards().run()
