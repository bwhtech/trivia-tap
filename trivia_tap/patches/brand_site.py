import frappe


# frappe signs its mails (codes, password resets) with the site's app name and logo
def execute():
	settings = frappe.get_single("Website Settings")
	if settings.app_name in (None, "", "Frappe"):
		settings.app_name = "TriviaTap"
	if not settings.app_logo:
		settings.app_logo = "/assets/trivia_tap/images/trivia-tap-logo.png"
	settings.save()
