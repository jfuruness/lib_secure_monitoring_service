import random
import ipaddress

from rovpp_pkg import ROVPPV1LiteSimpleAS

from secure_monitoring_service_pkg.simulation_engine.trusted_server import TrustedServer
from secure_monitoring_service_pkg.simulation_framework.sim_logger import sim_logger as logger
from secure_monitoring_service_pkg.simulation_engine.report import Report


class ROVSMS(ROVPPV1LiteSimpleAS):
    name = "ROV V4 Lite"

    _max_num_dishonest_nodes = 0
    trusted_server = TrustedServer(0)

    def __init__(self, *args, reset_trusted_server=True, **kwargs):
        """When everything is being reset, reset the trust server also"""
        # logger.debug("Created ROVSMS {0}".format(kwargs['asn']))
        # At the end of the graphing, everything should be reset
        if reset_trusted_server:
            self.trusted_server.__init__()
        super(ROVSMS, self).__init__(*args, **kwargs)
        # The following variable indicates if the AS used a relay
        # and it's updated in the V4Subgraph method _recalculate_outcomes_with_relays
        self.used_relay = False

    def receive_ann(self, ann, *args, **kwargs):
        """Recieves ann and reports it"""
        logger.debug(f"ASN {self.asn} inside receive_ann")
        if ann.invalid_by_roa:
            logger.debug(f"ASN {self.asn} sending report about {ann.prefix}")
            if self._max_num_dishonest_nodes > 0:
                if self.asn not in ann.as_path:
                    adjusted_as_path = (self.asn,) + ann.as_path
                    report = Report(reporting_asn=self.asn, prefix=ann.prefix, as_path=adjusted_as_path)
                    self.trusted_server.receive_report(report)
            else:
                report = Report(reporting_asn=self.asn, prefix=ann.prefix, as_path=ann.as_path)
                self.trusted_server.receive_report(report)
        return super(ROVSMS, self).receive_ann(ann, *args, **kwargs)

    def _force_add_blackholes_from_avoid_list(self, ordered_prefix_subprefix_dict):
        holes = []
        for reported_prefix in self.trusted_server._recommendations:
            reported_prefix_network = ipaddress.ip_network(reported_prefix)
            # If the reported prefix is a prefix hijack, and a valid ann already exists,
            # don't consider blackholing it. Hidden Hijacks don't exist in prefix hijacks.
            reported_prefix_ann = self._local_rib.get_ann(reported_prefix)
            if reported_prefix_ann and reported_prefix_ann.valid_by_roa:
                continue
            for prefix, ann in self._local_rib.prefix_anns():
                ann_prefix_network = ipaddress.ip_network(prefix)
                # Check if ann is
                # - The reported prefix is a subprefix of it
                # - The AS path of has a member on the avoid list
                if reported_prefix_network.subnet_of(ann_prefix_network) and \
                    self.trusted_server.rec_blackhole(reported_prefix, ann.as_path):
                    # Create Blackhole
                    # We need to create our own subprefix ann
                    # Since we may not have actually received the hijack
                    # Since this policy is for hidden hijacks
                    if reported_prefix_ann:
                        blackhole_ann = reported_prefix_ann.copy()
                    else:
                        blackhole_ann = ann.copy()
                    blackhole_ann.prefix = reported_prefix
                    blackhole_ann.roa_valid_length = False
                    blackhole_ann.blackhole = True
                    blackhole_ann.traceback_end = True
                    holes.append(blackhole_ann)

        for hole in holes:
            # Add blackhole ann to localRIB
            self._local_rib.add_ann(hole)

    def use_relay(self, relay_asns, relay_prefix_dict, assume_relays_are_reachable, scenario):
        """return the relay that it would use
        :param scenario:
        """
        # TODO: Future enhancement: Consider picking preference with
        #   1. Relationship preference
        #   2. Shortest path
        # Check if Relays are assumed to be reachable
        if assume_relays_are_reachable:
            return random.choice(list(relay_asns))
        else:
            # Check what relay ASes are available to this AS
            accessible_relays = list()
            for asn in relay_asns:
                prefix = relay_prefix_dict[asn]
                # TODO: should probably check if ASN is at the end of the path?
                if prefix in self._local_rib._info and asn in self._local_rib._info[prefix].as_path:
                    # Check if attacker on path, and if so, add attacker to list
                    attackers_on_path = scenario.attacker_asns & set(self._local_rib._info[prefix].as_path)
                    if attackers_on_path:
                        # attacker_on_path is expected to be of size 1
                        accessible_relays.append(next(iter(attackers_on_path)))
                    else:
                        accessible_relays.append(asn)
            # Uniformly at random select from available relays
            return random.choice(accessible_relays) if len(accessible_relays) > 0 else None



class ROVSMSK1(ROVSMS):
    name = "ROV V4 Lite K1"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 1
    trusted_server = TrustedServer(max_num_dishonest_nodes=1)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK2(ROVSMS):
    name = "ROV V4 Lite K2"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 2
    trusted_server = TrustedServer(max_num_dishonest_nodes=2)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK3(ROVSMS):
    name = "ROV V4 Lite K3"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 3
    trusted_server = TrustedServer(max_num_dishonest_nodes=3)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK4(ROVSMS):
    name = "ROV V4 Lite K4"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 4
    trusted_server = TrustedServer(max_num_dishonest_nodes=4)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK5(ROVSMS):
    name = "ROV V4 Lite K5"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 5
    trusted_server = TrustedServer(max_num_dishonest_nodes=5)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK6(ROVSMS):
    name = "ROV V4 Lite K6"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 6
    trusted_server = TrustedServer(max_num_dishonest_nodes=6)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK7(ROVSMS):
    name = "ROV V4 Lite K7"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 7
    trusted_server = TrustedServer(max_num_dishonest_nodes=7)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK10(ROVSMS):
    name = "ROV V4 Lite K10"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 10
    trusted_server = TrustedServer(max_num_dishonest_nodes=10)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK20(ROVSMS):
    name = "ROV V4 Lite K20"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 20
    trusted_server = TrustedServer(max_num_dishonest_nodes=20)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK30(ROVSMS):
    name = "ROV V4 Lite K30"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 30
    trusted_server = TrustedServer(max_num_dishonest_nodes=30)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK50(ROVSMS):
    name = "ROV V4 Lite K50"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 50
    trusted_server = TrustedServer(max_num_dishonest_nodes=50)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK70(ROVSMS):
    name = "ROV V4 Lite K70"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 70
    trusted_server = TrustedServer(max_num_dishonest_nodes=70)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK100(ROVSMS):
    name = "ROV V4 Lite K100"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 100
    trusted_server = TrustedServer(max_num_dishonest_nodes=100)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK150(ROVSMS):
    name = "ROV V4 Lite K150"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 150
    trusted_server = TrustedServer(max_num_dishonest_nodes=150)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK200(ROVSMS):
    name = "ROV V4 Lite K200"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 200
    trusted_server = TrustedServer(max_num_dishonest_nodes=200)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK300(ROVSMS):
    name = "ROV V4 Lite K300"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 300
    trusted_server = TrustedServer(max_num_dishonest_nodes=300)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK500(ROVSMS):
    name = "ROV V4 Lite K500"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 500
    trusted_server = TrustedServer(max_num_dishonest_nodes=500)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK1000(ROVSMS):
    name = "ROV V4 Lite K1000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 1000
    trusted_server = TrustedServer(max_num_dishonest_nodes=1000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK1500(ROVSMS):
    name = "ROV V4 Lite K1500"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 1500
    trusted_server = TrustedServer(max_num_dishonest_nodes=1500)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK2000(ROVSMS):
    name = "ROV V4 Lite K2000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 2000
    trusted_server = TrustedServer(max_num_dishonest_nodes=2000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK5000(ROVSMS):
    name = "ROV V4 Lite K5000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 5000
    trusted_server = TrustedServer(max_num_dishonest_nodes=5000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK10000(ROVSMS):
    name = "ROV V4 Lite K10000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 10000
    trusted_server = TrustedServer(max_num_dishonest_nodes=10000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK20000(ROVSMS):
    name = "ROV V4 Lite K20000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 20000
    trusted_server = TrustedServer(max_num_dishonest_nodes=20000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)


class ROVSMSK30000(ROVSMS):
    name = "ROV V4 Lite K30000"

    __slots__ = tuple()

    _max_num_dishonest_nodes = 30000
    trusted_server = TrustedServer(max_num_dishonest_nodes=30000)

    def __init__(self, *args, **kwargs):
        super(ROVSMS, self).__init__(*args, **kwargs)
