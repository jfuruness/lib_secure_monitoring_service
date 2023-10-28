from typing import Dict, Type

from bgpy.caida_collector import AS

from bgpy import graphs
from bgpy import EngineTestConfig
from bgpy import BGPSimpleAS
from bgpy import ROVSimpleAS
from bgpy.caida_collector import ASNs

from rovpp import ROVPPAnn

from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import ROVSMSK1


class Config133(EngineTestConfig):
    """Contains config options to run a test"""

    name = "133"
    desc = "AutoImmune Attack with V4 Lite k=1"
    scenario = SubprefixAutoImmuneScenario(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVSMSK1,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
    )
    graph = graphs.Graph046()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {
        32: ROVSMSK1,
        33: ROVSMSK1,
        77: ROVSimpleAS,
    }
    propagation_rounds = 1
