from typing import Dict, Type

from caida_collector_pkg import AS

from bgp_simulator_pkg import graphs
from bgp_simulator_pkg import EngineTestConfig
from bgp_simulator_pkg import BGPSimpleAS
from bgp_simulator_pkg import ASNs

from rovpp_pkg import ROVPPAnn

from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import ROVSMSK1


class Config105(EngineTestConfig):
    """Contains config options to run a test"""

    name = "105"
    desc = "Subprefix Hijack with V4 Lite k=1."
    scenario = V4SubprefixHijackScenario(attacker_asns={ASNs.ATTACKER.value},
                                         victim_asns={ASNs.VICTIM.value},
                                         AdoptASCls=ROVSMSK1,
                                         BaseASCls=BGPSimpleAS,
                                         AnnCls=ROVPPAnn)
    graph = graphs.Graph027()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {4: ROVSMSK1,
                                                    10: ROVSMSK1,
                                                    ASNs.VICTIM.value: ROVSMSK1}
    propagation_rounds = 1
