import unittest

from scheduler import Order, Vehicle, schedule_orders


class SchedulerTests(unittest.TestCase):
    def test_assigns_high_priority_orders(self):
        orders = [
            Order("o1", (31.2, 121.4), (31.3, 121.5), 50, 5, 3),
            Order("o2", (31.21, 121.41), (31.18, 121.37), 60, 2, 8),
        ]
        vehicles = [
            Vehicle("v1", (31.2, 121.4), 200, 45),
            Vehicle("v2", (31.4, 121.6), 200, 45),
        ]

        result = schedule_orders(orders, vehicles)

        self.assertEqual(len(result.assignments), 2)
        self.assertGreater(result.total_score, 0)
        self.assertTrue(all(a.travel_km > 0 for a in result.assignments))

    def test_unassigned_when_capacity_not_enough(self):
        orders = [Order("o-heavy", (31.2, 121.4), (31.3, 121.5), 999, 5, 3)]
        vehicles = [Vehicle("v1", (31.2, 121.4), 100, 45)]

        result = schedule_orders(orders, vehicles)

        self.assertEqual(result.unassigned_orders, ["o-heavy"])
        self.assertEqual(result.assignments, [])

    def test_vehicle_availability_keeps_fractional_time(self):
        orders = [
            Order("o1", (31.2, 121.4), (31.201, 121.402), 50, 5, 10),
            Order("o2", (31.26, 121.46), (31.31, 121.52), 50, 4, 10),
        ]
        vehicles = [Vehicle("v1", (31.2, 121.4), 100, 30)]

        result = schedule_orders(orders, vehicles)

        self.assertEqual(len(result.assignments), 2)
        self.assertLess(result.assignments[0].eta_hour, result.assignments[1].eta_hour)


if __name__ == "__main__":
    unittest.main()
