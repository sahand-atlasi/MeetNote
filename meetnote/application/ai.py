from typing import Protocol

from meetnote.domain.models import Meeting


class ExtractedActionItem:
    def __init__(
        self,
        description: str,
        owner: str | None = None,
    ) -> None:
        self.description = description
        self.owner = owner


class ActionItemExtractor(Protocol):
    def extract_action_items(
        self,
        meeting: Meeting,
    ) -> list[ExtractedActionItem]: ...


class FakeActionItemExtractor:
    def extract_action_items(
        self,
        meeting: Meeting,
    ) -> list[ExtractedActionItem]:
        return [
            ExtractedActionItem(
                description="Review the meeting recording",
                owner="Sahand",
            ),
            ExtractedActionItem(
                description="Prepare meeting minutes",
            ),
        ]
