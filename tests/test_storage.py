from meetnote.storage.repositories import (
    ActionItemRepository,
    MeetingRepository,
)


def test_action_item_can_be_marked_open_and_deleted(tmp_path):
    database_path = tmp_path / "meetnote.db"

    meetings = MeetingRepository(database_path)
    action_items = ActionItemRepository(database_path)

    meeting_id = meetings.create("Planning")
    action_item_id = action_items.create(
        meeting_id,
        "Review the transcript",
    )

    action_items.mark_done(action_item_id)
    assert action_items.list_for_meeting(meeting_id)[0].status == "done"

    action_items.mark_open(action_item_id)
    assert action_items.list_for_meeting(meeting_id)[0].status == "open"

    action_items.delete(action_item_id)
    assert action_items.list_for_meeting(meeting_id) == []
