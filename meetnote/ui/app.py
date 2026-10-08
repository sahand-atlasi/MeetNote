import os
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from kivy.clock import Clock

from meetnote.application.transcription import (
    FakeTranscriber,
    LocalWhisperTranscriber,
)
from meetnote.application.services import MeetingService


class MeetingScreen(BoxLayout):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            orientation="vertical",
            spacing=10,
            padding=20,
            **kwargs,
        )

        self.executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="meetnote-worker",
        )
        self.transcription_future: Future[str] | None = None
        data_directory = Path("data")
        data_directory.mkdir(parents=True, exist_ok=True)

        transcriber_name = os.environ.get(
            "MEETNOTE_TRANSCRIBER",
            "fake",
        ).lower()

        if transcriber_name == "whisper":
            transcriber = LocalWhisperTranscriber(
                model_size="base",
                device="cpu",
                compute_type="int8",
            )
        else:
            transcriber = FakeTranscriber()

        self.meeting_service = MeetingService(
            database_path=data_directory / "meetnote.db",
            transcriber=transcriber,
        )
        self.current_meeting_id: int | None = None
        self.selected_file_path: Path | None = None

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

        self.submit_button = Button(
            text="Submit meeting",
            size_hint_y=None,
            height=50,
        )
        self.submit_button.disabled = False
        self.submit_button.bind(on_press=self.submit_meeting)

        extract_button = Button(
            text="Extract action items",
            size_hint_y=None,
            height=50,
        )
        extract_button.bind(on_press=self.extract_action_items)

        refresh_button = Button(
            text="Refresh action items",
            size_hint_y=None,
            height=50,
        )
        refresh_button.bind(on_press=self.refresh_action_items)

        self.action_items_label = Label(
            text="No action items loaded",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=120,
        )
        self.action_items_label.bind(
            width=self._update_action_items_text_size,
        )

        self.add_widget(
            Label(
                text="MeetNote",
                font_size="30sp",
                size_hint_y=None,
                height=50,
            )
        )
        self.add_widget(
            Label(
                text="Create a new meeting",
                size_hint_y=None,
                height=35,
            )
        )
        self.add_widget(self.title_input)
        self.add_widget(select_file_button)
        self.add_widget(self.selected_file_label)
        self.add_widget(self.submit_button)
        self.add_widget(extract_button)
        self.add_widget(refresh_button)
        self.add_widget(self.action_items_label)
        self.add_widget(self.status_label)

    def _update_action_items_text_size(
        self,
        label: Label,
        width: float,
    ) -> None:
        label.text_size = (width, None)

    def open_file_chooser(self, _button: Button) -> None:
        chooser = FileChooserListView(
            path=str(Path.home()),
            filters=[
                "*.mp3",
                "*.wav",
                "*.m4a",
                "*.mp4",
                "*.mov",
            ],
        )

        choose_button = Button(
            text="Use selected file",
            size_hint_y=None,
            height=50,
        )

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(chooser)
        layout.add_widget(choose_button)

        popup = Popup(
            title="Choose meeting recording",
            content=layout,
            size_hint=(0.9, 0.9),
        )

        choose_button.bind(
            on_press=lambda _button: self.select_file(
                chooser,
                popup,
            )
        )

        popup.open()

    def select_file(
        self,
        chooser: FileChooserListView,
        popup: Popup,
    ) -> None:
        if not chooser.selection:
            self.status_label.text = "Status: select a file first"
            return

        self.selected_file_path = Path(chooser.selection[0])
        self.selected_file_label.text = str(self.selected_file_path)
        self.status_label.text = "Status: file selected"
        popup.dismiss()

    def submit_meeting(self, _button: Button) -> None:
        self.status_label.text = "Status: submit clicked"

        title = self.title_input.text.strip()

        if not title:
            self.status_label.text = "Status: enter a meeting title"
            return

        if self.selected_file_path is None:
            self.status_label.text = "Status: select an audio or video file"
            return

        if (
            self.transcription_future is not None
            and not self.transcription_future.done()
        ):
            self.status_label.text = "Status: transcription already in progress"
            return

        try:
            self.current_meeting_id = self.meeting_service.create_meeting(
                title=title,
                notes=str(self.selected_file_path),
            )
        except Exception as error:
            self.status_label.text = f"Status: submit failed: {error}"
            return

        self.status_label.text = "Status: transcribing recording"
        self.submit_button.disabled = True

        self.transcription_future = self.executor.submit(
            self.meeting_service.transcribe_meeting,
            self.current_meeting_id,
            self.selected_file_path,
        )
        self.transcription_future.add_done_callback(
            self._transcription_finished,
        )

    def _transcription_finished(
        self,
        future: Future[str],
    ) -> None:
        Clock.schedule_once(
            lambda _dt: self._show_transcription_result(future),
        )

    def _show_transcription_result(
        self,
        future: Future[str],
    ) -> None:
        self.submit_button.disabled = False

        try:
            transcript = future.result()
        except Exception as error:
            self.status_label.text = f"Status: transcription failed: {error}"
            return

        self.status_label.text = (
            "Status: meeting submitted; "
            f"transcript length: {len(transcript)} characters"
        )

        self.action_items_label.text = "No action items loaded"
        self.status_label.text = (
            f"Status: meeting submitted (ID {self.current_meeting_id})"
        )

    def extract_action_items(self, _button: Button) -> None:
        if self.current_meeting_id is None:
            self.action_items_label.text = (
                "Submit a meeting before extracting action items"
            )
            return

        try:
            count = self.meeting_service.extract_action_items(
                self.current_meeting_id,
            )
        except ValueError as error:
            self.status_label.text = f"Status: {error}"
            return

        self.status_label.text = f"Status: extracted {count} action item(s)"
        self.refresh_action_items(_button)

    def refresh_action_items(self, _button: Button) -> None:
        if self.current_meeting_id is None:
            self.action_items_label.text = (
                "Submit a meeting before refreshing action items"
            )
            return

        items = self.meeting_service.list_action_items(
            self.current_meeting_id,
        )

        if not items:
            self.action_items_label.text = "No action items"
            self.status_label.text = "Status: action items refreshed"
            return

        self.action_items_label.text = "\n".join(
            self._format_action_item(item) for item in items
        )
        self.status_label.text = "Status: action items refreshed"

    @staticmethod
    def _format_action_item(item: Any) -> str:
        owner = getattr(item, "owner", None)
        owner_text = f" — {owner}" if owner else ""
        return f"• [{item.status}] {item.description}{owner_text}"

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)


class MeetNoteApp(App):
    title = "MeetNote"

    def build(self) -> MeetingScreen:
        return MeetingScreen()

    def on_stop(self) -> None:
        if isinstance(self.root, MeetingScreen):
            self.root.shutdown()
