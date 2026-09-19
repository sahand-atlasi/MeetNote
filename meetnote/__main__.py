from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


class MeetingScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=10,
            padding=20,
            **kwargs,
        )

        self.title_input = TextInput(
            hint_text="Enter meeting title",
            multiline=False,
            size_hint_y=None,
            height=45,
        )

        self.selected_file_label = Label(
            text="No audio or video file selected",
            size_hint_y=None,
            height=40,
        )

        self.status_label = Label(
            text="Status: waiting for a file",
            size_hint_y=None,
            height=40,
        )

        select_file_button = Button(
            text="Select audio or video file",
            size_hint_y=None,
            height=50,
        )
        select_file_button.bind(on_press=self.open_file_chooser)

        submit_button = Button(
            text="Submit meeting",
            size_hint_y=None,
            height=50,
        )
        submit_button.bind(on_press=self.submit_meeting)

        self.add_widget(Label(text="MeetNote", font_size="30sp"))
        self.add_widget(Label(text="Create a new meeting"))
        self.add_widget(self.title_input)
        self.add_widget(select_file_button)
        self.add_widget(self.selected_file_label)
        self.add_widget(submit_button)
        self.add_widget(self.status_label)

    def open_file_chooser(self, _button):
        chooser = FileChooserListView(
            path=str(Path.home()),
            filters=["*.mp3", "*.wav", "*.m4a", "*.mp4", "*.mov"],
        )

        choose_button = Button(
            text="Use selected file",
            size_hint_y=None,
            height=50,
        )
        choose_button.bind(
            on_press=lambda _: self.select_file(chooser, popup)
        )

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(chooser)
        layout.add_widget(choose_button)

        popup = Popup(
            title="Choose meeting recording",
            content=layout,
            size_hint=(0.9, 0.9),
        )

        popup.open()

    def select_file(self, chooser, popup):
        if not chooser.selection:
            self.status_label.text = "Status: select a file first"
            return

        selected_path = chooser.selection[0]
        self.selected_file_label.text = selected_path
        self.status_label.text = "Status: file selected"
        popup.dismiss()

    def submit_meeting(self, _button):
        title = self.title_input.text.strip()
        file_path = self.selected_file_label.text

        if not title:
            self.status_label.text = "Status: enter a meeting title"
            return

        if file_path == "No audio or video file selected":
            self.status_label.text = "Status: select an audio or video file"
            return

        self.status_label.text = "Status: meeting submitted"


class MeetNoteApp(App):
    title = "MeetNote"

    def build(self):
        return MeetingScreen()


if __name__ == "__main__":
    MeetNoteApp().run()