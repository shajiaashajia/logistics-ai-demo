import json
import threading
import time
import unittest
from http.client import HTTPConnection

from server import run


class ServerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 18080
        cls.thread = threading.Thread(target=run, kwargs={"host": "127.0.0.1", "port": cls.port}, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    def test_schedule_success(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=3)
        payload = {
            "orders": [{"id": "O-1", "pickup": [31.2, 121.4], "dropoff": [31.3, 121.5], "weight": 100, "priority": 5, "deadline_hour": 2}],
            "vehicles": [{"id": "V-1", "location": [31.2, 121.4], "capacity": 300, "speed_kmph": 40}],
        }
        conn.request("POST", "/api/schedule", body=json.dumps(payload), headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(resp.status, 200)
        self.assertEqual(data["summary"]["orders_assigned"], 1)

    def test_schedule_bad_priority(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=3)
        payload = {
            "orders": [{"id": "O-1", "pickup": [31.2, 121.4], "dropoff": [31.3, 121.5], "weight": 100, "priority": 6, "deadline_hour": 2}],
            "vehicles": [{"id": "V-1", "location": [31.2, 121.4], "capacity": 300, "speed_kmph": 40}],
        }
        conn.request("POST", "/api/schedule", body=json.dumps(payload), headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        self.assertEqual(resp.status, 400)


if __name__ == "__main__":
    unittest.main()
