import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.label import Label

kivy.require("2.3.0")


class FlashcardButton(Button):
    def __init__(self, label: str, question: str, answer: str, **kwargs):
        super(FlashcardButton, self).__init__(**kwargs)
        self.text = label
        self.question = question
        self.answer = answer
        self.bind(on_press=self.callback)

    def callback(self, target: Button):
        print('The "%s" flashcard was selected' % target.text)


class FlashcardsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(FlashcardsScreen, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.top_buttons = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        self.top_buttons.add_widget(
            FlashcardButton(
                "RAM",
                "What is the purpose of RAM?",
                "Stores in-use data and instructions",
            )
        )
        self.top_buttons.add_widget(
            FlashcardButton(
                "TCP/IP stack",
                "What are the 4 layers in the TCP/IP stack?",
                "Application, Transport, Internet, Link",
            )
        )
        self.add_widget(self.top_buttons)

        self.add_widget(Label(text="What is the purpose of RAM?"))


class Flashcards(App):

    def build(self):
        return FlashcardsScreen()


if __name__ == "__main__":
    Flashcards().run()
