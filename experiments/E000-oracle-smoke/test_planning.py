import unittest

from src.planning import Edge, Task, is_correct, shortest_distance


DIRECT = Task("S", "G", (Edge("S", "J"), Edge("J", "G")))
KEY_DETOUR = Task(
    "S", "G",
    (
        Edge("S", "J"),
        Edge("J", "K"),
        Edge("K", "J"),
        Edge("J", "G", requires_key=True),
    ),
    key_at="K",
)
UNREACHABLE = Task("S", "G", (Edge("S", "G", requires_key=True),), key_at="K")


class PlanningOracleTest(unittest.TestCase):
    def test_direct_chain(self):
        self.assertEqual(shortest_distance(DIRECT), 2)

    def test_key_detour_requires_revisiting_a_node(self):
        self.assertEqual(shortest_distance(KEY_DETOUR), 4)
        self.assertTrue(is_correct(KEY_DETOUR, {"path": ["S", "J", "K", "J", "G"]}))

    def test_unreachable_goal(self):
        self.assertIsNone(shortest_distance(UNREACHABLE))
        self.assertTrue(is_correct(UNREACHABLE, {"unreachable": True}))

    def test_starting_on_goal(self):
        task = Task("G", "G", ())
        self.assertEqual(shortest_distance(task), 0)
        self.assertTrue(is_correct(task, {"path": ["G"]}))

    def test_starting_on_key(self):
        task = Task("K", "G", (Edge("K", "G", requires_key=True),), key_at="K")
        self.assertEqual(shortest_distance(task), 1)
        self.assertTrue(is_correct(task, {"path": ["K", "G"]}))

    def test_rejects_a_locked_step(self):
        self.assertFalse(is_correct(KEY_DETOUR, {"path": ["S", "J", "G"]}))

    def test_rejects_a_valid_but_suboptimal_path(self):
        task = Task("S", "G", DIRECT.edges + (Edge("S", "G"),))
        self.assertFalse(is_correct(task, {"path": ["S", "J", "G"]}))

    def test_rejects_a_false_unreachable_answer(self):
        self.assertFalse(is_correct(DIRECT, {"unreachable": True}))

    def test_rejects_an_answer_with_both_forms(self):
        self.assertFalse(is_correct(UNREACHABLE, {"unreachable": True, "path": ["S", "G"]}))
