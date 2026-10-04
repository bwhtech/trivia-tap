import frappe


# frappe signs its mails (codes, password resets) with the site's app name and logo
def execute():
	settings = frappe.get_single("Website Settings")
	if settings.app_name in (None, "", "Frappe"):
		settings.app_name = "TriviaTap"
	if not settings.app_logo:
		settings.app_logo = "/assets/trivia_tap/images/trivia-tap-logo.png"
	settings.save()

	# frappe gives this role to users who sign up with Google
	if not frappe.db.get_single_value("Portal Settings", "default_role"):
		frappe.db.set_single_value("Portal Settings", "default_role", "Quiz Host")
