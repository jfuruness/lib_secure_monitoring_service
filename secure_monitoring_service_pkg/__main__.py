from datetime import datetime
import time
import subprocess
from pathlib import Path
import argparse

from bgp_simulator_pkg import ROVSimpleAS
from bgp_simulator_pkg import SpecialPercentAdoptions

from rovpp_pkg import ROVPPAnn
from rovpp_pkg import ROVPPV1LiteSimpleAS

from secure_monitoring_service_pkg import V4Subgraph
from secure_monitoring_service_pkg import V4Simulation
from secure_monitoring_service_pkg import Artemis
from secure_monitoring_service_pkg import ROVPPO, ROVO
from secure_monitoring_service_pkg import ROVSMS, ROVSMSK1, ROVSMSK2
from secure_monitoring_service_pkg import ROVSMSK3, ROVSMSK5, ROVSMSK6
from secure_monitoring_service_pkg import ROVSMSK10
from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import ArtemisSubprefixHijackScenario
from secure_monitoring_service_pkg import V4SuperprefixPrefixHijack
from secure_monitoring_service_pkg import V4PrefixHijackScenario
from secure_monitoring_service_pkg import RelayPrefixHijack
from secure_monitoring_service_pkg import V4Scenario
from secure_monitoring_service_pkg import V4OriginHijack
from secure_monitoring_service_pkg import CDN
from secure_monitoring_service_pkg import Peer
from secure_monitoring_service_pkg import metadata_collector

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
PREFIX_HIJACK = "V4PrefixHijackScenario"
ARTEMIS_SUBPREFIX_HIJACK = "ArtemisSubprefixHijackScenario"
SUPERPREFIX_PLUS_PREFIX_HIJACK = "V4SuperprefixPrefixHijack"
RELAY_PREFIX_HIJACK = "RelayPrefixHijack"
ORIGIN_HIJACK = "V4OriginHijack"

ATTACK_RELAY_PREFIX_HIJACK = 'prefix_hijack'
ATTACK_RELAY_ORIGIN_HIJACK = 'origin_hijack'


ALL_PERCENTAGES = [SpecialPercentAdoptions.ONLY_ONE, 0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.99]

STANDARD_POLICIES = {
    'rov': ROVSimpleAS,
    'v1lite': ROVPPV1LiteSimpleAS
}

POLICIES = {
    'artemis': Artemis,
    'rovppo': ROVPPO,
    'rovo': ROVO,
    'v4': ROVSMS,
    'v4k1': ROVSMSK1,
    'v4k2': ROVSMSK2,
    'v4k3': ROVSMSK3,
    'v4k5': ROVSMSK5,
    'v4k6': ROVSMSK6,
    'v4k10': ROVSMSK10
}

# Add the STANDARD_POLICIES to list of POLICIES
POLICIES.update(STANDARD_POLICIES)


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
    elif overlay_setting_raw in ['akamai', 'cloudflare', 'verisign', 'incapsula', 'neustar', 'conglomerate']:
        overlay_setting = CDN().__getattribute__(overlay_setting_raw)
    elif overlay_setting_raw in ['five', 'ten', 'twenty', 'forty', 'fifty', 'hundred']:
        overlay_setting = Peer().__getattribute__(overlay_setting_raw)
    else:
        raise ValueError(f"Unknown Overlay setting given: {overlay_setting_raw}")

    settings = {
        "num_attackers": args.num_attackers,
        "min_rov_confidence": args.rov_adoption_min_conf if args.rov_adoption != 'none' else 1000,
        "adoption_subcategory_attrs": args.adoption_subcategory,
        "relay_asns": overlay_setting,
        "attack_relays": args.attack_relays,
        "fraction_of_peer_ases_to_attack": args.fraction_of_peer_ases_to_attack,
        "assume_relays_are_reachable": args.assume_relays_are_reachable,
        "tunnel_customers_traffic": args.tunnel_customers_traffic,
        "probe_data_plane": args.probe_data_plane,
        "special_static_as_class": None if not args.replace_rov_ases_with else POLICIES.get(
            args.replace_rov_ases_with[0]),
        "probabilistic_rov_adoption": args.probabilistic_rov_adoption,
        "allow_rov_turnover": args.allow_rov_turnover,
        "attack_relays_type": args.attack_relays_type[0]
    }
    # Special Settings for some scenarios
    if args.scenario == AUTOIMMUNE:
        settings["indirect"] = True if args.autoimmune_attack_type == 'indirect' else False
    if args.scenario == ARTEMIS_SUBPREFIX_HIJACK:
        settings["fightback_origin_only"] = args.fightback_origin_only
        settings["fightback_cdn_only"] = args.fightback_cdn_only

    return settings


def process_simulation_args(args):
    rov_setting_raw = args.rov_adoption  # none / real
    if rov_setting_raw == 'none':
        if args.replace_rov_ases_with:
            raise ValueError(
                f"If `replace_rov_ases_with` (e.g. {args.replace_rov_ases_with}) is set, then `rov_adoption` setting must be set (i.e. NOT None)")
        rov_setting = False
    elif rov_setting_raw == 'real':
        rov_setting = True
    else:
        raise ValueError(f"Unknown ROV setting given: {rov_setting_raw}")

    aux_path = Path(__file__).parent / "aux_files"
    percentages = args.percentages
    if percentages == [-1.0,]:
        percentages = [SpecialPercentAdoptions.ONLY_ONE,]
    elif percentages == [1000.0,]:
        percentages = [SpecialPercentAdoptions.ALL_BUT_ONE,]
    return {
        "percent_adoptions": percentages,
        "num_trials": args.num_trials,
        "subgraphs": [Cls() for Cls in V4Subgraph.v4_subclasses if Cls.name],
        "parse_cpus": args.cpus,
        "python_hash_seed": args.python_hash_seed,
        "caida_topology_date": args.caida_topology_date,
        "caida_kwargs": {"csv_path": aux_path / "rov_adoption_real.csv"} if rov_setting else {}
    }


def only_using_standard_policies(policies):
    standard_policies_list = STANDARD_POLICIES.keys()
    num_standard_policies = len(standard_policies_list)
    if len(policies) != num_standard_policies:
        return False
    for policy in policies:
        if policy not in standard_policies_list:
            return False
    return True


def other_policies(policies):
    if len(policies) > 1:
        return "others"
    else:
        return policies[0]


def process_other_args(args):
    # If output filename given, use it
    if args.output:
        output_filename = args.output
    else:
        # TODO: Change this to put the single policy that's being used (if it's a single policy)
        policies_used_str = "standard" if only_using_standard_policies(args.policy) else other_policies(args.policy)
        percentages_str = 'full' if args.percentages == ALL_PERCENTAGES else str(args.percentages).replace(' ', '')
        min_rov_conf = int(args.rov_adoption_min_conf * 100)
        if args.replace_rov_ases_with:
            mixed_adoption_setting = args.replace_rov_ases_with[0]
        else:
            mixed_adoption_setting = args.rov_adoption

        # Scenario type
        if args.scenario == ARTEMIS_SUBPREFIX_HIJACK and args.fightback_origin_only:
            scenario_type = 'originOnly'
        elif args.scenario == ARTEMIS_SUBPREFIX_HIJACK and args.fightback_cdn_only:
            scenario_type = 'cdnOnly'
        elif args.scenario == AUTOIMMUNE:
            scenario_type = args.autoimmune_attack_type
        elif args.attack_relays_type[0] == 'origin_hijack':
            scenario_type = 'originHijack'
        else:
            scenario_type = 'none'

        # Auto Generate Filename
        output_filename = f"{args.scenario}_scenario" + \
                          f"_{scenario_type}_type" + \
                          f"_{policies_used_str}_policies" + \
                          f"_{mixed_adoption_setting}_rov" + \
                          f"_{min_rov_conf}_conf" + \
                          f"_{args.allow_rov_turnover}_turnover" + \
                          f"_{args.python_hash_seed}_hash" + \
                          f"_{args.probe_data_plane}_probe" + \
                          f"_{args.tunnel_customers_traffic}_tunnel" + \
                          f"_{args.relay_asns[0]}_relay" + \
                          f"_{args.attack_relays}_attackRelay" + \
                          f"_{args.num_attackers}_attacker" + \
                          f"_{args.num_trials}_trials" + \
                          f"_{percentages_str}_percentages"

    settings = {
        "scenario": args.scenario,
        "output_filename": output_filename,
        "collect_avoid_list_metadata": args.collect_avoid_list_metadata,
        "collect_as_metadata": args.collect_as_metadata
    }
    # Update Metadata collector
    # Save output filename to metadata_collector
    metadata_collector.output_filename = output_filename
    metadata_collector.base_path = str(BASE_PATH)
    if args.collect_avoid_list_metadata:
        metadata_collector.collect_avoid_list_metadata = args.collect_avoid_list_metadata
        metadata_collector.write_avoid_list_csv_header()
    if args.collect_as_metadata:
        metadata_collector.collect_as_metadata = args.collect_as_metadata
        metadata_collector.write_as_csv_header()
    if args.collect_agg_as_metadata:
        metadata_collector.collect_agg_as_metadata = args.collect_agg_as_metadata
        metadata_collector.write_agg_as_csv_header()
    if args.collect_artemis_metadata:
        metadata_collector.collect_artemis_metadata = args.collect_artemis_metadata
        metadata_collector.write_artemis_csv_header()
    return settings


#############################
# Arg Parser
#############################

def process_args(args):
    # NOTE: Processing Other Args needs to be first to allow metadata_collector to know output filename
    # Processes Other Args
    other_args = process_other_args(args)
    # Processes Scenario Args
    scenario_args = process_scenario_args(args)
    # Processes Simulation Args
    simulation_args = process_simulation_args(args)

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
    parser.add_argument('--rov_adoption_min_conf',
                        type=float,
                        nargs='?',
                        default=0.0,
                        help='ROV minimum confidence of adopter')
    parser.add_argument('--caida_topology_date',
                        type=str,
                        nargs='?',
                        default='2023.05.07',
                        help='Date for caida topology data formatted as "yyyy.mm.dd"')

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
                                 'conglomerate',
                                 'five',
                                 'ten',
                                 'twenty',
                                 'forty',
                                 'fifty',
                                 'hundred'])
    parser.add_argument('--replace_rov_ases_with',
                        type=str,
                        nargs=1,
                        default=None,
                        help='Adopting ASes that can be set as special adopting '
                             'ASes when the ROV adopting is set to real',
                        choices=POLICIES.keys())
    parser.add_argument('--attack_relays',
                        action="store_true",
                        default=False,
                        help='Whether or not to attack relays.')
    parser.add_argument('--attack_relays_type',
                        type=str,
                        nargs=1,
                        default=ATTACK_RELAY_PREFIX_HIJACK,
                        help='The relays that can be used',
                        choices=['prefix_hijack',
                                 'origin_hijack'])
    parser.add_argument('--fraction_of_peer_ases_to_attack',
                        type=float,
                        nargs='?',
                        default=1.0,
                        help='A float representing the fraction peers to be '
                             'attacked when the "attack_relays" flag is set')
    parser.add_argument('--assume_relays_are_reachable',
                        action="store_true",
                        default=False,
                        help='This will enable/disable relays from sending '
                             'out a relay prefix. If set to True, then the '
                             'relay prefixes are not sent, and relays are'
                             ' assumed to be reachable to any adopting AS.')
    parser.add_argument('--tunnel_customers_traffic',
                        action="store_true",
                        default=False,
                        help='Whether or not to allow adopters to tunnel '
                             'reconnected traffic.')
    parser.add_argument('--probe_data_plane',
                        action="store_true",
                        default=False,
                        help='This enables the overlays to check the dataplane '
                             'result to determine its availability.')
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
                        choices=[SUBPREFIX_HIJACK,
                                 PREFIX_HIJACK,
                                 AUTOIMMUNE,
                                 ARTEMIS_SUBPREFIX_HIJACK,
                                 SUPERPREFIX_PLUS_PREFIX_HIJACK,
                                 RELAY_PREFIX_HIJACK,
                                 ORIGIN_HIJACK])
    parser.add_argument('--autoimmune_attack_type',
                        type=str,
                        nargs='?',
                        default='none',
                        help='This setting is only used for the '
                             'SubprefixAutoImmuneScenario, to indicate '
                             'if it is direct/indirect.',
                        choices=['none', 'direct', 'indirect'])
    parser.add_argument('--probabilistic_rov_adoption',
                        action="store_true",
                        default=False,
                        help='If ROV adoption is not set to "none", then adopt ROV according to confidence score.')
    parser.add_argument('--allow_rov_turnover',
                        action="store_true",
                        default=False,
                        help='If ROV adoption is not set to "none", then allow preset ' 
                             'ROV ases to be converted to other adopting policy selected for simulation.')
    parser.add_argument('--fightback_origin_only',
                        action="store_true",
                        default=False,
                        help='Whether or not the origin fights back alone in the Artemis scenario settings.')
    parser.add_argument('--fightback_cdn_only',
                        action="store_true",
                        default=False,
                        help='Whether or not the CDN fights back without origin in the Artemis scenario settings.')

    # Other Args
    parser.add_argument('--collect_avoid_list_metadata',
                        action="store_true",
                        default=False,
                        help='Whether or not to collect avoid list metadata.')
    parser.add_argument('--collect_as_metadata',
                        action="store_true",
                        default=False,
                        help='Whether or not to collect individual AS metadata. '
                             'WARNING: Should only be done for a small number of trials, '
                             'as the resulting file grows large very quickly.')
    parser.add_argument('--collect_agg_as_metadata',
                        action="store_true",
                        default=False,
                        help='Whether or not to collect aggregated AS metadata.')
    parser.add_argument('--collect_artemis_metadata',
                        action="store_true",
                        default=False,
                        help='Whether or not to collect Artemis metadata.')
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
    scenario_kwargs["special_static_as_class"] = str(scenario_kwargs["special_static_as_class"])
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
    elif other_args["scenario"] == PREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[V4PrefixHijackScenario(AdoptASCls=Cls,
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
    elif other_args["scenario"] == RELAY_PREFIX_HIJACK:
        sims = [
            V4Simulation(scenarios=[RelayPrefixHijack(AdoptASCls=Cls,
                                                      AnnCls=ROVPPAnn,
                                                      **scenario_args)
                                    for Cls in adoption_classes
                                    ],
                         output_path=BASE_PATH / other_args["output_filename"],
                         **simulation_args),
        ]
    elif other_args["scenario"] == ORIGIN_HIJACK:
        sims = [
            V4Simulation(scenarios=[V4OriginHijack(AdoptASCls=Cls,
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
    other_args['experiment_start_time'] = datetime.now().isoformat()
    other_args['policies'] = [x.__name__ for x in adoption_classes]
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
        metadata_collector.clean_up_lock_files()
        end_time = time.perf_counter()
        print("End Time", time.ctime())
        print("Elasped Time: ", end_time - start_time)
