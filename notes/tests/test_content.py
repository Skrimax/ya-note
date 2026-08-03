from http import HTTPStatus

from notes.forms import NoteForm
from .base import BaseNotesTestCase


class ContentTests(BaseNotesTestCase):
    def test_note_in_object_list_context(self):
        response = self.client_auth_1.get(self.notes_list_url)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_sees_only_own_notes(self):
        response = self.client_auth_1.get(self.notes_list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        self.assertNotIn(self.note2, notes)

    def test_forms_passed_to_add_pages(self):
        add_response = self.client_auth_1.get(self.add_url)
        self.assertEqual(add_response.status_code, HTTPStatus.OK)
        self.assertIn('form', add_response.context)
        self.assertIsInstance(add_response.context['form'], NoteForm)
        self.assertFalse(add_response.context['form'].is_bound)

    def test_forms_passed_to_edit_pages(self):
        edit_response = self.client_auth_1.get(self.edit_url)
        self.assertEqual(edit_response.status_code, HTTPStatus.OK)
        self.assertIn('form', edit_response.context)
        self.assertIsInstance(edit_response.context['form'], NoteForm)
        self.assertFalse(edit_response.context['form'].is_bound)
        self.assertEqual(edit_response.context['form'].instance, self.note)
