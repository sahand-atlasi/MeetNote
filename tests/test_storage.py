import sqlite3

import pytest

from meetnote.storage.database import connect
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


def test_foreign_keys_are_enabled(tmp_path):
    database_path = tmp_path / "meetnote.db"

    with connect(database_path) as connection:
        foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]

    assert foreign_keys_enabled == 1


def test_deleting_meeting_cascades_action_items(tmp_path):
    database_path = tmp_path / "meetnote.db"

    meetings = MeetingRepository(database_path)

    with connect(database_path) as connection:
        meeting_id = meetings.create("Planning")
        connection.execute(
            """
            INSERT INTO action_items
                (meeting_id, description)
            VALUES (?, ?)
            """,
            (meeting_id, "Review transcript"),
        )

    meetings.delete(meeting_id)

    with connect(database_path) as connection:
        remaining_items = connection.execute(
            "SELECT id FROM action_items WHERE meeting_id = ?",
            (meeting_id,),
        ).fetchall()

    assert remaining_items == []


def test_invalid_action_item_meeting_is_rejected(tmp_path):
    database_path = tmp_path / "meetnote.db"

    with pytest.raises(sqlite3.IntegrityError):
        with connect(database_path) as connection:
            connection.execute(
                """
                INSERT INTO action_items
                    (meeting_id, description)
                VALUES (?, ?)
                """,
                (999999, "Invalid item"),
            )
