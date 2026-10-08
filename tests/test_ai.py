from types import SimpleNamespace
from unittest.mock import MagicMock

from meetnote.application.ai import (
    ActionItemOutput,
    ActionItemsOutput,
    FakeActionItemExtractor,
    OpenAIActionItemExtractor,
)
from meetnote.application.services import MeetingService
from meetnote.domain.models import Meeting


def test_openai_action_item_extractor_returns_parsed_items() -> None:
    meeting = Meeting(
        id=1,
        title="Weekly meeting",
        notes="Discussed project progress.",
        transcript="Sahand will review the recording.",
        created_at="2026-10-08T12:00:00+00:00",
    )

    parsed_output = ActionItemsOutput(
        items=[
            ActionItemOutput(
                description="Review the recording",
                owner="Sahand",
            ),
            ActionItemOutput(
                description="Prepare meeting minutes",
                owner=None,
            ),
        ]
    )

    response = SimpleNamespace(output_parsed=parsed_output)

    client = MagicMock()
    client.responses.parse.return_value = response

    extractor = OpenAIActionItemExtractor(
        client=client,
        model="test-model",
    )

    result = extractor.extract_action_items(meeting)

    assert len(result) == 2
    assert result[0].description == "Review the recording"
    assert result[0].owner == "Sahand"
    assert result[1].description == "Prepare meeting minutes"
    assert result[1].owner is None

    client.responses.parse.assert_called_once()


def test_meeting_service_extracts_and_saves_action_items(
    tmp_path,
) -> None:
    database_path = tmp_path / "meetnote.db"

    service = MeetingService(
        database_path=database_path,
        action_item_extractor=FakeActionItemExtractor(),
    )

    meeting_id = service.create_meeting("Weekly meeting")

    created_count = service.extract_action_items(meeting_id)

    assert created_count == 2

    action_items = service.list_action_items(meeting_id)

    assert len(action_items) == 2
    assert action_items[0].description == "Review the meeting recording"
    assert action_items[0].owner == "Sahand"
    assert action_items[0].status == "open"
    assert action_items[1].description == "Prepare meeting minutes"
    assert action_items[1].owner is None
    assert action_items[1].status == "open"


def test_meeting_service_rejects_unknown_meeting(
    tmp_path,
) -> None:
    database_path = tmp_path / "meetnote.db"

    service = MeetingService(
        database_path=database_path,
        action_item_extractor=FakeActionItemExtractor(),
    )

    try:
        service.extract_action_items(999)
    except ValueError as error:
        assert str(error) == "Meeting 999 does not exist"
    else:
        raise AssertionError("Expected ValueError for unknown meeting")
