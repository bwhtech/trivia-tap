from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils.password import check_password

from trivia_tap.auth import (
	change_password,
	login_with_code,
	reset_password,
	reset_password_with_link,
	send_code,
	send_reset_link,
	sign_up,
)
from trivia_tap.email_code import MAX_TRIES

EMAIL = "new.host@example.com"
PASSWORD = "Quiz-Host-Pass-2026!"
NEW_PASSWORD = "Aspen-Rocket-Mint-64"


class CodeTestCase(IntegrationTestCase):
	def setUp(self):
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		frappe.cache.delete_keys("tt:code")
		frappe.set_user("Guest")
		self.login_manager = patch.object(frappe.local, "login_manager", create=True).start()
		self.signup_disabled = patch("trivia_tap.auth.is_signup_disabled", return_value=False).start()
		self.code_mail = patch("trivia_tap.email_code.send_mail").start()
		self.notice_mail = patch("trivia_tap.auth.send_mail").start()

	def tearDown(self):
		patch.stopall()
		frappe.set_user("Administrator")
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		frappe.cache.delete_keys("tt:code")
		super().tearDown()

	def mailed_code(self, purpose):
		send_code(EMAIL, purpose)
		return self.code_mail.call_args.args[3]["code"]

	def make_host(self):
		frappe.get_doc(
			{"doctype": "User", "email": EMAIL, "first_name": "Host", "new_password": PASSWORD}
		).insert(ignore_permissions=True)


class TestSignUp(CodeTestCase):
	def test_creates_a_logged_in_quiz_host(self):
		code = self.mailed_code("sign_up")
		sign_up("New Host", EMAIL.upper(), PASSWORD, code)

		user = frappe.get_doc("User", EMAIL)
		self.assertIn("Quiz Host", frappe.get_roles(user.name))
		self.assertEqual(user.first_name, "New Host")
		self.login_manager.login_as.assert_called_once_with(EMAIL)

	def test_refuses_a_wrong_code(self):
		code = self.mailed_code("sign_up")

		with self.assertRaisesRegex(frappe.ValidationError, "wrong or has expired"):
			sign_up("New Host", EMAIL, PASSWORD, wrong(code))
		self.assertFalse(frappe.db.exists("User", EMAIL))

	def test_wrong_tries_use_up_the_code(self):
		code = self.mailed_code("sign_up")
		for _try in range(MAX_TRIES):
			with self.assertRaises(frappe.ValidationError):
				sign_up("New Host", EMAIL, PASSWORD, wrong(code))

		with self.assertRaisesRegex(frappe.ValidationError, "wrong or has expired"):
			sign_up("New Host", EMAIL, PASSWORD, code)

	def test_failed_sign_up_keeps_the_code(self):
		code = self.mailed_code("sign_up")
		# frappe skips the password policy in tests, so fail the insert the same way
		with patch("frappe.core.doctype.user.user.User.validate", side_effect=frappe.ValidationError):
			with self.assertRaises(frappe.ValidationError):
				sign_up("New Host", EMAIL, "weak", code)

		sign_up("New Host", EMAIL, PASSWORD, code)
		self.assertTrue(frappe.db.exists("User", EMAIL))

	def test_existing_email_gets_a_notice_not_a_code(self):
		self.make_host()

		send_code(EMAIL, "sign_up")

		self.code_mail.assert_not_called()
		self.assertEqual(self.notice_mail.call_args.args[2], "trivia_tap_account_exists")

	def test_refuses_a_quick_resend(self):
		send_code(EMAIL, "sign_up")

		with self.assertRaises(frappe.RateLimitExceededError):
			send_code(EMAIL, "sign_up")

	def test_refuses_when_sign_up_is_disabled(self):
		self.signup_disabled.return_value = True

		with self.assertRaises(frappe.PermissionError):
			send_code(EMAIL, "sign_up")
		self.code_mail.assert_not_called()


class TestResetPassword(CodeTestCase):
	def test_sets_the_new_password_and_logs_in(self):
		self.make_host()
		code = self.mailed_code("reset_password")

		reset_password(EMAIL, code, NEW_PASSWORD)

		self.assertEqual(check_password(EMAIL, NEW_PASSWORD), EMAIL)
		self.login_manager.login_as.assert_called_once_with(EMAIL)

	def test_unknown_email_gets_no_mail(self):
		send_code(EMAIL, "reset_password")

		self.code_mail.assert_not_called()
		self.notice_mail.assert_not_called()

	def test_a_sign_up_code_cannot_reset(self):
		code = self.mailed_code("sign_up")
		self.make_host()

		with self.assertRaisesRegex(frappe.ValidationError, "wrong or has expired"):
			reset_password(EMAIL, code, NEW_PASSWORD)


class TestLoginWithCode(CodeTestCase):
	def test_logs_in(self):
		self.make_host()
		code = self.mailed_code("log_in")

		login_with_code(EMAIL, code)

		self.login_manager.login_as.assert_called_once_with(EMAIL)

	def test_code_works_once(self):
		self.make_host()
		code = self.mailed_code("log_in")
		login_with_code(EMAIL, code)

		with self.assertRaisesRegex(frappe.ValidationError, "wrong or has expired"):
			login_with_code(EMAIL, code)

	def test_refuses_users_who_need_two_factor(self):
		self.make_host()
		code = self.mailed_code("log_in")

		with patch("trivia_tap.auth.should_run_2fa", return_value=True):
			with self.assertRaisesRegex(frappe.ValidationError, "two-factor"):
				login_with_code(EMAIL, code)
		self.login_manager.login_as.assert_not_called()


def wrong(code):
	return f"{(int(code) + 1) % 10**6:06}"


class TestChangePassword(IntegrationTestCase):
	def setUp(self):
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		frappe.get_doc(
			{"doctype": "User", "email": EMAIL, "first_name": "Host", "new_password": PASSWORD}
		).insert(ignore_permissions=True)
		frappe.set_user(EMAIL)
		login_manager = patch.object(frappe.local, "login_manager", create=True).start()
		login_manager.check_password.side_effect = check_password

	def tearDown(self):
		patch.stopall()
		frappe.set_user("Administrator")
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		super().tearDown()

	def test_changes_the_password(self):
		change_password(PASSWORD, "Aspen-Rocket-Mint-64")

		self.assertEqual(check_password(EMAIL, "Aspen-Rocket-Mint-64"), EMAIL)

	def test_wrong_current_password_is_a_validation_error(self):
		# an AuthenticationError would make frappe clear the session cookies
		with self.assertRaisesRegex(frappe.ValidationError, "Current password is wrong"):
			change_password("not-my-password", "Aspen-Rocket-Mint-64")


class TestResetLink(IntegrationTestCase):
	def setUp(self):
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		frappe.get_doc(
			{"doctype": "User", "email": EMAIL, "first_name": "Host", "new_password": PASSWORD}
		).insert(ignore_permissions=True)
		frappe.set_user(EMAIL)
		self.login_manager = patch.object(frappe.local, "login_manager", create=True).start()
		self.mail = patch("trivia_tap.auth.send_mail").start()

	def tearDown(self):
		patch.stopall()
		frappe.set_user("Administrator")
		frappe.delete_doc_if_exists("User", EMAIL, force=True)
		super().tearDown()

	def mailed_key(self):
		send_reset_link()
		link = self.mail.call_args.args[3]["link"]
		self.assertIn("/trivia-tap/reset-password?key=", link)
		return link.split("key=")[1]

	def test_mails_the_callers_own_inbox(self):
		self.mailed_key()

		self.assertEqual(self.mail.call_args.args[0], EMAIL)

	def test_link_sets_the_new_password_and_logs_in(self):
		key = self.mailed_key()
		frappe.set_user("Guest")

		reset_password_with_link(key, NEW_PASSWORD)

		self.assertEqual(check_password(EMAIL, NEW_PASSWORD), EMAIL)
		self.login_manager.login_as.assert_called_once_with(EMAIL)

	def test_link_works_once(self):
		key = self.mailed_key()
		reset_password_with_link(key, NEW_PASSWORD)

		with self.assertRaisesRegex(frappe.ValidationError, "already used or has expired"):
			reset_password_with_link(key, "Cedar-Comet-Plum-91")

	def test_refuses_administrator(self):
		frappe.set_user("Administrator")

		with self.assertRaises(frappe.ValidationError):
			send_reset_link()
		self.mail.assert_not_called()
