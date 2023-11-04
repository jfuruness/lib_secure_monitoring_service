from typing import Dict, Type

from bgpy.caida_collector import AS

from bgpy import graphs
from bgpy import EngineTestConfig
from bgpy import BGPSimpleAS
from bgpy import ROVSimpleAS
from bgpy import ASNs

from rovpp import ROVPPAnn

from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import ROVSMSK1


class Config111(EngineTestConfig):
    """Contains config options to run a test"""

    name = "111"
    desc = "Subprefix Hijack with V4 Lite k=1."
    scenario = V4SubprefixHijackScenario(
        attacker_asns={ASNs.ATTACKER.value},
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVSMSK1,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
    )
    graph = graphs.Graph020()
    non_default_as_cls_dict: Dict[int, Type[AS]] = {
        32: ROVSMSK1,
        33: ROVSMSK1,
        89: ROVSMSK1,
        77: ROVSimpleAS,
    }
    propagation_rounds = 1
