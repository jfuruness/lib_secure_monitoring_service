from typing import Dict, Type

from bgpy.caida_collector import AS

from bgpy import graphs
from bgpy import EngineTestConfig
from bgpy import BGPSimpleAS
from bgpy.caida_collector import ASNs

from rovpp_pkg import ROVPPAnn
from rovpp_pkg import ROVPPV1LiteSimpleAS

from secure_monitoring_service_pkg import V4SubprefixHijackScenario


class Config103(EngineTestConfig):
    """Contains config options to run a test"""

    name = "103"
    desc = "Subprefix Hijack with V1 Lite."
    scenario = V4SubprefixHijackScenario(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVPPV1LiteSimpleAS,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
    )
    graph = graphs.Graph027()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {
        4: ROVPPV1LiteSimpleAS,
        10: ROVPPV1LiteSimpleAS,
        ASNs.VICTIM.value: ROVPPV1LiteSimpleAS,
    }
    propagation_rounds = 1
