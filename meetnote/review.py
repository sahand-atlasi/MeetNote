from meetnote.models import ActionItemStatus


VALID_TRANSITIONS: dict[ActionItemStatus, set[ActionItemStatus]] = {
    ActionItemStatus.SUBMITTED: {
        ActionItemStatus.UNDER_REVIEW,
    },
    ActionItemStatus.UNDER_REVIEW: {
        ActionItemStatus.VERIFIED,
        ActionItemStatus.NEEDS_CHANGES,
        ActionItemStatus.REJECTED,
    },
    ActionItemStatus.NEEDS_CHANGES: {
        ActionItemStatus.UNDER_REVIEW,
    },
    ActionItemStatus.VERIFIED: {
        ActionItemStatus.COMPLETED,
    },
    ActionItemStatus.REJECTED: set(),
    ActionItemStatus.COMPLETED: set(),
}


class InvalidStatusTransition(ValueError):
    """Raised when an action-item status change is not allowed."""


def can_transition(
    current: ActionItemStatus,
    new: ActionItemStatus,
) -> bool:
    return new in VALID_TRANSITIONS[current]


def transition_status(
    current: ActionItemStatus,
    new: ActionItemStatus,
) -> ActionItemStatus:
    if not can_transition(current, new):
        raise InvalidStatusTransition(
            f"Cannot change status from {current.value} to {new.value}"
        )

    return new
