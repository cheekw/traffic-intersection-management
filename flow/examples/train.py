from flow.core.params import VehicleParams
from flow.controllers import IDMController, ContinuousRouter
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.networks import Network
from flow.core.experiment import Experiment
import numpy as np

class FourWayIntersection(Network):
    def specify_nodes(self, net_params):
        # Define the nodes (junctions) of the network
        nodes = [{"id": "north", "x": 0,  "y": 50},  # North node
                 {"id": "south", "x": 0,  "y": -50},  # South node
                 {"id": "east",  "x": 50, "y": 0},    # East node
                 {"id": "west",  "x": -50, "y": 0},   # West node
                 {"id": "center", "x": 0, "y": 0}]    # Center node (junction)
        return nodes

    def specify_edges(self, net_params):
        # Define the edges (roads) of the network
        edges = [
            {"id": "northsouth", "from": "north", "to": "center", "numLanes": 3, "speed": 30, "length": 50},
            {"id": "southnorth", "from": "south", "to": "center", "numLanes": 3, "speed": 30, "length": 50},
            {"id": "eastwest", "from": "east", "to": "center", "numLanes": 3, "speed": 30, "length": 50},
            {"id": "westeast", "from": "west", "to": "center", "numLanes": 3, "speed": 30, "length": 50}
        ]
        return edges

    def specify_routes(self, net_params):
        # Define the routes vehicles can take
        routes = {
            "northsouth": ["northsouth", "eastwest", "southnorth", "westeast"],
            "southnorth": ["southnorth", "westeast", "northsouth", "eastwest"],
            "eastwest": ["eastwest", "southnorth", "westeast", "northsouth"],
            "westeast": ["westeast", "northsouth", "eastwest", "southnorth"]
        }
        return routes

# Vehicle parameters
vehicles = VehicleParams()
vehicles.add("human", acceleration_controller=(IDMController, {}), routing_controller=(ContinuousRouter, {}), num_vehicles=20)

# Simulation parameters
sim_params = SumoParams(sim_step=0.1, render=True)

# Environment parameters
additional_env_params = {"target_velocity": 50}
env_params = EnvParams(additional_params=additional_env_params)

# Network parameters
additional_net_params = {"radius": 50, "lanes": 3, "speed_limit": 30}
net_params = NetParams(additional_params=additional_net_params)

# Initial configuration
initial_config = InitialConfig(spacing="random", perturbation=1)

# Setup the experiment
network = FourWayIntersection(name="four_way_intersection", vehicles=vehicles, net_params=net_params, initial_config=initial_config)
env_name = "AccelEnv"
flow_params = dict(
    exp_tag="four_way_intersection_experiment",
    env_name=env_name,
    network=network,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
)

# Run the experiment
exp = Experiment(flow_params)
exp.run(1, 1500)