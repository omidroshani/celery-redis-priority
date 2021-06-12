from unittest import TestCase, mock, skip
from tasks import wait, sleep_seconds
from time import sleep
from celery import group, chord, chain

# Priorities:   0, 3, 6, 9
# Queues:       a-high, b-medium, c-low

class TestPriority(TestCase):

    def test(self):
        """
        Test a simple FIFO queue with priority (de)escalation
        """
        tasks = [
            { "priority": 0, "fixture_name": "A" },
            { "priority": 0, "fixture_name": "B" },
            { "priority": 0, "fixture_name": "C" },
            { "priority": 9, "fixture_name": "D" }, # deescalate
            { "priority": 0, "fixture_name": "E" },
            { "priority": 0, "fixture_name": "F" },
            { "priority": 9, "fixture_name": "G" }, # deescalate
            { "priority": 0, "fixture_name": "H" },
        ]
        results = [] 
        for task in tasks:
            print(f"Task {task['fixture_name']} with {task['priority']} priority was sent to queue !")
            t = wait.s(**task)
            results.append(t.apply_async(priority=task["priority"]))

        complete = False
        success = []
        while not complete:
            complete = True
            for r in results:
                if r.state != "SUCCESS":
                    complete = False
                else:
                    v = r.result
                    if v not in success:
                        success.append(v)
                        print(f"Task {v} was completed :)")
            sleep(sleep_seconds)

        self.assertEqual(
            success,
            ["A", "B", "C", "E", "F", "H", "D", "G"],
            "Numeric Priority not completed in expected order"
        )



class TestPriorityQueue(TestCase):
    def test(self):
        """
        Test a simple FIFO queue with priority (de)escalation
        This test shows that priority is honored above queue order
        """
        tasks = [
            { "priority": 0, "fixture_name": "A", "queue":"a-high"},
            { "priority": 0, "fixture_name": "B", "queue":"b-medium"},
            { "priority": 9, "fixture_name": "C", "queue":"b-medium"},
            { "priority": 3, "fixture_name": "D", "queue":"a-high"},
            { "priority": 3, "fixture_name": "E", "queue":"a-high"},
            { "priority": 3, "fixture_name": "F", "queue":"b-medium"},
            { "priority": 3, "fixture_name": "G", "queue":"a-high"},
            { "priority": 9, "fixture_name": "H", "queue":"a-high"},
        ]
        results = [] 
        for task in tasks:
            t = wait.s(**task)
            results.append(t.apply_async(priority=task["priority"], queue=task["queue"]))

        complete = False
        success = []
        while not complete:
            complete = True
            for r in results:
                if r.state != "SUCCESS":
                    complete = False
                else:
                    v = r.result
                    if v not in success:
                        success.append(v)
            sleep(sleep_seconds)
        self.assertEqual(
            success,
            ["A", "B", "D", "E", "G", "F", "H", "C"],
            "Numeric Priority not completed in expected order"
        )



a = TestPriority()
a.test()