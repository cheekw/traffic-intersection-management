from flow.networks import Network

class FourWayIntersectionNetwork(Network):
    def specify_nodes(self, net_params):
        return [
            {"id": "north_end", "x": 0,  "y": 50},
            {"id": "south_end", "x": 0,  "y": -50},
            {"id": "east_end",  "x": 50, "y": 0},
            {"id": "west_end",  "x": -50, "y": 0},
            {"id": "center", "x": 0, "y": 0}
        ]

    def specify_edges(self, net_params):
        return [
            {"id": "north_to_center", "from": "north_end", "to": "center", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "south_to_center", "from": "south_end", "to": "center", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "east_to_center",  "from": "east_end",  "to": "center", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "west_to_center",  "from": "west_end",  "to": "center", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "center_to_south", "from": "center", "to": "south_end", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "center_to_north", "from": "center", "to": "north_end", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "center_to_east",  "from": "center", "to": "east_end", "length": 50, "numLanes": 1, "speed": 10},
            {"id": "center_to_west",  "from": "center", "to": "west_end", "length": 50, "numLanes": 1, "speed": 10}
        ]

    def specify_routes(self, net_params):
        # Define routes
        return {
            "north_to_center": [
                (["north_to_center", "center_to_south"], 0.34), # straight
                (["north_to_center", "center_to_east"], 0.33), # left
                (["north_to_center", "center_to_west"], 0.33), # right
            ],
            "south_to_center":
            [
                (["south_to_center", "center_to_north"], 0.34), # straight
                (["south_to_center", "center_to_west"], 0.33), # left
                (["south_to_center", "center_to_east"], 0.33), # right
            ],
            "east_to_center":
            [
                (["east_to_center", "center_to_west"], 0.34), # straight
                (["east_to_center", "center_to_south"], 0.33), # left
                (["east_to_center", "center_to_north"], 0.33), # right
            ],
            "west_to_center":
            [
                (["west_to_center", "center_to_east"], 0.34), # straight
                (["west_to_center", "center_to_north"], 0.33), # left
                (["west_to_center", "center_to_south"], 0.33), # right
            ],
        }

    def specify_edge_starts(self):
        return [
            ("north_to_center", 0),
            ("south_to_center", 50),
            ("east_to_center", 100),
            ("west_to_center", 150),
            ("center_to_south", 200),
            ("center_to_north", 250),
            ("center_to_east",  300),
            ("center_to_west",  350)
        ]


# Define Params

from flow.core.params import NetParams, VehicleParams, TrafficLightParams, SumoParams, EnvParams
from flow.envs import Env
from flow.core.experiment import Experiment

# add vehicle inflow
from flow.core.params import InFlows
inflow = InFlows()
inflow.add(veh_type="human",
           edge="north_to_center",
           probability=0.1)
inflow.add(veh_type="human",
           edge="west_to_center",
           probability=0.1)
inflow.add(veh_type="human",
           edge="south_to_center",
           probability=0.1)
inflow.add(veh_type="human",
           edge="east_to_center",
           probability=0.1)

# Setup network and simulation parameters
net_params = NetParams(
    inflows=inflow,
    # additional_params=ADDITIONAL_NET_PARAMS
)
vehicles = VehicleParams()  # Define your vehicles here
sumo_params = SumoParams(render=True)  # Enable GUI rendering

from flow.controllers import IDMController, GridRouter

vehicles.add(veh_id="human",
             acceleration_controller=(IDMController, {}),
             routing_controller=(GridRouter, {}),
             num_vehicles=1)

from flow.core.params import InitialConfig
initial_config = InitialConfig(spacing="uniform")

tl_logic = TrafficLightParams(baseline=False)
phases = [
    {"duration": "30", "state": "rrrGGgrrrGGg"},  # North-South movement
    {"duration": "5", "state": "rrryyyrrryyy"},   # Yellow phase
    {"duration": "30", "state": "GGgrrrGGgrrr"},  # East-West movement
    {"duration": "5", "state": "yyyrrryyyrrr"}    # Yellow phase
]
# tl_logic.add(
#     "center", 
#     tls_type="static", 
#     programID="1", 
#     offset="0", 
#     phases=phases
# )
tl_logic.add(
    "center", 
    tls_type="actuated", 
    programID="1", 
    phases=phases,
    maxGap=5.0, 
    detectorGap=0.9, 
    offset="0", 
    showDetectors=True
)

from flow.envs.ring.accel import AccelEnv, ADDITIONAL_ENV_PARAMS
env_params = EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)

from flow.core.experiment import Experiment

flow_params = dict(
    exp_tag='test_network',
    env_name=AccelEnv,
    network=FourWayIntersectionNetwork,
    simulator='traci',
    sim=sumo_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
    tls=tl_logic
)

# number of time steps
flow_params['env'].horizon = 3000
exp = Experiment(flow_params)

# run the sumo simulation
_ = exp.run(1)