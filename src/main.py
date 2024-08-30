from __future__ import annotations
import csv
from pathlib import Path
import sys
import kivy
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.lang import Builder

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


def unbind_all(widget: Widget, event: str):
    for callback in widget._cb:  # type: ignore
        widget.funbind(event, callback)
    widget._cb = []  # type: ignore


# Source: https://github.com/kivy/kivy/wiki/Scrollable-Label
Builder.load_string(
    """
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
        padding: 20, 20
        font_size: 20

<BottomButtons>:
    orientation: "horizontal"
    size_hint_y: None
    height: 50
    BoxLayout:
        visible: False
        id: toggle_answer_buttons
    Button:
        text: "Edit flashcards"
        id: edit_flashcards_button
        on_release: app.show_editor()
        size_hint: 0.5, 1

<FlashcardsEditor>:
    orientation: "vertical"
    text: ""
    TextInput:
        id: flashcards_input
        text: root.text
        # https://stackoverflow.com/a/76593994/11519302
        input_type: "text"
        keyboard_suggestions: True
    Button:
        text: "Save"
        size_hint_y: None
        height: 50
        id: save_flashcards_button
    """
)


class ScrollableLabel(ScrollView):
    text = StringProperty("")


class BottomButtons(BoxLayout):
    pass


class FlashcardsEditor(BoxLayout):
    text = StringProperty("")


class FlashcardButton(Button):
    def __init__(
        self, parent: FlashcardsScreen, label: str, question: str, answer: str, **kwargs
    ):
        super(FlashcardButton, self).__init__(**kwargs)
        self.text = label
        self.question = question
        self.answer = answer
        self.main_screen = parent
        self.bind(on_release=self.activate)

    def activate(self, _):
        self.main_screen.active_flashcard = self
        self.show_question()

    def show_answer(self):
        main_text = TextInput(
            text=self.answer,
            readonly=True,
        )
        self.main_screen.flashcard_container.clear_widgets()
        self.main_screen.flashcard_container.add_widget(main_text)
        toggle_answer_buttons = (
            self.main_screen.bottom_buttons.ids.toggle_answer_buttons
        )
        toggle_answer_buttons.clear_widgets()
        toggle_answer_buttons.add_widget(
            Button(
                text="Show question",
                on_release=lambda _: self.show_question(),
                size_hint_y=None,
                height=50,
            )
        )

    def show_question(self):
        main_text = TextInput(
            text=self.question,
            readonly=True,
        )
        self.main_screen.flashcard_container.clear_widgets()
        self.main_screen.flashcard_container.add_widget(main_text)
        toggle_answer_buttons = (
            self.main_screen.bottom_buttons.ids.toggle_answer_buttons
        )
        toggle_answer_buttons.clear_widgets()
        toggle_answer_buttons.add_widget(
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

        self.active_flashcard: FlashcardButton | None = None
        self.top_buttons = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        self.add_widget(self.top_buttons)
        self.flashcard_container = BoxLayout(orientation="vertical")
        self.add_widget(self.flashcard_container)
        self.bottom_buttons = BottomButtons()
        self.add_widget(self.bottom_buttons)

        Clock.schedule_once(self.reload_flashcards_ui, 0)

    def reload_flashcards_ui(self, _=None):
        self.flashcard_container.clear_widgets()
        splash_text = Label(text=f"Loading flashcards...")
        self.flashcard_container.add_widget(splash_text)
        self.bottom_buttons.ids.toggle_answer_buttons.clear_widgets()
        self.bottom_buttons.ids.toggle_answer_buttons.visible = False
        self.load_flashcard_buttons()

    def load_flashcard_buttons(self, _=None):
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

        self.top_buttons.clear_widgets()
        loaded_flashcards = 0
        invalid_flashcards = []
        for flashcard_data in flashcards:
            if len(flashcard_data) != 3:
                print(
                    f"Skipping invalid flashcard: {flashcard_data}",
                    file=sys.stderr,
                )
                invalid_flashcards.append(flashcard_data)
                continue
            label, question, answer = flashcard_data
            self.top_buttons.add_widget(
                FlashcardButton(
                    parent=self,
                    label=label.strip(),
                    question=question.strip(),
                    answer=answer.strip(),
                )
            )
            loaded_flashcards += 1

        self.flashcard_container.clear_widgets()
        splash_text = ""
        if loaded_flashcards:
            splash_text += f"Loaded {loaded_flashcards} flashcard(s). Click on one at the top to view it."
        else:
            splash_text += "No flashcards!\n\nAdd some to the CSV file using the button at the bottom."
        if invalid_flashcards:
            splash_text += f"\n\n\nWarning: Skipped {len(invalid_flashcards)} invalid flashcard(s):\n"
            for flashcard_data in invalid_flashcards:
                splash_text += f"\n{flashcard_data}"
        splash_text_label = ScrollableLabel(text=splash_text)
        self.flashcard_container.add_widget(splash_text_label)


def print_usage():
    print("Usage: python main.py [filename]", file=sys.stderr)


def get_flashcards_path():
    return Path(sys.argv[1]) if len(sys.argv) == 2 else Path("flashcards.csv")


def read_flashcards_file():
    file_path = get_flashcards_path()
    try:
        return open(file_path)
    except FileNotFoundError:
        return None


def write_flashcards_file(flashcards: str):
    file_path = get_flashcards_path()
    with open(file_path, "w") as file:
        file.write(flashcards)


def get_flashcards() -> list[Flashcard]:
    flashcards_file = read_flashcards_file()
    if not flashcards_file:
        return []
    with flashcards_file as file:
        reader = csv.reader(file)
        return list(reader)  # type: ignore


class Flashcards(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_flashcards_csv = (
            "Example, An important question, An impressive answer\n"
        )
        self.top = FlashcardsScreen()

    def show_editor(self):
        flashcards_file = read_flashcards_file()
        content = (
            flashcards_file.read() if flashcards_file else self.default_flashcards_csv
        )

        popup = Popup(
            title="Edit flashcards CSV file",
            content=FlashcardsEditor(text=content),
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
        )

        def save_flashcards(_):
            write_flashcards_file(popup.content.ids.flashcards_input.text)
            self.top.reload_flashcards_ui()
            popup.dismiss()

        popup.content.ids.save_flashcards_button.bind(on_release=save_flashcards)
        popup.open()

    def build(self):
        return self.top


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Too many arguments", file=sys.stderr)
        print_usage()
        sys.exit(1)

    Flashcards().run()
