#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 16, 2023

@author: Reynaldo Morillo
"""

from v4_graph_generator import Line, generate_plot, linemap_2
import data_manager as dm


####################################
# Main
####################################

# Example file name
# V4SubprefixHijackScenario_scenario_none_type_real_rov_0_hash_incapsula_relay_False_attackRelay_5_attacker_500_trials_full_percentages

#-----------------------------------
# Constants
#-----------------------------------

line_name_map = {
        "rov": 'ROV adopting',
        "rovppv1lite": "ROV++ V1 Lite adopting",
        "v4k2": "Pheme k=2 adopting",
        "v4k5": "Pheme k=5 adopting",
        "v4k10": "Pheme k=10 adopting",
    }

#-----------------------------------
# Args
#-----------------------------------

scenario = 'SubprefixAutoImmuneScenario'
scenario_type ='indirect'
rov_settings = ['real', 'none']
# rov_setting = 'none'
hash_seed = 0
# relay
attack_relay = False
num_attackers = 5
num_trials = 500

metric = dm.victim_success
relays = ['verisign', 'five']
# relays = ['cloudflare', 'verisign', 'five', 'twenty']
k_values = [2, 5, 10]
reference_policies = ['rov', 'rovppv1lite']
v4_policies = [ f'v4k{k}' for k in k_values ]


for rov_setting in rov_settings:
    for metric in [dm.attacker_success, dm.victim_success, dm.disconnections]:
        
        #-----------------------------------
        # Plot Generation
        #-----------------------------------
        
        subgraph = dm.metric_subgraph[metric]
        
        
        # Load paths
        paths = list()
        
        for relay in relays:
            paths.append(
                    dm.json_file(scenario, scenario_type, rov_setting, hash_seed, relay, attack_relay, num_attackers, num_trials)
                )
        
        # Load Results
        rov_results = dm.get_results([paths[0]], subgraph, [dm.policy_name_map['rov']])
        rovpp_results = dm.get_results([paths[0]], subgraph, [dm.policy_name_map['rovppv1lite']])
        v4_results = dm.get_results(paths, subgraph, v4_policies)
        results = rov_results + rovpp_results
        
        for policy in v4_policies:
            results = results + (dm.get_results(paths, subgraph, [dm.policy_name_map[policy]]))
    
        
        # Generate Lines
        lines_map = dict()
        relay_filename = ""
        i = 0
        
        # Add the reference policies first 
        for policy in reference_policies:
            lines_map[i] = line_name_map[policy]
            i += 1
            
        # Add the Pheme policies (with the different settings of k)
        for k in k_values:
            for relay in relays:        
                if relay in dm.cdns:
                    lines_map[i] = f"Pheme {relay.capitalize()} - k={k} adopting"
                    relay_filename = "cdns"
                elif relay in dm.peers:
                    lines_map[i] = f"Pheme Peer {dm.peer_map[relay]} - k={k} adopting"
                    relay_filename = "peers"
                i += 1
        
        lines = []
        for i, result in enumerate(results):
            lines.append(Line(lines_map[i], False, result.adopting[subgraph]))
        
            
        # Plot Lines
        generate_plot(lines,
                      ylim=100,
                      outcome_text=dm.metric_outcome[metric],
                      size_inches=(5, 4),
                      legend_kwargs={'loc':'best', 'prop':{'size': 11}},
                      linemap=linemap_2,
                      fname=f"./paper_plots/autoimmune_{scenario_type}/rov_{rov_setting}/autoimmune_{scenario_type}_with_relay_{dm.metric_filename_prefix[metric]}.pdf")
