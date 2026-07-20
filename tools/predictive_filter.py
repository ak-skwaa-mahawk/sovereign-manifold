#!/usr/bin/env python3
# predictive_filter.py — Lightweight 3D Constant-Velocity Kalman Filter (v1.0.0)
import math
import time

class ManifoldKalmanFilter:
    def __init__(self):
        # State vector: [x, y, z, vx, vy, vz]
        self.state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Diagonal Covariance Matrix P (Uncertainty) representing variance of each state element
        self.P = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        
        # Process Noise Covariance Q (system variance over time)
        self.Q = [0.05, 0.05, 0.05, 0.1, 0.1, 0.1]
        
        # Measurement Noise Covariance R (sensor error)
        self.R = [0.1, 0.1, 0.1]
        
        self.last_time = None
        self.boundary_limit = 5.0  # Max allowable vector divergence radius

    def update(self, z_meas):
        """
        Executes a predictable Predict/Correct cycle using spatial list arithmetic.
        z_meas: list of 3 floats [x, y, z] observed from the live stream
        """
        current_time = time.time()
        if self.last_time is None:
            self.state[0:3] = z_meas
            self.last_time = current_time
            return self.get_summary()

        dt = current_time - self.last_time
        if dt <= 0:
            dt = 0.001
        self.last_time = current_time

        # 1. PREDICT STEP
        # Extrapolate position using estimated velocity: x = x + vx * dt
        self.state[0] += self.state[3] * dt
        self.state[1] += self.state[4] * dt
        self.state[2] += self.state[5] * dt
        
        # Grow uncertainty over time: P = P + Q * dt
        for i in range(6):
            self.P[i] += self.Q[i] * dt

        # 2. CORRECT STEP
        # Innovation residuals (observed - predicted)
        res = [
            z_meas[0] - self.state[0],
            z_meas[1] - self.state[1],
            z_meas[2] - self.state[2]
        ]

        # Compute Kalman Gain: K = P / (P + R) for each measurement channel
        for i in range(3):
            S = self.P[i] + self.R[i]
            K = self.P[i] / S
            
            # Update state estimate with measurement input
            self.state[i] += K * res[i]
            # Update velocity state estimate using position residual mapping
            self.state[i+3] += (K / dt) * res[i] if dt > 0 else 0.0
            
            # Reduce uncertainty after mapping update
            self.P[i] *= (1.0 - K)
            self.P[i+3] *= (1.0 - K)

        return self.get_summary()

    def get_summary(self):
        x, y, z, vx, vy, vz = self.state
        v_mag = math.sqrt(vx**2 + vy**2 + vz**2)
        pos_mag = math.sqrt(x**2 + y**2 + z**2)
        avg_uncertainty = sum(self.P[0:3]) / 3.0

        # Calculate projected time-to-impact if moving toward safety margins
        time_to_limit = None
        if v_mag > 0.001:
            # Radial velocity component approximation
            v_radial = (x*vx + y*vy + z*vz) / pos_mag if pos_mag > 0 else 0
            if v_radial > 0:  # Moving outward
                distance_left = self.boundary_limit - pos_mag
                time_to_limit = max(0.0, distance_left / v_radial) if distance_left > 0 else 0.0

        return {
            "coords_est": [round(x, 4), round(y, 4), round(z, 4)],
            "v_magnitude": round(v_mag, 4),
            "uncertainty": round(avg_uncertainty, 4),
            "time_to_limit": round(time_to_limit, 2) if time_to_limit is not None else None
        }
