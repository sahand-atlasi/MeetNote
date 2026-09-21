import unittest

from meetnote.models import ActionItemStatus
from meetnote.review import (
    InvalidStatusTransition,
    can_transition,
    transition_status,
)


class ReviewTransitionTests(unittest.TestCase):
    def test_submitted_item_can_enter_review(self) -> None:
        self.assertTrue(
            can_transition(
                ActionItemStatus.SUBMITTED,
                ActionItemStatus.UNDER_REVIEW,
            )
        )

    def test_item_can_be_verified_by_workflow(self) -> None:
        result = transition_status(
            ActionItemStatus.UNDER_REVIEW,
            ActionItemStatus.VERIFIED,
        )

        self.assertEqual(result, ActionItemStatus.VERIFIED)

    def test_submitted_item_cannot_be_completed_directly(self) -> None:
        self.assertFalse(
            can_transition(
                ActionItemStatus.SUBMITTED,
                ActionItemStatus.COMPLETED,
            )
        )

    def test_rejected_item_cannot_be_verified(self) -> None:
        with self.assertRaises(InvalidStatusTransition):
            transition_status(
                ActionItemStatus.REJECTED,
                ActionItemStatus.VERIFIED,
            )

    def test_verified_item_can_be_completed(self) -> None:
        result = transition_status(
            ActionItemStatus.VERIFIED,
            ActionItemStatus.COMPLETED,
        )

        self.assertEqual(result, ActionItemStatus.COMPLETED)
