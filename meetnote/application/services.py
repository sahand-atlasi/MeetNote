from pathlib import Path

from meetnote.application.ai import (
    ActionItemExtractor,
    FakeActionItemExtractor,
)
from meetnote.application.transcription import (
    FakeTranscriber,
    Transcriber,
)
from meetnote.domain.models import ActionItem, Meeting
from meetnote.storage.repositories import (
    ActionItemRepository,
    MeetingRepository,
)


class MeetingService:
    def __init__(
        self,
        database_path: Path,
        action_item_extractor: ActionItemExtractor | None = None,
        transcriber: Transcriber | None = None,
    ) -> None:
        self.meetings = MeetingRepository(database_path)
        self.action_items = ActionItemRepository(database_path)
        self.action_item_extractor = action_item_extractor or FakeActionItemExtractor()
        self.transcriber = transcriber or FakeTranscriber()

    def transcribe_meeting(
        self,
        meeting_id: int,
        audio_path: Path,
    ) -> str:
        transcript = self.transcriber.transcribe(audio_path)

        self.meetings.update_transcript(
            meeting_id,
            transcript,
        )

        return transcript

    def extract_action_items(self, meeting_id: int) -> int:
        meeting = self.meetings.get(meeting_id)

        if meeting is None:
            raise ValueError(f"Meeting {meeting_id} does not exist")

        extracted_items = self.action_item_extractor.extract_action_items(meeting)

        created_count = 0

        for item in extracted_items:
            self.action_items.create(
                meeting_id=meeting.id,
                description=item.description,
                owner=item.owner,
            )
            created_count += 1

        return created_count

    def create_meeting(self, title: str, notes: str = "") -> int:
        cleaned_title = title.strip()

        if not cleaned_title:
            raise ValueError("Meeting title cannot be empty")

        return self.meetings.create(
            title=cleaned_title,
            notes=notes.strip(),
        )

    def list_meetings(self) -> list[Meeting]:
        return self.meetings.list_all()

    def delete_meeting(self, meeting_id: int) -> None:
        self.meetings.delete(meeting_id)

    def add_action_item(
        self,
        meeting_id: int,
        description: str,
        owner: str | None = None,
        due_date: str | None = None,
    ) -> int:
        cleaned_description = description.strip()

        if not cleaned_description:
            raise ValueError("Action-item description cannot be empty")

        cleaned_owner = owner.strip() if owner is not None else None

        return self.action_items.create(
            meeting_id=meeting_id,
            description=cleaned_description,
            owner=cleaned_owner or None,
            due_date=due_date,
        )

    def list_upcoming_action_items(
        self,
        meeting_id: int,
    ) -> list[ActionItem]:
        items = self.list_action_items(meeting_id)

        return sorted(
            (
                item
                for item in items
                if item.status == "open" and item.due_date is not None
            ),
            key=lambda item: item.due_date,
        )

    def list_action_items(self, meeting_id: int) -> list[ActionItem]:
        return self.action_items.list_for_meeting(meeting_id)

    def mark_action_item_done(self, action_item_id: int) -> None:
        self.action_items.mark_done(action_item_id)

    def mark_action_item_open(self, action_item_id: int) -> None:
        self.action_items.mark_open(action_item_id)

    def verify_action_item(self, action_item_id: int) -> None:
        self.action_items.verify(action_item_id)

    def reopen_action_item(self, action_item_id: int) -> None:
        self.action_items.reopen(action_item_id)
