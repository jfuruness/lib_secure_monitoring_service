from typing import Dict, Type

from caida_collector_pkg import AS

from bgp_simulator_pkg import graphs
from bgp_simulator_pkg import EngineTestConfig
from bgp_simulator_pkg import BGPSimpleAS
from bgp_simulator_pkg import ROVSimpleAS
from bgp_simulator_pkg import ASNs

from rovpp_pkg import ROVPPAnn

from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import ROVSMSK1


class Config143(EngineTestConfig):
    """Contains config options to run a test"""

    name = "143"
    desc = "AutoImmune Attack with V4 Lite k=1"
    scenario = SubprefixAutoImmuneScenario(num_attackers=1,
                                           attacker_asns={ASNs.ATTACKER.value},
                                           victim_asns={ASNs.VICTIM.value},
                                           AdoptASCls=ROVSMSK1,
                                           BaseASCls=BGPSimpleAS,
                                           AnnCls=ROVPPAnn)
    graph = graphs.Graph043()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {3: ROVSMSK1,
                                                    4: ROVSMSK1,
                                                    8: ROVSMSK1,
                                                    10: ROVSMSK1,
                                                    7: ROVSimpleAS}
    propagation_rounds = 1
