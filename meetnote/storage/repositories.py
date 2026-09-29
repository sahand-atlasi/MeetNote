from datetime import datetime, timezone
from pathlib import Path

from meetnote.storage.database import connect


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

    def get(self, meeting_id: int) -> dict | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, title, notes, created_at
                FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
            ).fetchone()

        return dict(row) if row is not None else None

    def list_all(self) -> list[dict]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, title, notes, created_at
                FROM meetings
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def delete(self, meeting_id: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                DELETE FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
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

    def list_for_meeting(self, meeting_id: int) -> list[dict]:
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

        return [dict(row) for row in rows]

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
