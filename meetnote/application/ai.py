import os
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel, Field

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
    ) -> list[ExtractedActionItem]:
        ...


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


class ActionItemOutput(BaseModel):
    description: str = Field(
        description="A concrete action that someone should complete",
    )
    owner: str | None = Field(
        default=None,
        description="The person responsible, if identifiable",
    )


class ActionItemsOutput(BaseModel):
    items: list[ActionItemOutput]


class OpenAIActionItemExtractor:
    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = client or OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.model = model

    def extract_action_items(
        self,
        meeting: Meeting,
    ) -> list[ExtractedActionItem]:
        prompt = (
            "Extract concrete action items from this meeting. "
            "Only include tasks that someone should perform. "
            "Use null for owner when no responsible person is stated.\n\n"
            f"Meeting title: {meeting.title}\n"
            f"Meeting notes:\n{meeting.notes}"
        )

        response = self.client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=ActionItemsOutput,
        )

        parsed = response.output_parsed

        if parsed is None:
            return []

        return [
            ExtractedActionItem(
                description=item.description,
                owner=item.owner,
            )
            for item in parsed.items
        ]