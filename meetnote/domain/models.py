from dataclasses import dataclass


@dataclass(frozen=True)
class Meeting:
    id: int
    title: str
    notes: str
    created_at: str


@dataclass(frozen=True)
class ActionItem:
    id: int
    meeting_id: int
    description: str
    owner: str | None
    status: str
    due_date: str | None
