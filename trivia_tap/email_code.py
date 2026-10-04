import hmac
import secrets

import frappe
from frappe import _
from frappe.utils import sha256_hash

LIFETIME_MINUTES = 10
RESEND_AFTER_SECONDS = 30
MAX_TRIES = 5

SUBJECTS = {
	"sign_up": "Your TriviaTap sign up code",
	"reset_password": "Your TriviaTap password reset code",
	"log_in": "Your TriviaTap log in code",
}


class EmailCode:
	"""A 6-digit code mailed to prove the caller reads this inbox, kept hashed in Redis."""

	def __init__(self, purpose: str, email: str):
		self.purpose = purpose
		self.email = email
		self.key = f"tt:code:{purpose}:{email}"

	def throttle(self) -> None:
		# per email, not per IP: one inbox must not be flooded from many addresses
		sent_key = f"tt:code_sent:{self.purpose}:{self.email}"
		if frappe.cache.get_value(sent_key):
			frappe.throw(_("Wait a few seconds before asking for a new code."), frappe.RateLimitExceededError)
		frappe.cache.set_value(sent_key, 1, expires_in_sec=RESEND_AFTER_SECONDS)

	def send(self) -> None:
		code = f"{secrets.randbelow(10**6):06}"
		frappe.cache.set_value(self.key, sha256_hash(code), expires_in_sec=LIFETIME_MINUTES * 60)
		frappe.cache.delete_value(self.tries_key)
		send_mail(
			self.email,
			_(SUBJECTS[self.purpose]),
			"trivia_tap_code",
			{"code": code, "minutes": LIFETIME_MINUTES, "purpose": self.purpose},
		)

	def check(self, code: str) -> None:
		stored = frappe.cache.get_value(self.key)
		if stored and hmac.compare_digest(stored, sha256_hash(code.strip())):
			return
		if stored and self.count_try() >= MAX_TRIES:
			self.clear()
		frappe.throw(_("That code is wrong or has expired."))

	def clear(self) -> None:
		frappe.cache.delete_value([self.key, self.tries_key])

	@property
	def tries_key(self) -> str:
		return f"{self.key}:tries"

	def count_try(self) -> int:
		# INCR is atomic, so parallel guesses cannot share one try
		key = frappe.cache.make_key(self.tries_key)
		tries = frappe.cache.incr(key)
		frappe.cache.expire(key, LIFETIME_MINUTES * 60)
		return tries


def send_mail(email: str, subject: str, template: str, args: dict) -> None:
	frappe.sendmail(
		recipients=email,
		subject=subject,
		template=template,
		args=args,
		with_container=True,
		wrapper="templates/emails/auth_email.html",
		now=True,
	)
