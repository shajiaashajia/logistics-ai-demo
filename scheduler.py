from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Optional, Tuple


@dataclass
class Order:
    id: str
    pickup: Tuple[float, float]
    dropoff: Tuple[float, float]
    weight: float
    priority: int  # 1-5, 5 = highest
    deadline_hour: float


@dataclass
class Vehicle:
    id: str
    location: Tuple[float, float]
    capacity: float
    speed_kmph: float
    available_from_hour: float = 0.0


@dataclass
class Assignment:
    order_id: str
    vehicle_id: str
    eta_hour: float
    score: float
    travel_km: float
    deadline_breached: bool


@dataclass
class DispatchResult:
    assignments: List[Assignment]
    unassigned_orders: List[str]
    total_score: float


def _distance_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) * 111.0


def _score_candidate(order: Order, vehicle: Vehicle) -> Optional[Tuple[float, float, float]]:
    if order.weight > vehicle.capacity:
        return None

    to_pickup = _distance_km(vehicle.location, order.pickup)
    delivery_leg = _distance_km(order.pickup, order.dropoff)
    total_distance = to_pickup + delivery_leg
    travel_time = total_distance / max(vehicle.speed_kmph, 1.0)
    eta = vehicle.available_from_hour + travel_time

    priority_bonus = order.priority * 20.0
    distance_penalty = total_distance * 0.5
    deadline_penalty = max(0.0, eta - order.deadline_hour) * 40.0
    utilization_bonus = (order.weight / max(vehicle.capacity, 1.0)) * 15.0

    score = priority_bonus + utilization_bonus - distance_penalty - deadline_penalty
    return score, eta, total_distance


def schedule_orders(orders: List[Order], vehicles: List[Vehicle]) -> DispatchResult:
    order_queue = sorted(orders, key=lambda o: (-o.priority, o.deadline_hour, o.id))

    fleet_state: Dict[str, Vehicle] = {
        v.id: Vehicle(
            id=v.id,
            location=v.location,
            capacity=v.capacity,
            speed_kmph=v.speed_kmph,
            available_from_hour=v.available_from_hour,
        )
        for v in vehicles
    }

    assignments: List[Assignment] = []
    unassigned: List[str] = []
    total_score = 0.0

    for order in order_queue:
        best_vehicle_id: Optional[str] = None
        best_score = float("-inf")
        best_eta = 0.0
        best_distance = 0.0

        for vehicle in fleet_state.values():
            candidate = _score_candidate(order, vehicle)
            if candidate is None:
                continue
            score, eta, distance = candidate
            if score > best_score or (score == best_score and eta < best_eta):
                best_score = score
                best_vehicle_id = vehicle.id
                best_eta = eta
                best_distance = distance

        if best_vehicle_id is None:
            unassigned.append(order.id)
            continue

        chosen = fleet_state[best_vehicle_id]
        chosen.location = order.dropoff
        chosen.available_from_hour = best_eta

        assignments.append(
            Assignment(
                order_id=order.id,
                vehicle_id=best_vehicle_id,
                eta_hour=round(best_eta, 2),
                score=round(best_score, 2),
                travel_km=round(best_distance, 2),
                deadline_breached=best_eta > order.deadline_hour,
            )
        )
        total_score += best_score

    return DispatchResult(assignments=assignments, unassigned_orders=unassigned, total_score=round(total_score, 2))
