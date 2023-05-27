from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import json
import subprocess
from pathlib import Path
import argparse

from bgp_simulator_pkg import ROVSimpleAS

from rovpp_pkg import ROVPPAnn
from rovpp_pkg import ROVPPV1LiteSimpleAS

from secure_monitoring_service_pkg import V4Subgraph
from secure_monitoring_service_pkg import V4Simulation
from secure_monitoring_service_pkg import ROVSMS, ROVSMSK1, ROVSMSK2
from secure_monitoring_service_pkg import ROVSMSK3, ROVSMSK5, ROVSMSK6
from secure_monitoring_service_pkg import ROVSMSK10
from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import ArtemisSubprefixHijackScenario
from secure_monitoring_service_pkg import V4SuperprefixPrefixHijack
from secure_monitoring_service_pkg import CDN
from secure_monitoring_service_pkg import Peer

############################
# Constants
############################

BASE_PATH = Path("~/Desktop/graphs/").expanduser()

# Adopting settings
adoption_settings = {
    "adopters_for_1_attackers": [ROVSimpleAS, ROVPPV1LiteSimpleAS, ROVSMS, ROVSMSK1, ROVSMSK2],
    "adopters_for_2_attackers": [ROVSimpleAS, ROVPPV1LiteSimpleAS, ROVSMSK1, ROVSMSK2, ROVSMSK3],
    "adopters_for_5_attackers": [ROVSimpleAS, ROVPPV1LiteSimpleAS, ROVSMSK2, ROVSMSK5, ROVSMSK10]
}

# Scenario options
AUTOIMMUNE = "SubprefixAutoImmuneScenario"
SUBPREFIX_HIJACK = "V4SubprefixHijackScenario"
ARTEMIS_SUBPREFIX_HIJACK = "ArtemisSubprefixHijackScenario"
SUPERPREFIX_PLUS_PREFIX_HIJACK = "V4SuperprefixPrefixHijack"

ALL_PERCENTAGES = [0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.99]

POLICIES = {
    'rov': ROVSimpleAS,
    'v1lite': ROVPPV1LiteSimpleAS,
    'v4': ROVSMS,
    'v4k1': ROVSMSK1,
    'v4k2': ROVSMSK2,
    'v4k3': ROVSMSK3,
    'v4k5': ROVSMSK5,
    'v4k6': ROVSMSK6,
    'v4k10': ROVSMSK10
}


#############################
# Functions
#############################

def process_policies(args):
    policies = list()
    for policy in args.policy:
        policies.append(POLICIES[policy])
    return policies


def process_scenario_args(args):
    overlay_setting_raw = args.relay_asns[0]
    if overlay_setting_raw == None:
        overlay_setting = None
        assert args.attack_relays is False, "Cannot set attack_relays if relays is none"
    elif overlay_setting_raw in ['akamai', 'cloudflare', 'verisign', 'incapsula', 'neustar']:
        overlay_setting = CDN().__getattribute__(overlay_setting_raw)
    elif overlay_setting_raw in ['five', 'ten', 'twenty', 'hundred']:
        overlay_setting = Peer().__getattribute__(overlay_setting_raw)
    else:
        raise ValueError(f"Unknown Overlay setting given: {overlay_setting_raw}")

    settings = {
        "num_attackers": args.num_attackers,
        "min_rov_confidence": 0 if args.rov_adoption != 'none' else 1000,
        "adoption_subcategory_attrs": args.adoption_subcategory,
        "relay_asns": overlay_setting,
        "attack_relays": args.attack_relays,
        "assume_relays_are_reachable": args.assume_relays_are_reachable,
        "tunnel_customer_traffic": args.tunnel_customer_traffic,
    }
    # Set for AutoImmune attack indirect/direct
    if args.scenario == AUTOIMMUNE:
        settings["indirect"] = True if args.autoimmune_attack_type == 'indirect' else False

    return settings


def process_simulation_args(args):
    rov_setting_raw = args.rov_adoption  # none / real
    if rov_setting_raw == 'none':
        rov_setting = False
    elif rov_setting_raw == 'real':
        rov_setting = True
    else:
        raise ValueError(f"Unknown ROV setting given: {rov_setting_raw}")

    return {
        "percent_adoptions": args.percentages,
        "num_trials": args.num_trials,
        "subgraphs": [Cls() for Cls in V4Subgraph.v4_subclasses if Cls.name],
        "parse_cpus": args.cpus,
        "python_hash_seed": args.python_hash_seed,
        "caida_kwargs": {"csv_path": Path("./aux_files/rov_adoption_real.csv")} if rov_setting else {}
    }


def process_other_args(args):
    # If output filename given, use it
    if args.output:
        output_filename = args.output
    else:
        percentages_str = 'full' if args.percentages == ALL_PERCENTAGES else str(args.percentages).replace(' ', '')
        # Auto Generate Filename
        output_filename = f"{args.scenario}_scenario" + \
                          f"_{args.autoimmune_attack_type}_type" + \
                          f"_{args.rov_adoption}_rov" + \
                          f"_{args.python_hash_seed}_hash" + \
                          f"_{args.relay_asns[0]}_relay" + \
                          f"_{args.attack_relays}_attackRelay" + \
                          f"_{args.num_attackers}_attacker" + \
                          f"_{args.num_trials}_trials" + \
                          f"_{percentages_str}_percentages"

    settings = {
        "scenario": args.scenario,
        "output_filename": output_filename
    }
    return settings


#############################
# Arg Parser
#############################

def process_args(args):
    # Processes Scenario Args
    scenario_args = process_scenario_args(args)
    # Processes Simulation Args
    simulation_args = process_simulation_args(args)
    # Processes Other Args
    other_args = process_other_args(args)

    return args, scenario_args, simulation_args, other_args


def parse_args():
    parser = argparse.ArgumentParser(description='Secure Monitoring Service Simulation')
    # Simulation Args
    parser.add_argument('--percentages',
                        type=float,
                        nargs='*',
                        default=ALL_PERCENTAGES,
                        help='a list of floats')
    parser.add_argument('-o', '--output',
                        type=str,
                        nargs='?',
                        default=None,
                        help='Output filename')
    parser.add_argument('--num_trials',
                        type=int,
                        nargs='?',
                        default=10,
                        help='Number of trials to run')
    parser.add_argument('--cpus',
                        type=int,
                        nargs='?',
                        default=1,
                        help='Number of CPUs to use')
    parser.add_argument('--python_hash_seed',
                        type=int,
                        nargs='?',
                        default=0,
                        help='Deterministic setting seed. '
                             'Needs to be same as environment '
                             'variable PYTHONHASHSEED')
    parser.add_argument('--rov_adoption',
                        type=str,
                        nargs='?',
                        default='none',
                        help='ROV adoption setting. If given, '
                             'ROV ASes will be added to simulation.',
                        choices=['none', 'real'])

    # Scenario Args
    parser.add_argument('--num_attackers',
                        type=int,
                        nargs='?',
                        default=1,
                        help='Number of attackers')
    parser.add_argument('--adoption_subcategory',
                        type=str,
                        nargs='*',
                        default=("stub_or_mh_ases", "etc_ases", "input_clique_ases"),
                        help='The area in the graph for adoption. '
                             'Does not restrict additional ROV adoption')
    parser.add_argument('--relay_asns',
                        type=str,
                        nargs=1,
                        default=[None],
                        help='The relays that can be used',
                        choices=['none',
                                 'akamai',
                                 'cloudflare',
                                 'verisign',
                                 'incapsula',
                                 'neustar',
                                 'five',
                                 'ten',
                                 'twenty',
                                 'hundred'])
    parser.add_argument('--attack_relays',
                        type=bool,
                        nargs='?',
                        default=False,
                        help='Whether or not to attack relays.')
    parser.add_argument('--assume_relays_are_reachable',
                        type=bool,
                        nargs='?',
                        default=False,
                        help='This will enable/disable relays from sending '
                             'out a relay prefix. If set to True, then the '
                             'relay prefixes are not sent, and relays are'
                             ' assumed to be reachable to any adopting AS.')
    parser.add_argument('--tunnel_customer_traffic',
                        type=bool,
                        nargs='?',
                        default=False,
                        help='Whether or not to allow adopters to tunnel '
                             'reconnected traffic.')
    parser.add_argument('--policy',
                        type=str,
                        nargs='*',
                        default=None,
                        help='Adoption Policies to use',
                        choices=POLICIES.keys())
    parser.add_argument('--scenario',
                        type=str,
                        nargs='?',
                        default="V4SubprefixHijackScenario",
                        help='Attack Scenario',
                        choices=['V4SubprefixHijackScenario',
                                 'SubprefixAutoImmuneScenario',
                                 'ArtemisSubprefixHijackScenario'])
    parser.add_argument('--autoimmune_attack_type',
                        type=str,
                        nargs='?',
                        default='none',
                        help='This setting is only used for the '
                             'SubprefixAutoImmuneScenario, to indicate '
                             'if it is direct/indirect.',
                        choices=['none', 'direct', 'indirect'])
    return process_args(parser.parse_args())


#############################
# Functions
#############################

# Function for this obtained here and updated with more safe function call
# https://stackoverflow.com/a/41210204
def get_git_revision_hash():
    return subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout[:-1]


def get_git_short_revision_hash():
    return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout[:-1]


def process_experiment_settings(simulation_kwargs, scenario_kwargs, other_settings):
    settings = dict()
    settings.update(other_settings)
    del simulation_kwargs["subgraphs"]  # We don't need to output this
    simulation_kwargs["caida_kwargs"] = str(simulation_kwargs["caida_kwargs"])
    settings.update(simulation_kwargs)
    scenario_kwargs["relay_asns"] = str(scenario_kwargs["relay_asns"])
    settings.update(scenario_kwargs)
    settings["git_hash"] = get_git_revision_hash()
    settings["git_short_hash"] = get_git_short_revision_hash()
    return settings


#############################
# Main
#############################

def main():
    all_args, scenario_args, simulation_args, other_args = parse_args()

    # Get adoption classes
    if all_args.policy:
        adoption_classes = process_policies(all_args)
    else:
        adoption_classes = adoption_settings[f"adopters_for_{scenario_args['num_attackers']}_attackers"]

    sims = None
    if other_args["scenario"] == SUBPREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[V4SubprefixHijackScenario(AdoptASCls=Cls,
                                                              AnnCls=ROVPPAnn,
                                                              **scenario_args)
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / other_args["output_filename"],
                         **simulation_args),
        ]
    elif other_args["scenario"] == AUTOIMMUNE:
        sims = [
            V4Simulation(scenarios=[SubprefixAutoImmuneScenario(AdoptASCls=Cls,
                                                                AnnCls=ROVPPAnn,
                                                                **scenario_args)
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / other_args["output_filename"],
                         **simulation_args),
        ]
    elif other_args["scenario"] == ARTEMIS_SUBPREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[ArtemisSubprefixHijackScenario(AdoptASCls=Cls,
                                                                   AnnCls=ROVPPAnn,
                                                                   **scenario_args)
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / other_args["output_filename"],
                         **simulation_args),
        ]
    elif other_args["scenario"] == SUPERPREFIX_PLUS_PREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[V4SuperprefixPrefixHijack(AdoptASCls=Cls,
                                                              AnnCls=ROVPPAnn,
                                                              **scenario_args)
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / other_args["output_filename"],
                         **simulation_args),
        ]
    else:
        raise f"Unknown scenario specified: {other_args['scenario']}"

    # collect experiment settings
    experiment_settings_to_save = process_experiment_settings(simulation_args, scenario_args, other_args)

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
