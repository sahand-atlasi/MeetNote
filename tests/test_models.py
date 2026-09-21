import unittest
from datetime import date

from meetnote.models import (
    ActionItem,
    ActionItemLabel,
    ActionItemStatus,
    Priority,
)


class ActionItemTests(unittest.TestCase):
    def test_default_status_is_submitted(self) -> None:
        item = ActionItem(
            title="Prepare the report",
            meeting_id=1,
        )

        self.assertEqual(item.status, ActionItemStatus.SUBMITTED)
        self.assertEqual(item.label, ActionItemLabel.ACTION_ITEM)
        self.assertEqual(item.priority, Priority.MEDIUM)

    def test_action_item_can_store_meeting_information(self) -> None:
        item = ActionItem(
            title="Review the budget",
            meeting_id=2,
            assignee="Marco",
            deadline=date(2026, 9, 30),
            priority=Priority.HIGH,
            evidence="Marco will review the budget by 30 September.",
            timestamp_seconds=125.5,
        )

        self.assertEqual(item.assignee, "Marco")
        self.assertEqual(item.deadline, date(2026, 9, 30))
        self.assertEqual(item.priority, Priority.HIGH)
        self.assertEqual(item.timestamp_seconds, 125.5)

    def test_empty_title_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ActionItem(
                title="   ",
                meeting_id=1,
            )

    def test_invalid_meeting_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ActionItem(
                title="Prepare the report",
                meeting_id=0,
            )
