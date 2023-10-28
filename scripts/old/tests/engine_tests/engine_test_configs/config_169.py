from typing import Dict, Type

from bgpy.caida_collector import AS

from bgpy import EngineTestConfig
from bgpy import BGPSimpleAS
from bgpy import ROVSimpleAS
from bgpy.caida_collector import ASNs

from rovpp_pkg import ROVPPAnn

from .. import graphs
from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import ROVSMSK1


class Config169(EngineTestConfig):
    """Contains config options to run a test
    This is a Indirect AutoImmune attack."""

    name = "169"
    desc = "Indirect AutoImmune Attack with ROV++ V4 k=1\nThe origin has two providers"
    graph = graphs.Graph066()
    scenario = SubprefixAutoImmuneScenario(
        num_attackers=2,
        attacker_asns=graph.attacker_asn_set,
        victim_asns={ASNs.VICTIM.value},
        AdoptASCls=ROVSMSK1,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
        assume_relays_are_reachable=True,
        indirect=True,
    )

    non_default_as_cls_dict: Dict[int, Type[AS]] = {
        3: ROVSMSK1,
        8: ROVSMSK1,
        11: ROVSMSK1,
        7: ROVSimpleAS,
    }

    propagation_rounds = 1
