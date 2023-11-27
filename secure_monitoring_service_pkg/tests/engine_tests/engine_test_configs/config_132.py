from frozendict import frozendict

from bgpy.tests.engine_tests.graphs import graph_045
from bgpy.tests.engine_tests.utils import EngineTestConfig
from bgpy.simulation_engine import BGPSimpleAS
from bgpy.simulation_engine import ROVSimpleAS
from bgpy.enums import ASNs

from rovpp import ROVPPAnn

from secure_monitoring_service_pkg import V4SubprefixHijackScenario
from secure_monitoring_service_pkg import V4ScenarioConfig
from secure_monitoring_service_pkg import ROVSMSK2

config_132 = EngineTestConfig(
    name="132",
    desc="Subprefix Hijack with V4 Lite k=2",
    scenario_config=V4ScenarioConfig(
        ScenarioCls=V4SubprefixHijackScenario,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
        AdoptASCls=ROVSMSK2,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({
            3: ROVSMSK2,
            4: ROVSMSK2,
            8: ROVSMSK2,
            10: ROVSMSK2,
            12: ROVSMSK2,
            7: ROVSimpleAS,
        }),
    ),
    graph=graph_045,
)
