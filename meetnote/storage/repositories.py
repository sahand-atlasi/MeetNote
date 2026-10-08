from datetime import datetime, timezone
from pathlib import Path
from typing import cast

from meetnote.domain.models import (
    ActionItem,
    ActionItemStatus,
    Meeting,
)
from meetnote.storage.database import connect


def meeting_from_row(row: dict) -> Meeting:
    return Meeting(
        id=int(row["id"]),
        title=str(row["title"]),
        notes=str(row["notes"]),
        transcript=str(row["transcript"]),
        created_at=str(row["created_at"]),
    )


def action_item_from_row(row: dict) -> ActionItem:
    return ActionItem(
        id=int(row["id"]),
        meeting_id=int(row["meeting_id"]),
        description=str(row["description"]),
        owner=str(row["owner"]) if row["owner"] is not None else None,
        status=cast(ActionItemStatus, row["status"]),
        due_date=(str(row["due_date"]) if row["due_date"] is not None else None),
    )


class MeetingRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def create(self, title: str, notes: str = "") -> int:
        created_at = datetime.now(timezone.utc).isoformat()

        with connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO meetings (title, notes, created_at)
                VALUES (?, ?, ?)
                """,
                (title, notes, created_at),
            )

        if cursor.lastrowid is None:
            raise RuntimeError("Meeting insert did not return an ID")

        return cursor.lastrowid

    def get(self, meeting_id: int) -> Meeting | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, title, notes, transcript, created_at
                FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
            ).fetchone()

        return meeting_from_row(dict(row)) if row is not None else None

    def list_all(self) -> list[Meeting]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, title, notes, transcript, created_at
                FROM meetings
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [meeting_from_row(dict(row)) for row in rows]

    def delete(self, meeting_id: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                DELETE FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
            )

    def update_transcript(
        self,
        meeting_id: int,
        transcript: str,
    ) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE meetings
                SET transcript = ?
                WHERE id = ?
                """,
                (transcript, meeting_id),
            )


class ActionItemRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def create(
        self,
        meeting_id: int,
        description: str,
        owner: str | None = None,
        due_date: str | None = None,
    ) -> int:
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO action_items
                    (meeting_id, description, owner, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (meeting_id, description, owner, due_date),
            )

        if cursor.lastrowid is None:
            raise RuntimeError("Action-item insert did not return an ID")

        return cursor.lastrowid

    def list_for_meeting(self, meeting_id: int) -> list[ActionItem]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, meeting_id, description, owner, status, due_date
                FROM action_items
                WHERE meeting_id = ?
                ORDER BY id
                """,
                (meeting_id,),
            ).fetchall()

        return [action_item_from_row(dict(row)) for row in rows]

    def mark_done(self, action_item_id: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE action_items
                SET status = 'done'
                WHERE id = ?
                """,
                (action_item_id,),
            )

    def mark_open(self, action_item_id: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE action_items
                SET status = 'open'
                WHERE id = ?
                """,
                (action_item_id,),
            )

    def delete(self, action_item_id: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                DELETE FROM action_items
                WHERE id = ?
                """,
                (action_item_id,),
            )
