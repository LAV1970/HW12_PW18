import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from models import Note, Tag, User  # Update this line
from schemas import NoteModel, NoteUpdate, NoteStatusUpdate  # Update this line
from main import (
    get_notes,
    get_note,
    create_note,
    remove_note,
    update_note,
    update_status_note,
)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_notes(self):
        notes = [Note(), Note(), Note()]
        self.session.query().filter().offset().limit().all.return_value = notes
        result = await get_notes(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, notes)

    async def test_get_note_found(self):
        note = Note()
        self.session.query().filter().first.return_value = note
        result = await get_note(note_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_get_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_note(note_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_note(self):
        body = NoteModel(title="test", description="test note", tags=[1, 2])
        tags = [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]
        self.session.query().filter().all.return_value = tags
        result = await create_note(body=body, user=self.user, db=self.session)
        self.assertEqual(result.title, body.title)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.tags, tags)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_note_found(self):
        note = Note()
        self.session.query().filter().first.return_value = note
        result = await remove_note(note_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_remove_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_note(note_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_note_found(self):
        body = NoteUpdate(title="test", description="test note", tags=[1, 2], done=True)
        self.mock_tags_query()
        note = Note(tags=self.mock_tags())
        self.session.query().filter().first.return_value = note
        self.session.query().filter().all.return_value = note.tags
        self.session.commit.return_value = None
        result = await update_note(
            note_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, note)

    async def test_update_status_note_found(self):
        body = NoteStatusUpdate(done=True)
        note = Note()
        self.session.query().filter().first.return_value = note
        self.session.commit.return_value = None
        result = await update_status_note(
            note_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, note)

    def mock_tags_query(self):
        tags = [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]
        self.session.query().filter().all.return_value = tags

    def mock_tags(self):
        return [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]


if __name__ == "__main__":
    unittest.main()
