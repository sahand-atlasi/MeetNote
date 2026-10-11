from pathlib import Path

from meetnote.application.services import MeetingService


def test_service_deletes_action_item(tmp_path: Path) -> None:
    service = MeetingService(database_path=tmp_path / "meetnote.db")

    meeting_id = service.create_meeting("Planning")
    action_item_id = service.add_action_item(
        meeting_id,
        "Prepare project demo",
    )

    service.delete_action_item(action_item_id)

    assert service.list_action_items(meeting_id) == []
