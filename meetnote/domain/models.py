from dataclasses import dataclass
from typing import Literal


MeetingStatus = Literal["active", "archived"]
ActionItemStatus = Literal["open", "done", "verified"]


@dataclass(frozen=True)
class Meeting:
    id: int
    title: str
    notes: str
    transcript: str
    created_at: str


@dataclass(frozen=True)
class ActionItem:
    id: int
    meeting_id: int
    description: str
    owner: str | None
    status: ActionItemStatus
    due_date: str | None
