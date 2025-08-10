# simulation.py
# This script integrates the CARLA simulator with the ethical decision-making engine.
# It spawns the ego vehicle and scenario actors (cars/pedestrians),
# applies the decision logic based on the chosen ethical mode,
# controls the vehicle accordingly, takes a screenshot, and logs the result.

import carla
import time
import os
import csv
from datetime import datetime
from ethics_engine import utilitarian_decision, deontological_decision, virtue_ethics_decision

# === Connect to CARLA ===
# Connects to the CARLA server on localhost at port 2000 with a timeout.
client = carla.Client("localhost", 2000)
client.set_timeout(10.0)
world = client.get_world()

# === Clear actors ===
# Removes all vehicles and pedestrians from the world to start fresh.
for actor in world.get_actors().filter("*vehicle*"):
    actor.destroy()
for actor in world.get_actors().filter("*walker*"):
    actor.destroy()

# === Setup ===
# Loads blueprints for vehicles and pedestrians from CARLA's library.
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.filter("vehicle.*")[0]
car_bp = blueprint_library.filter("vehicle.*")[1]
ped_bp = blueprint_library.filter("walker.pedestrian.*")

# Retrieves spawn points and spawns the ego vehicle.
spawn_points = world.get_map().get_spawn_points()
vehicle_transform = spawn_points[0]
vehicle = world.try_spawn_actor(vehicle_bp, vehicle_transform)
if not vehicle:
    raise RuntimeError("Vehicle spawn failed.")

# Sets the spectator view to the ego vehicle's position.
spectator = world.get_spectator()
spectator.set_transform(vehicle.get_transform())

# === USER CONFIGURATION ===
scenario_name = "pedestrian_vs_pedestrian"      # Options: car_vs_car, car_vs_pedestrian, pedestrian_vs_pedestrian
ethical_mode = "virtue"             # Options: utilitarian, deontological, virtue
# ===========================

# === Scenario input data for decision functions ===
scenario_input = {
    "name": scenario_name,
    "left_risk": 9,
    "right_risk": 5,
    "left_is_child": True  
}

# === Spawn scenario actors ===
actors = []
origin = vehicle.get_transform().location
distance = 15 # Distance in meters ahead of the ego vehicle

# Spawns different combinations of cars and pedestrians depending on scenario type.
if scenario_name == "car_vs_pedestrian":
    # Left = car, Right = pedestrian
    left_car = world.try_spawn_actor(car_bp, carla.Transform(origin + carla.Location(x=distance, y=-1.5, z=0.5)))
    right_ped = world.try_spawn_actor(ped_bp[0], carla.Transform(origin + carla.Location(x=distance, y=1.5, z=0.5)))
    actors.extend([left_car, right_ped])

elif scenario_name == "car_vs_car":
    left_car = world.try_spawn_actor(car_bp, carla.Transform(origin + carla.Location(x=distance, y=-1.5, z=0.5)))
    right_car = world.try_spawn_actor(car_bp, carla.Transform(origin + carla.Location(x=distance, y=1.5, z=0.5)))
    actors.extend([left_car, right_car])

elif scenario_name == "pedestrian_vs_pedestrian":
    left_ped = world.try_spawn_actor(ped_bp[0], carla.Transform(origin + carla.Location(x=distance, y=-1.5, z=0.5)))
    right_ped = world.try_spawn_actor(ped_bp[1], carla.Transform(origin + carla.Location(x=distance, y=1.5, z=0.5)))
    actors.extend([left_ped, right_ped])

# Ensures all actors spawned successfully.
if not all(actors):
    raise RuntimeError("Failed to spawn all scenario actors.")

# === Decision Logic ===
decision_func = {
    "utilitarian": utilitarian_decision,
    "deontological": deontological_decision,
    "virtue": virtue_ethics_decision
}[ethical_mode]

# Runs the chosen ethical decision function.
decision = decision_func(scenario_input)
print(f"[INFO] Scenario: {scenario_name} | Mode: {ethical_mode} | Decision: {decision}")

# === Screenshot Setup ===
image_dir = "screenshots"
os.makedirs(image_dir, exist_ok=True)
filename = f"{scenario_name}_{ethical_mode}.png"
image_path = os.path.join(image_dir, filename)

start_time = time.time()

# Callback to save a screenshot after a delay.
def save_image(image):
    elapsed = time.time() - start_time
    if elapsed > 8:
        image.save_to_disk(image_path)
        print(f"[INFO] Screenshot saved at {elapsed:.2f} seconds: {image_path}")
        camera.stop()


# === Camera Setup ===
camera_bp = blueprint_library.find("sensor.camera.rgb")
vehicle_transform = vehicle.get_transform()
camera_location = vehicle_transform.location + carla.Location(x=-6, z=7)
camera_rotation = carla.Rotation(pitch=-35, yaw=0)
camera_transform = carla.Transform(camera_location, camera_rotation)

camera = world.spawn_actor(camera_bp, camera_transform)
spectator.set_transform(camera_transform)

camera.listen(save_image)  

# === Vehicle Control ===
control = carla.VehicleControl()

if decision == "swerve_left":
    control.throttle = 0.5
    control.steer = -0.5

elif decision == "swerve_right":
    control.throttle = 0.5
    control.steer = 0.5

elif decision == "brake":
    # Step 1: move forward a bit
    vehicle.apply_control(carla.VehicleControl(throttle=0.5, steer=0.0))
    time.sleep(4.5)

    # Step 2: apply brakes
    control.throttle = 0.0
    control.brake = 1.0
    control.steer = 0.0

elif decision == "slow down":
    # Phase 1: Move slowly
    vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=0.0))
    time.sleep(7) 

    # Phase 2: Stop
    vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0, steer=0.0))

else:  # "straight"
    control.throttle = 0.5
    control.steer = 0.0

vehicle.apply_control(control)
print(f"[DEBUG] Applied control — Throttle: {control.throttle}, Brake: {control.brake}, Steer: {control.steer}")

# Wait to complete scenario
time.sleep(20)

# === Cleanup ===
camera.destroy()
vehicle.destroy()
for actor in actors:
    if actor:
        actor.destroy()

# === Log Results ===
log_path = "results/dilemma_log.csv"
os.makedirs("results", exist_ok=True)
file_exists = os.path.isfile(log_path)

with open(log_path, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["scenario", "mode", "decision", "screenshot"])
    writer.writerow([scenario_name, ethical_mode, decision, filename])
