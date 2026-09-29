from pathlib import Path

from meetnote.storage.repositories import (
    ActionItemRepository,
    MeetingRepository,
)
from meetnote.domain.models import ActionItem, Meeting


class MeetingService:
    def __init__(self, database_path: Path) -> None:
        self.meetings = MeetingRepository(database_path)
        self.action_items = ActionItemRepository(database_path)

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

    def list_action_items(self, meeting_id: int) -> list[ActionItem]:
        return self.action_items.list_for_meeting(meeting_id)

    def mark_action_item_done(self, action_item_id: int) -> None:
        self.action_items.mark_done(action_item_id)

    def mark_action_item_open(self, action_item_id: int) -> None:
        self.action_items.mark_open(action_item_id)
