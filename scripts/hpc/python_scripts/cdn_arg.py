from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import json
import sys

from rovpp_pkg import ROVPPAnn
from rovpp_pkg import ROVPPV1LiteSimpleAS

from secure_monitoring_service_pkg import V4Subgraph
from secure_monitoring_service_pkg import V4Simulation
from secure_monitoring_service_pkg import ROVSMS, ROVSMSK1, ROVSMSK2
from secure_monitoring_service_pkg import ROVSMSK3, ROVSMSK5, ROVSMSK6
from secure_monitoring_service_pkg import ROVSMSK10
from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import CDN
from secure_monitoring_service_pkg import Peer

############################
# Constants
############################

BASE_PATH = Path("~/Desktop/graphs/").expanduser()

# Adopting settings
adoption_settings = {
    "adopters_for_1_attackers": [ROVPPV1LiteSimpleAS, ROVSMS, ROVSMSK1, ROVSMSK2],
    "adopters_for_2_attackers": [ROVPPV1LiteSimpleAS, ROVSMSK1, ROVSMSK2, ROVSMSK3],
    "adopters_for_5_attackers": [ROVPPV1LiteSimpleAS, ROVSMSK1, ROVSMSK5, ROVSMSK10]
}

# Scenario options
AUTOIMMUNE = "SubprefixAutoImmuneScenario"
SUBPREFIX_HIJACK = "V4SubprefixHijackScenario"


#############################
# Functions
#############################

def process_experiment_settings(simulation_kwargs, scenario_kwargs, other_settings):
    settings = dict()
    settings.update(other_settings)
    del simulation_kwargs["subgraphs"]  # We don't need to output this
    simulation_kwargs["caida_kwargs"] = str(simulation_kwargs["caida_kwargs"])
    settings.update(simulation_kwargs)
    del scenario_kwargs["relay_asns"]  # This can be very large for peer setting
    settings.update(scenario_kwargs)
    return settings


#############################
# Simulation Arguments
#############################

#----------------------------
# Command Line argument
cdn_arg = sys.argv[1]
#----------------------------


def other_settings():
    settings = {
        "scenario": AUTOIMMUNE,
        "output_filename": f"hpc_autoimmune_indirect_5_attackers_{cdn_arg}_500_trials"
    }
    return settings


def scenario_kwargs():
    settings = {
        "num_attackers": 5,
        "min_rov_confidence": 0,
        "adoption_subcategory_attrs": ("stub_or_mh_ases", "etc_ases", "input_clique_ases"),
        "relay_asns": getattr(CDN, sys.argv[1]),
        "assume_relays_are_reachable": False,
        "tunnel_customer_traffic": False,
    }
    # Set for AutoImmune attack indirect/direct
    if other_settings()["scenario"] == AUTOIMMUNE:
        settings["indirect"] = True

    # Validate Settings
    if not (settings["relay_asns"] == Peer.twenty or settings["relay_asns"] == Peer.hundred
            or settings["relay_asns"] == Peer.five or settings["relay_asns"] == Peer.ten):
        assert not settings["assume_relays_are_reachable"], "assume_relays_are_reachable " \
                                                            "should only be set True for " \
                                                            "Peer relay setting"
    return settings


def simulation_kwargs():
    return {
        "percent_adoptions": [0.01, 0.1, 0.2, 0.4, 0.6, 0.8, 0.99],
        "num_trials": 500,
        "subgraphs": [Cls() for Cls in V4Subgraph.v4_subclasses if Cls.name],
        "parse_cpus": 100,
        "python_hash_seed": 0,
        "caida_kwargs": {"csv_path": Path("../../aux_files/rov_adoption_real.csv")}
    }


#############################
# Main
#############################

def main():
    # Get adoption classes
    adoption_classes = adoption_settings[f"adopters_for_{scenario_kwargs()['num_attackers']}_attackers"]

    # Load Simulation settings
    settings = other_settings()

    sims = None
    if settings["scenario"] == SUBPREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[V4SubprefixHijackScenario(AdoptASCls=Cls,
                                                              AnnCls=ROVPPAnn,
                                                              **scenario_kwargs())
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / settings["output_filename"],
                         **simulation_kwargs()),
        ]
    elif settings["scenario"] == AUTOIMMUNE:
        sims = [
            V4Simulation(scenarios=[SubprefixAutoImmuneScenario(AdoptASCls=Cls,
                                                                AnnCls=ROVPPAnn,
                                                                **scenario_kwargs())
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / settings["output_filename"],
                         **simulation_kwargs()),
        ]
    else:
        raise f"Unknown scenario specified: {settings['scenario']}"

    # collect experiment settings
    experiment_settings_to_save = process_experiment_settings(simulation_kwargs(), scenario_kwargs(), other_settings())

    # Run Simulations
    for sim in sims:
        start = datetime.now()
        sim.run(experiment_settings_to_save)
        print(f"{sim.output_path} {(datetime.now() - start).total_seconds()}")


if __name__ == "__main__":
    print("Start Time", time.ctime())
    start_time = time.perf_counter()
    try:
        main()
    finally:
        end_time = time.perf_counter()
        print("End Time", time.ctime())
        print("Elasped Time: ", end_time - start_time)
