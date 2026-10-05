from pathlib import Path

import pytest

from meetnote.application.ai import ExtractedActionItem
from meetnote.application.services import MeetingService
from meetnote.storage.database import initialize_database


@pytest.fixture
def service(tmp_path: Path) -> MeetingService:
    database_path = tmp_path / "ai.sqlite3"
    initialize_database(database_path)
    return MeetingService(database_path)


def test_fake_extractor_returns_action_items(
    service: MeetingService,
) -> None:
    meeting_id = service.create_meeting("Planning meeting")

    created_count = service.extract_action_items(meeting_id)

    assert created_count == 2

    items = service.list_action_items(meeting_id)

    assert len(items) == 2
    assert items[0].description == "Review the meeting recording"
    assert items[0].owner == "Sahand"
    assert items[1].description == "Prepare meeting minutes"
    assert items[1].owner is None


def test_extract_action_items_for_missing_meeting(
    service: MeetingService,
) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        service.extract_action_items(999)


def test_custom_extractor_is_used(service: MeetingService) -> None:
    class SingleItemExtractor:
        def extract_action_items(self, meeting):
            return [
                ExtractedActionItem(
                    description="Custom action item",
                    owner="Test owner",
                )
            ]

    meeting_id = service.create_meeting("Planning meeting")

    service.action_item_extractor = SingleItemExtractor()

    created_count = service.extract_action_items(meeting_id)

    assert created_count == 1

    items = service.list_action_items(meeting_id)

    assert items[0].description == "Custom action item"
    assert items[0].owner == "Test owner"
