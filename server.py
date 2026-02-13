from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from scheduler import Order, Vehicle, schedule_orders


ROOT = Path(__file__).parent
WEB_DIR = ROOT / "web"


class BadRequestError(ValueError):
    pass


def _parse_coord(raw: Sequence[Any], field_name: str) -> Tuple[float, float]:
    if not isinstance(raw, list) or len(raw) != 2:
        raise BadRequestError(f"{field_name} must be [lat, lng]")
    lat = float(raw[0])
    lng = float(raw[1])
    return lat, lng


def _validate_priority(priority: int) -> int:
    if priority < 1 or priority > 5:
        raise BadRequestError("priority must be in range [1, 5]")
    return priority


def _parse_orders(orders_raw: List[Dict[str, Any]]) -> List[Order]:
    parsed: List[Order] = []
    for o in orders_raw:
        parsed.append(
            Order(
                id=str(o["id"]),
                pickup=_parse_coord(o["pickup"], "pickup"),
                dropoff=_parse_coord(o["dropoff"], "dropoff"),
                weight=float(o["weight"]),
                priority=_validate_priority(int(o["priority"])),
                deadline_hour=float(o["deadline_hour"]),
            )
        )
    return parsed


def _parse_vehicles(vehicles_raw: List[Dict[str, Any]]) -> List[Vehicle]:
    parsed: List[Vehicle] = []
    for v in vehicles_raw:
        capacity = float(v["capacity"])
        speed = float(v["speed_kmph"])
        if capacity <= 0:
            raise BadRequestError("vehicle capacity must be > 0")
        if speed <= 0:
            raise BadRequestError("vehicle speed_kmph must be > 0")

        parsed.append(
            Vehicle(
                id=str(v["id"]),
                location=_parse_coord(v["location"], "location"),
                capacity=capacity,
                speed_kmph=speed,
                available_from_hour=float(v.get("available_from_hour", 0)),
            )
        )
    return parsed


class LogisticsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            self._send_json({"status": "ok"})
            return
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/schedule":
            self._send_json({"error": "Not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw.decode("utf-8"))
            orders_raw: List[Dict[str, Any]] = body.get("orders", [])
            vehicles_raw: List[Dict[str, Any]] = body.get("vehicles", [])
            if not isinstance(orders_raw, list) or not isinstance(vehicles_raw, list):
                raise BadRequestError("orders and vehicles must be arrays")

            orders = _parse_orders(orders_raw)
            vehicles = _parse_vehicles(vehicles_raw)
            result = schedule_orders(orders, vehicles)
            self._send_json(
                {
                    "assignments": [a.__dict__ for a in result.assignments],
                    "unassigned_orders": result.unassigned_orders,
                    "total_score": result.total_score,
                    "summary": {
                        "orders_total": len(orders),
                        "orders_assigned": len(result.assignments),
                        "orders_unassigned": len(result.unassigned_orders),
                    },
                }
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json({"error": f"Bad request: {exc}"}, status=400)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), LogisticsHandler)
    print(f"Logistics AI dispatch server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
