from __future__ import annotations
import csv
import sys
import kivy
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.label import Label

kivy.require("2.3.0")

# Types
Flashcard = tuple[str, str, str]


class WrappedLabel(Label):
    # Thank you https://stackoverflow.com/a/58227983/11519302
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *_: self.setter("text_size")(self, (self.width, None)),
            texture_size=lambda *_: self.setter("height")(self, self.texture_size[1]),
        )


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
        main_text = TextInput(
            text=self.question,
            readonly=True,
        )
        self.main_screen.flashcard_container.clear_widgets()
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
        self.add_widget(self.top_buttons)
        self.flashcard_container = BoxLayout(orientation="vertical")
        self.add_widget(self.flashcard_container)
        Clock.schedule_once(self.load_flashcards, 0)

        self.flashcard_container.clear_widgets()
        splash_text = Label(text=f"Loading flashcards...")
        self.flashcard_container.add_widget(splash_text)

    def load_flashcards(self, _):
        try:
            flashcards = get_flashcards()
        except OSError as error:
            popup = Popup(
                title="Error while starting the app",
                content=WrappedLabel(
                    text=f"Error: Couldn't read the flashcards file.\n\n{error}"
                ),
                size_hint=(0.8, 0.8),
                auto_dismiss=False,
            )
            popup.open()
            return

        loaded_flashcards = 0
        invalid_flashcards = 0
        for flashcard_data in flashcards:
            if len(flashcard_data) < 3:
                print(
                    f"Skipping invalid flashcard: {flashcard_data}",
                    file=sys.stderr,
                )
                invalid_flashcards += 1
                continue
            label, question, answer = flashcard_data
            self.top_buttons.add_widget(
                FlashcardButton(
                    parent=self,
                    label=label,
                    question=question,
                    answer=answer,
                )
            )
            loaded_flashcards += 1

        self.flashcard_container.clear_widgets()
        splash_text = Label(text=f"Loaded {loaded_flashcards} flashcards")
        self.flashcard_container.add_widget(splash_text)


def print_usage():
    print("Usage: python main.py <filename>", file=sys.stderr)


def get_flashcards() -> list[Flashcard]:
    if len(sys.argv) < 2:
        print("Please provide a path to the flashcards CSV file", file=sys.stderr)
        print_usage()
        sys.exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments", file=sys.stderr)
        print_usage()
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as file:
        reader = csv.reader(file)
        return list(reader)  # type: ignore


class Flashcards(App):

    def build(self):
        return FlashcardsScreen()


if __name__ == "__main__":
    Flashcards().run()
