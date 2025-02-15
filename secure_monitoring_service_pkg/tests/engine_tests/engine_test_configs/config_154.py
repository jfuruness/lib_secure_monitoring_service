from typing import Dict, Type

from caida_collector_pkg import AS

from bgp_simulator_pkg import EngineTestConfig
from bgp_simulator_pkg import BGPSimpleAS
from bgp_simulator_pkg import ROVSimpleAS
from bgp_simulator_pkg import ASNs

from rovpp_pkg import ROVPPAnn
from rovpp_pkg import ROVPPV1LiteSimpleAS

from .. import graphs
from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario


class Config154(EngineTestConfig):
    """Contains config options to run a test"""

    name = "154"
    desc = "AutoImmune Attack with ROV++ V1 Lite"
    graph = graphs.Graph061()
    relay_asns = {12, 13}
    scenario = SubprefixAutoImmuneScenario(num_attackers=2,
                                           attacker_asns=graph.attacker_asn_set,
                                           victim_asns={ASNs.VICTIM.value},
                                           AdoptASCls=ROVPPV1LiteSimpleAS,
                                           BaseASCls=BGPSimpleAS,
                                           AnnCls=ROVPPAnn,
                                           relay_asns=relay_asns)

    non_default_as_cls_dict: Dict[int, Type[AS]] = {3: ROVPPV1LiteSimpleAS,
                                                    4: ROVPPV1LiteSimpleAS,
                                                    8: ROVPPV1LiteSimpleAS,
                                                    10: ROVPPV1LiteSimpleAS,
                                                    11: ROVPPV1LiteSimpleAS,
                                                    7: ROVSimpleAS}
    for asn in relay_asns:
        non_default_as_cls_dict[asn] = ROVPPV1LiteSimpleAS
    propagation_rounds = 1
