from typing import Dict, Type

from caida_collector_pkg import AS

from bgp_simulator_pkg import EngineTestConfig
from bgp_simulator_pkg import BGPSimpleAS
from bgp_simulator_pkg import ROVSimpleAS
from bgp_simulator_pkg import ASNs

from rovpp_pkg import ROVPPAnn

from .. import graphs
from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import ROVSMS
from secure_monitoring_service_pkg import CDN

class Config171(EngineTestConfig):
    """

    """

    name = "171"
    desc = "Subprefix Hijack with V4 k=0 \n" \
           "CDN Setting (Akamai) \n" \
           "Relays ARE attacked and Not assumed reachable"
    graph = graphs.Graph067()
    relay_asns = CDN.akamai
    scenario = V4SubprefixHijackScenario(num_attackers=1,
                                         attacker_asns=graph.attacker_asn_set,
                                         victim_asns={ASNs.VICTIM.value},
                                         AdoptASCls=ROVSMS,
                                         BaseASCls=BGPSimpleAS,
                                         AnnCls=ROVPPAnn,
                                         relay_asns=relay_asns,
                                         fraction_of_peer_ases_to_attack=1.0,
                                         attack_relays=True,
                                         assume_relays_are_reachable=False)

    non_default_as_cls_dict: Dict[int, Type[AS]] = {3: ROVSMS,
                                                    4: ROVSMS,
                                                    10: ROVSMS,
                                                    11: ROVSMS,
                                                    7: ROVSimpleAS}
    for asn in relay_asns:
        non_default_as_cls_dict[asn] = ROVSMS

    propagation_rounds = 1
