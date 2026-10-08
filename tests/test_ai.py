from types import SimpleNamespace
from unittest.mock import MagicMock

from meetnote.application.ai import (
    ActionItemOutput,
    ActionItemsOutput,
    OpenAIActionItemExtractor,
)
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