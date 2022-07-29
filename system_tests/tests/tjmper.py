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


MODES = [
    "All out",
    "PLT1 and SMPL engaged",
    "PLT2 and SMPL engaged"
]

AIR_SUPPLY = [
    (0, "Off Dumped"),
    (1, "Off Valve Reset"),
    (2, "On Dumped"),
    (3, "On Valve Reset")
]

ERRORS = [
    (0, "No Error (Operational)"),
    (1, "PLT1 Homing TMO"),
    (2, "PLT1 Engaging TMO"),
    (3, "PLT1EN SMPL Homing TMO"),
    (4, "PLT1EN SMPL Engaging TMO"),
    (5, "PLT2 Homing TMO"),
    (6, "PLT2 Engaging TMO"),
    (7, "PLT2EN SMPL Homing TMO"),
    (8, "PLT2EN SMPL Engaging TMO")
]

ALARM_PVS = [
    "ID",
    "MODE",
    "LMT",
    "LMT:PLATE1:HOME",
    "LMT:PLATE1:ENGAGED",
    "LMT:PLATE2:HOME",
    "LMT:PLATE2:ENGAGED",
    "LMT:SAMPLE:HOME",
    "LMT:SAMPLE:ENGAGED",
    "AIR",
    "ERR"
]


class TjmperTests(unittest.TestCase):
    """
    Tests for the Tjmper IOC.
    """
    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Tjmper", DEVICE_PREFIX)
        self._lewis.backdoor_run_function_on_device("reset")
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX, default_wait_time=0)

    def test_WHEN_id_set_via_backdoor_THEN_id_updates(self):
        id_value = 4
        self._lewis.backdoor_set_on_device("id", id_value)
        self.ca.assert_that_pv_is("ID", id_value)

    @parameterized.expand(parameterized_list(AIR_SUPPLY))
    def test_WHEN_air_supply_set_via_backdoor_THEN_air_supply_updates(self, _, code, string):
        self._lewis.backdoor_set_on_device("air_supply", code)
        self.ca.assert_that_pv_is("AIR", string)

    @parameterized.expand(parameterized_list(ERRORS))
    def test_WHEN_error_set_via_backdoor_THEN_error_updates(self, _, code, string):
        self._lewis.backdoor_set_on_device("error_state", code)
        self.ca.assert_that_pv_is("ERR", string)

    @parameterized.expand(parameterized_list(MODES))
    def test_WHEN_mode_set_THEN_mode_updates(self, _, mode):
        self.ca.set_pv_value("MODE:SP", mode)
        self.ca.assert_that_pv_is("MODE", mode)


        #self.ca.assert_that_pv_is("LMT:PLATE1:HOME", state[0])
        #self.ca.assert_that_pv_is("LMT:PLATE1:ENGAGED", state[1])
        #self.ca.assert_that_pv_is("LMT:PLATE2:HOME", state[2])
        #self.ca.assert_that_pv_is("LMT:PLATE2:ENGAGED", state[3])
        #self.ca.assert_that_pv_is("LMT:SAMPLE:HOME", state[4])
        #self.ca.assert_that_pv_is("LMT:SAMPLE:ENGAGED", state[5])
        
    @contextlib.contextmanager
    def _disconnect_device(self):
        self._lewis.backdoor_set_on_device("connected", False)
        try:
            yield
        finally:
            self._lewis.backdoor_set_on_device("connected", True)

    @parameterized.expand(parameterized_list(ALARM_PVS))
    def test_WHEN_device_disconnected_THEN_go_into_alarm(self, _, alarm_pv):
        self.ca.assert_that_pv_alarm_is(alarm_pv, self.ca.Alarms.NONE)

        with self._disconnect_device():
            self.ca.assert_that_pv_alarm_is(alarm_pv, self.ca.Alarms.INVALID)

        self.ca.assert_that_pv_alarm_is(alarm_pv, self.ca.Alarms.NONE)
