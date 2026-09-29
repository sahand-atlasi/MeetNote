from pathlib import Path

import pytest

from meetnote.storage.database import initialize_database
from meetnote.storage.repositories import (
    ActionItemRepository,
    MeetingRepository,
)


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.sqlite3"
    initialize_database(path)
    return path


def test_create_and_read_meeting(database_path: Path) -> None:
    repository = MeetingRepository(database_path)

    meeting_id = repository.create(
        title="Planning meeting",
        notes="Discussed the next release.",
    )

    meeting = repository.get(meeting_id)

    assert meeting is not None
    assert meeting["title"] == "Planning meeting"
    assert meeting["notes"] == "Discussed the next release."


def test_create_and_list_action_items(database_path: Path) -> None:
    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning meeting")

    action_items.create(
        meeting_id=meeting_id,
        description="Prepare the release notes",
        owner="Sahand",
    )

    items = action_items.list_for_meeting(meeting_id)

    assert len(items) == 1
    assert items[0]["description"] == "Prepare the release notes"
    assert items[0]["owner"] == "Sahand"
    assert items[0]["status"] == "open"


def test_mark_action_item_done(database_path: Path) -> None:
    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning meeting")
    action_item_id = action_items.create(
        meeting_id=meeting_id,
        description="Send the minutes",
    )

    action_items.mark_done(action_item_id)

    items = action_items.list_for_meeting(meeting_id)

    assert items[0]["status"] == "done"


def test_action_item_requires_existing_meeting(database_path: Path) -> None:
    action_items = ActionItemRepository(database_path)

    with pytest.raises(Exception):
        action_items.create(
            meeting_id=999,
            description="Invalid action item",
        )


def test_deleting_meeting_deletes_its_action_items(
    database_path: Path,
) -> None:
    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning meeting")
    action_items.create(
        meeting_id=meeting_id,
        description="Prepare the agenda",
    )

    meetings.delete(meeting_id)

    assert meetings.get(meeting_id) is None
    assert action_items.list_for_meeting(meeting_id) == []


def test_mark_action_item_open(database_path: Path) -> None:
    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning meeting")
    action_item_id = action_items.create(
        meeting_id=meeting_id,
        description="Send the minutes",
    )

    action_items.mark_done(action_item_id)
    action_items.mark_open(action_item_id)

    items = action_items.list_for_meeting(meeting_id)

    assert items[0]["status"] == "open"


def test_delete_action_item(database_path: Path) -> None:
    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning meeting")
    action_item_id = action_items.create(
        meeting_id=meeting_id,
        description="Send the minutes",
    )

    action_items.delete(action_item_id)

    assert action_items.list_for_meeting(meeting_id) == []
