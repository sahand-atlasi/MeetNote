from pathlib import Path

import pytest

from meetnote.application.services import MeetingService
from meetnote.storage.database import initialize_database


@pytest.fixture
def service(tmp_path: Path) -> MeetingService:
    database_path = tmp_path / "service.sqlite3"
    initialize_database(database_path)
    return MeetingService(database_path)


def test_service_creates_meeting_with_cleaned_values(
    service: MeetingService,
) -> None:
    meeting_id = service.create_meeting(
        title="  Planning meeting  ",
        notes="  Discuss release  ",
    )

    meetings = service.list_meetings()

    assert meeting_id == meetings[0]["id"]
    assert meetings[0]["title"] == "Planning meeting"
    assert meetings[0]["notes"] == "Discuss release"


def test_service_rejects_empty_meeting_title(
    service: MeetingService,
) -> None:
    with pytest.raises(ValueError, match="Meeting title cannot be empty"):
        service.create_meeting("   ")


def test_service_creates_and_completes_action_item(
    service: MeetingService,
) -> None:
    meeting_id = service.create_meeting("Planning meeting")

    action_item_id = service.add_action_item(
        meeting_id=meeting_id,
        description="  Send the minutes  ",
        owner="  Sahand  ",
    )

    service.mark_action_item_done(action_item_id)

    items = service.list_action_items(meeting_id)

    assert items[0]["description"] == "Send the minutes"
    assert items[0]["owner"] == "Sahand"
    assert items[0]["status"] == "done"


def test_service_rejects_empty_action_item(
    service: MeetingService,
) -> None:
    meeting_id = service.create_meeting("Planning meeting")

    with pytest.raises(
        ValueError,
        match="Action-item description cannot be empty",
    ):
        service.add_action_item(meeting_id, "   ")
