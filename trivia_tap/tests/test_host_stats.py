import frappe
from frappe.tests import IntegrationTestCase

from trivia_tap.api import generate_game_pin, get_host_stats

HOST = "stats.host@example.com"
OTHER_HOST = "other.stats.host@example.com"


class TestHostStats(IntegrationTestCase):
	def setUp(self):
		for email in (HOST, OTHER_HOST):
			if not frappe.db.exists("User", email):
				frappe.get_doc(
					{
						"doctype": "User",
						"email": email,
						"first_name": "Host",
						"roles": [{"role": "Quiz Host"}],
					}
				).insert(ignore_permissions=True)
		# IntegrationTestCase rolls back per class, so each test starts from no games
		sessions = frappe.get_all("TT Session", {"host": ("in", (HOST, OTHER_HOST))}, pluck="name")
		frappe.db.delete("TT Participant", {"session": ("in", sessions)})
		frappe.db.delete("TT Session", {"name": ("in", sessions)})
		frappe.db.delete("TT Quiz", {"owner": ("in", (HOST, OTHER_HOST))})

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def test_new_host_has_zeros(self):
		frappe.set_user(HOST)
		self.assertEqual(get_host_stats(), {"games_hosted": 0, "players_reached": 0, "quizzes_written": 0})

	def test_counts_ended_games_and_players_who_stayed(self):
		quiz = make_quiz(HOST)
		make_session(quiz, HOST, "Ended", players=["ana", "ben"], kicked=["cat"])
		make_session(quiz, HOST, "Cancelled", players=["dan"])
		make_quiz(HOST)

		frappe.set_user(HOST)
		self.assertEqual(get_host_stats(), {"games_hosted": 1, "players_reached": 2, "quizzes_written": 2})

	def test_another_hosts_games_do_not_count(self):
		quiz = make_quiz(OTHER_HOST)
		make_session(quiz, OTHER_HOST, "Ended", players=["ana"])

		frappe.set_user(HOST)
		self.assertEqual(get_host_stats(), {"games_hosted": 0, "players_reached": 0, "quizzes_written": 0})


def make_quiz(owner: str) -> str:
	quiz = frappe.get_doc(
		{
			"doctype": "TT Quiz",
			"title": "Stats Quiz",
			"questions": [
				{
					"question_text": "2 + 2?",
					"option_1": "3",
					"option_2": "4",
					"option_3": "5",
					"option_4": "6",
					"correct_option": "2",
				}
			],
		}
	).insert(ignore_permissions=True)
	frappe.db.set_value("TT Quiz", quiz.name, "owner", owner)
	return quiz.name


def make_session(quiz: str, host: str, status: str, players: list[str], kicked: list[str] | None = None):
	session = frappe.get_doc(
		{
			"doctype": "TT Session",
			"quiz": quiz,
			"host": host,
			"status": status,
			"game_pin": generate_game_pin(),
		}
	).insert(ignore_permissions=True)
	for nickname in players + (kicked or []):
		frappe.get_doc(
			{
				"doctype": "TT Participant",
				"session": session.name,
				"nickname": nickname,
				"kicked": int(nickname in (kicked or [])),
			}
		).insert(ignore_permissions=True)
