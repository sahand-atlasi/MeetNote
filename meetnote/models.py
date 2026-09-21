from dataclasses import dataclass
from datetime import date
from enum import Enum


class ActionItemStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    NEEDS_CHANGES = "needs_changes"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ActionItemLabel(str, Enum):
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    INFORMATION = "information"
    FOLLOW_UP = "follow_up"
    DEADLINE = "deadline"
    NEEDS_CLARIFICATION = "needs_clarification"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ActionItem:
    title: str
    meeting_id: int
    id: int | None = None
    description: str = ""
    assignee: str | None = None
    deadline: date | None = None
    priority: Priority = Priority.MEDIUM
    status: ActionItemStatus = ActionItemStatus.SUBMITTED
    label: ActionItemLabel = ActionItemLabel.ACTION_ITEM
    evidence: str = ""
    timestamp_seconds: float | None = None
    review_comment: str = ""
    reviewed_by: int | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Action item title cannot be empty")

        if self.meeting_id <= 0:
            raise ValueError("Meeting ID must be positive")
