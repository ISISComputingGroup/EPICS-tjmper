import contextlib
import unittest

from parameterized import parameterized

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim, parameterized_list


DEVICE_PREFIX = "TJMPER_01"


IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("TJMPER"),
        "macros": {},
        "emulator": "Tjmper",
    },
]


#TEST_MODES = [TestModes.RECSIM, TestModes.DEVSIM]
TEST_MODES = [TestModes.DEVSIM]

STATES = [
    ("Home", ),
    ("Block 1", ),
    ("Block 2", )
]

class TjmperTests(unittest.TestCase):
    """
    Tests for the Tjmper IOC.
    """
    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Tjmper", DEVICE_PREFIX)
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX, default_wait_time=0)

    def test_WHEN_id_set_via_backdoor_THEN_id_updates(self):
        id_value = 4
        self._lewis.backdoor_set_on_device("id", id_value)
        self.ca.assert_that_pv_is("ID", id_value)

    @parameterized.expand(
        parameterized_list(["Home", "Block 1", "Block 2"])
    )
    def test_WHEN_mode_set_THEN_mode_updates(self, _, mode_name):
        self.ca.set_pv_value("MODE:SP", mode_name)
        self.ca.assert_that_pv_is("MODE", mode_name)

    @parameterized.expand(
        parameterized_list(STATES)
    )
    def test_GIVEN_all_pistons_out_WHEN_mode_set_THEN_states_are_correct(self, _, mode, state):
        pass
        
    @contextlib.contextmanager
    def _disconnect_device(self):
        self._lewis.backdoor_set_on_device("connected", False)
        try:
            yield
        finally:
            self._lewis.backdoor_set_on_device("connected", True)

    def test_WHEN_device_disconnected_THEN_go_into_alarm(self):
        self.ca.assert_that_pv_alarm_is("ERR", self.ca.Alarms.NONE)

        with self._disconnect_device():
            self.ca.assert_that_pv_alarm_is("ERR", self.ca.Alarms.INVALID)

        self.ca.assert_that_pv_alarm_is("ERR", self.ca.Alarms.NONE)
