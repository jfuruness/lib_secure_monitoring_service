from frozendict import frozendict

from bgpy.tests.engine_tests.graphs import graph_060
from bgpy.tests.engine_tests.utils import EngineTestConfig
from bgpy.simulation_engine import BGPSimpleAS, ROVSimpleAS
from bgpy.enums import ASNs

from rovpp import ROVPPAnn

from secure_monitoring_service_pkg import SubprefixAutoImmuneScenario
from secure_monitoring_service_pkg import V4ScenarioConfig
from secure_monitoring_service_pkg import ROVSMSK2

config_151 = EngineTestConfig(
    name="151",
    desc="AutoImmune Attack with V4 Lite K=2",
    scenario_config=V4ScenarioConfig(
        ScenarioCls=SubprefixAutoImmuneScenario,
        num_attackers=2,
        AdoptASCls=ROVSMSK2,
        BaseASCls=BGPSimpleAS,
        AnnCls=ROVPPAnn,
        override_attacker_asns=frozenset(graph_060.attacker_asn_set),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict({
            3: ROVSMSK2,
            4: ROVSMSK2,
            8: ROVSMSK2,
            10: ROVSMSK2,
            11: ROVSMSK2,
            12: ROVSMSK2,
            7: ROVSimpleAS,
        }),
    ),
    graph=graph_060,
)
