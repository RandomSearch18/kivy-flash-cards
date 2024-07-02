from __future__ import annotations
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.label import Label

kivy.require("2.3.0")


class FlashcardButton(Button):
    def __init__(
        self, parent: FlashcardsScreen, label: str, question: str, answer: str, **kwargs
    ):
        super(FlashcardButton, self).__init__(**kwargs)
        self.text = label
        self.question = question
        self.answer = answer
        self.main_screen = parent
        self.bind(on_release=self.show_question)

    def show_answer(
        self,
    ):
        self.main_screen.flashcard_container.clear_widgets()
        main_text = TextInput(
            text=self.answer,
            readonly=True,
        )
        self.main_screen.flashcard_container.add_widget(main_text)
        self.main_screen.flashcard_container.add_widget(
            Button(
                text="Show question",
                on_release=lambda _: self.show_question(),
                size_hint_y=None,
                height=50,
            )
        )

    def show_question(self, _=None):
        self.main_screen.flashcard_container.clear_widgets()
        main_text = TextInput(
            text=self.question,
            readonly=True,
        )
        self.main_screen.flashcard_container.add_widget(main_text)
        self.main_screen.flashcard_container.add_widget(
            Button(
                text="Show answer",
                on_release=lambda _: self.show_answer(),
                size_hint_y=None,
                height=50,
            )
        )


class FlashcardsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(FlashcardsScreen, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.top_buttons = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        flashcards: list[tuple[str, str, str]] = [
            (
                "RAM",
                "What is the purpose of RAM?",
                "Stores in-use data and instructions",
            ),
            (
                "TCP/IP stack",
                "What are the 4 layers in the TCP/IP stack?",
                "Application, Transport, Internet, Link",
            ),
        ]
        for label, question, answer in flashcards:
            self.top_buttons.add_widget(
                FlashcardButton(
                    parent=self,
                    label=label,
                    question=question,
                    answer=answer,
                )
            )
        self.add_widget(self.top_buttons)

        self.flashcard_container = BoxLayout(orientation="vertical")
        self.add_widget(self.flashcard_container)


class Flashcards(App):

    def build(self):
        return FlashcardsScreen()


if __name__ == "__main__":
    Flashcards().run()
