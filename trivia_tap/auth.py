from urllib.parse import parse_qs, urlsplit

import frappe
from frappe import _
from frappe.core.doctype.user.user import get_signup_limit, update_password
from frappe.rate_limiter import rate_limit
from frappe.twofactor import should_run_2fa
from frappe.utils import cint, escape_html, get_url, validate_email_address
from frappe.website.utils import is_signup_disabled

from trivia_tap.email_code import SUBJECTS, EmailCode, send_mail


# nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=10 * 60)
def send_code(email: str, purpose: str) -> None:
	email = clean_email(email)
	if purpose not in SUBJECTS:
		frappe.throw(_("Unknown code purpose."))
	if purpose == "sign_up":
		check_signup_open()
	EmailCode(purpose, email).throttle()
	# the mail goes out from a job either way, so the response time does not tell
	# whether the email has an account
	frappe.enqueue(deliver_code, queue="short", email=email, purpose=purpose, now=frappe.flags.in_test)


# Frappe's own sign_up only mails a password link; a host wants to write a quiz
# right away, so this one takes the password and logs them in.
# nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=get_signup_limit, seconds=60)
def sign_up(full_name: str, email: str, password: str, code: str) -> None:
	email = clean_email(email)
	check_signup_open()
	email_code = EmailCode("sign_up", email)
	email_code.check(code)
	# same wording as frappe, so the form cannot tell which emails have accounts
	if frappe.db.exists("User", {"email": email}):
		frappe.throw(_("We could not create an account with the provided details."))

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(full_name.strip()),
			"new_password": password,
			"send_welcome_email": 0,
			"roles": [{"role": "Quiz Host"}],
		}
	)
	user.flags.ignore_permissions = True
	user.insert()
	email_code.clear()
	frappe.local.login_manager.login_as(user.name)


# nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=10 * 60)
def reset_password(email: str, code: str, new_password: str) -> None:
	email = clean_email(email)
	email_code = EmailCode("reset_password", email)
	email_code.check(code)
	user = active_user(email)
	if not user:
		frappe.throw(_("That code is wrong or has expired."))
	# frappe's update_password owns the policy, reuse check, session log out and login
	update_password(new_password, key=reset_key(user))
	email_code.clear()


# nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=10 * 60)
def login_with_code(email: str, code: str) -> None:
	email = clean_email(email)
	email_code = EmailCode("log_in", email)
	email_code.check(code)
	user = active_user(email)
	if not user:
		frappe.throw(_("That code is wrong or has expired."))
	email_code.clear()
	# login_as skips frappe's two-factor check, so those users must use their password
	if should_run_2fa(user):
		frappe.throw(_("Your account needs two-factor login. Log in with your password."))
	frappe.local.login_manager.login_as(user)


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=10, seconds=10 * 60)
def change_password(old_password: str, new_password: str) -> None:
	# frappe clears the session cookies on an AuthenticationError, so a typo in the
	# current password would log the host out of the page they are on
	try:
		frappe.local.login_manager.check_password(frappe.session.user, old_password)
	except frappe.AuthenticationError:
		frappe.throw(_("Current password is wrong."))
	update_password(new_password, old_password=old_password)


def deliver_code(email: str, purpose: str) -> None:
	if purpose == "sign_up" and frappe.db.exists("User", {"email": email}):
		send_mail(
			email,
			_("You already have a TriviaTap account"),
			"trivia_tap_account_exists",
			{"link": get_url("/trivia-tap/login")},
		)
	elif purpose == "sign_up" or active_user(email):
		EmailCode(purpose, email).send()


def check_signup_open() -> None:
	if is_signup_disabled():
		frappe.throw(_("Sign up is disabled on this site."), frappe.PermissionError)
	if signups_past_hour_exceeded():
		frappe.throw(_("Too many sign ups right now. Try again in an hour."), frappe.RateLimitExceededError)


def active_user(email: str) -> str | None:
	user = frappe.db.get_value("User", {"email": email, "enabled": 1}, "name")
	return user if user != "Administrator" else None


def reset_key(user: str) -> str:
	link = frappe.get_doc("User", user)._reset_password()
	return parse_qs(urlsplit(link).query)["key"][0]


def clean_email(email: str) -> str:
	email = email.strip().lower()
	validate_email_address(email, throw=True)
	return email


def signups_past_hour_exceeded() -> bool:
	limit = cint(frappe.get_system_settings("max_signups_allowed_per_hour") or 300)
	return frappe.db.get_creation_count("User", 60) >= limit
