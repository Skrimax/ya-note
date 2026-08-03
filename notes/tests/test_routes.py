from http import HTTPStatus

from .base import BaseNotesTestCase


class RoutesAccessTests(BaseNotesTestCase):
    def test_home_page_available_for_anonymous(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_list_available_for_authenticated(self):
        response = self.client_auth_1.get(self.notes_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_done_page_available_for_authenticated(self):
        response = self.client_auth_1.get(self.success_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_page_available_for_authenticated(self):
        response = self.client_auth_1.get(self.add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_edit_delete_available_only_for_author(self):
        paths = [
            self.detail_url,
            self.edit_url,
            self.delete_url,
        ]

        for path in paths:
            with self.subTest(path=path, user='author'):
                response = self.client_auth_1.get(path)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f"Автор не может открыть: {path}"
                )

        for path in paths:
            with self.subTest(path=path, user='other'):
                response = self.client_auth_2.get(path)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    f"Чужой пользователь видит: {path}"
                )

    def test_anonymous_redirected_to_login_on_protected_pages(self):
        protected_paths = [
            self.notes_list_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        ]

        for path in protected_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                expected_redirect = f"{self.login_url}?next={path}"
                self.assertRedirects(response, expected_redirect)

    def test_public_auth_pages_available_to_all(self):
        public_paths = [
            self.login_url,
            self.signup_url,
        ]

        for path in public_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_requires_post(self):
        response_get = self.client.get(self.logout_url)
        self.assertEqual(response_get.status_code,
                         HTTPStatus.METHOD_NOT_ALLOWED
                         )

    def test_logout_post_performs_logout_and_redirects(self):
        response_post = self.client_auth_1.post(self.logout_url)
        self.assertEqual(response_post.status_code, HTTPStatus.OK)
        self.assertFalse(self.client_auth_1.session.get('_auth_user_id'))
