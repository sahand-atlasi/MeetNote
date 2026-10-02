from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from meetnote.application.services import MeetingService
from meetnote.config import default_database_path
from meetnote.storage.database import initialize_database


class MeetingScreen(BoxLayout):
    def __init__(
        self,
        service: MeetingService,
        **kwargs,
    ):
        super().__init__(
            orientation="vertical",
            spacing=10,
            padding=20,
            **kwargs,
        )

        self.service = service
        self.selected_meeting_id: int | None = None
        self.action_items_layout = BoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint_y=None,
        )
        self.action_items_layout.bind(
            minimum_height=self.action_items_layout.setter("height")
        )

        action_items_scroll = ScrollView(size_hint_y=None, height=180)
        action_items_scroll.add_widget(self.action_items_layout)

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

        self.meetings_layout = BoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint_y=None,
        )
        self.meetings_layout.bind(minimum_height=self.meetings_layout.setter("height"))

        meetings_scroll = ScrollView(
            size_hint_y=1,
        )
        meetings_scroll.add_widget(self.meetings_layout)

        refresh_button = Button(
            text="Refresh saved meetings",
            size_hint_y=None,
            height=50,
        )
        refresh_button.bind(on_press=self.refresh_meetings)

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
        self.add_widget(
            Label(
                text="Saved meetings",
                size_hint_y=None,
                height=40,
            )
        )
        self.add_widget(
            Label(
                text="Action items",
                size_hint_y=None,
                height=40,
            )
        )
        self.add_widget(action_items_scroll)
        self.add_widget(meetings_scroll)
        self.add_widget(refresh_button)

        self.refresh_meetings()
        self.refresh_action_items()

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
        choose_button.bind(on_press=lambda _: self.select_file(chooser, popup))

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

        try:
            meeting_id = self.service.create_meeting(
                title=title,
                notes=f"Recording: {file_path}",
            )
        except ValueError as error:
            self.status_label.text = f"Status: {error}"
            return

        self.status_label.text = f"Status: meeting saved with ID {meeting_id}"

    def refresh_meetings(self, _button=None):
        self.meetings_layout.clear_widgets()

        meetings = self.service.list_meetings()

        for meeting in meetings:
            meeting_button = Button(
                text=(f"{meeting.id}: {meeting.title}\n{meeting.created_at}"),
                size_hint_y=None,
                height=60,
            )
            meeting_button.bind(
                on_press=lambda _button, meeting_id=meeting.id: self.select_meeting(
                    meeting_id
                )
            )
            self.meetings_layout.add_widget(meeting_button)

        for meeting in meetings:
            meeting_label = Label(
                text=(f"{meeting.id}: {meeting.title}\n{meeting.created_at}"),
                size_hint_y=None,
                height=60,
                halign="left",
                valign="middle",
            )
            meeting_label.bind(
                width=lambda label, _: setattr(
                    label,
                    "text_size",
                    (label.width, None),
                )
            )
            self.meetings_layout.add_widget(meeting_label)

    def select_meeting(self, meeting_id: int) -> None:
        self.selected_meeting_id = meeting_id
        self.refresh_action_items()
        self.status_label.text = f"Status: selected meeting {meeting_id}"

    def refresh_action_items(self) -> None:
        self.action_items_layout.clear_widgets()

        if self.selected_meeting_id is None:
            self.action_items_layout.add_widget(
                Label(
                    text="Select a meeting to view its action items",
                    size_hint_y=None,
                    height=40,
                )
            )
            return

        items = self.service.list_action_items(self.selected_meeting_id)

        if not items:
            self.action_items_layout.add_widget(
                Label(
                    text="No action items",
                    size_hint_y=None,
                    height=40,
                )
            )
            return

        for item in items:
            item_label = Label(
                text=(f"{item.description} — {item.status}"),
                size_hint_y=None,
                height=40,
            )
            self.action_items_layout.add_widget(item_label)


class MeetNoteApp(App):
    title = "MeetNote"

    def build(self):
        database_path = default_database_path()
        initialize_database(database_path)

        service = MeetingService(database_path)

        return MeetingScreen(service=service)
