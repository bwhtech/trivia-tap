import frappe

from trivia_tap.avatars import get_boot_pack
from trivia_tap.nicknames import get_boot_words


def get_context(context):
	context.no_cache = 1
	user = frappe.db.get_value("User", frappe.session.user, ["first_name", "user_image"], as_dict=True)
	context.boot = {
		"csrf_token": frappe.sessions.get_csrf_token(),
		"site_name": frappe.local.site,
		"session_user": frappe.session.user,
		"first_name": user.first_name,
		"user_image": user.user_image,
		"avatar_pack": get_boot_pack(),
		"nickname_words": get_boot_words(),
	}
