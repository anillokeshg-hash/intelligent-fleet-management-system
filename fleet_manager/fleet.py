"""Simulated fleet: vehicles that move around and report telemetry."""
import math
import random

# Map centre (change to your city). Vehicles roam within a small area around it.
CENTER_LAT, CENTER_LON = 28.6139, 77.2090

DRIVERS = ["Ravi", "Anita", "Suresh", "Priya", "Kiran", "Meena", "Arjun", "Divya"]
TYPES = ["Truck", "Van", "Truck", "Car", "Van", "Truck", "Car", "Van"]


class Vehicle:
    def __init__(self, idx):
        self.id = f"FL-{101 + idx}"
        self.type = TYPES[idx % len(TYPES)]
        self.driver = DRIVERS[idx % len(DRIVERS)]
        self.lat = CENTER_LAT + random.uniform(-0.05, 0.05)
        self.lon = CENTER_LON + random.uniform(-0.05, 0.05)
        self.heading = random.uniform(0, 360)  # degrees
        self.speed = random.uniform(30, 60)  # km/h
        self.fuel = random.uniform(30, 100)  # percent
        self.km_since_service = random.uniform(500, 14000)
        self.tyre_pressure = random.uniform(29, 35)  # psi
        self.battery_voltage = random.uniform(11.6, 12.8)
        self.wear = self.km_since_service / 15000  # 0..1, drives engine heat
        self.engine_temp = 80.0
        self.fuel_efficiency = random.uniform(6, 14)  # km/l

    def step(self):
        """Advance the vehicle by one simulated time step."""
        # speed random walk
        self.speed = min(max(self.speed + random.uniform(-8, 8), 0), 110)
        # steer a little, stay near the map centre
        self.heading += random.uniform(-25, 25)
        if abs(self.lat - CENTER_LAT) > 0.08 or abs(self.lon - CENTER_LON) > 0.08:
            self.heading = math.degrees(
                math.atan2(CENTER_LON - self.lon, CENTER_LAT - self.lat)
            )
        km = self.speed / 3600 * 20  # each step ~ 20 simulated seconds
        self.lat += math.cos(math.radians(self.heading)) * km / 111
        self.lon += math.sin(math.radians(self.heading)) * km / 111
        self.km_since_service += km
        self.fuel -= km / self.fuel_efficiency / 0.6  # tank ~60 L
        if self.fuel < 5:  # refuel
            self.fuel = 100.0
        self.engine_temp = 80 + self.speed * 0.12 + self.wear * 25 + random.uniform(-2, 2)
        self.tyre_pressure += random.uniform(-0.05, 0.02)
        self.battery_voltage += random.uniform(-0.02, 0.02)

    def telemetry(self):
        return {
            "id": self.id,
            "type": self.type,
            "driver": self.driver,
            "lat": round(self.lat, 5),
            "lon": round(self.lon, 5),
            "speed": round(self.speed, 1),
            "fuel": round(self.fuel, 1),
            "engine_temp": round(self.engine_temp, 1),
            "tyre_pressure": round(self.tyre_pressure, 1),
            "battery_voltage": round(self.battery_voltage, 2),
            "km_since_service": round(self.km_since_service),
            "fuel_efficiency": round(self.fuel_efficiency, 1),
        }


class Fleet:
    def __init__(self, n=8):
        self.vehicles = [Vehicle(i) for i in range(n)]

    def step(self):
        for v in self.vehicles:
            v.step()
        return [v.telemetry() for v in self.vehicles]
