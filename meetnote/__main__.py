from kivy.app import App
from kivy.uix.label import Label


class MeetNoteApp(App):
    title = "MeetNote"

    def build(self) -> Label:
        return Label(
            text="MeetNote is running!",
            font_size="28sp",
        )


if __name__ == "__main__":
    MeetNoteApp().run()