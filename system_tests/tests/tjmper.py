import contextlib
import unittest

from parameterized import parameterized

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, parameterized_list


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

LIMITS = [
    [1, 0, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 1],
    [0, 1, 1, 0, 1, 0],
    [1, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1, 0],
    [0, 1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 0]
]

AIR_SUPPLY = [
    (0, "Off Dumped"),
    (1, "Off Valve Reset"),
    (2, "On Dumped"),
    (3, "On Valve Reset")
]

ERRORS = [
    (0, "No Error (Operational)",   ChannelAccess.Alarms.NONE),
    (1, "PLT1 Homing TMO",          ChannelAccess.Alarms.MAJOR),
    (2, "PLT1 Engaging TMO",        ChannelAccess.Alarms.MAJOR),
    (3, "PLT1EN SMPL Homing TMO",   ChannelAccess.Alarms.MAJOR),
    (4, "PLT1EN SMPL Engaging TMO", ChannelAccess.Alarms.MAJOR),
    (5, "PLT2 Homing TMO",          ChannelAccess.Alarms.MAJOR),
    (6, "PLT2 Engaging TMO",        ChannelAccess.Alarms.MAJOR),
    (7, "PLT2EN SMPL Homing TMO",   ChannelAccess.Alarms.MAJOR),
    (8, "PLT2EN SMPL Engaging TMO", ChannelAccess.Alarms.MAJOR)
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

    @parameterized.expand(parameterized_list(LIMITS))
    def test_WHEN_limits_set_via_backdoor_THEN_limits_update(self, _, states):
        self._lewis.backdoor_set_on_device("plate_1_home", states[0])
        self._lewis.backdoor_set_on_device("plate_1_engaged", states[1])
        self._lewis.backdoor_set_on_device("plate_2_home", states[2])
        self._lewis.backdoor_set_on_device("plate_2_engaged", states[3])
        self._lewis.backdoor_set_on_device("sample_home", states[4])
        self._lewis.backdoor_set_on_device("sample_engaged", states[5])

        convert = lambda n: "True" if n == 1 else "False"
        self.ca.assert_that_pv_is("LMT:PLATE1:HOME", convert(states[0]))
        self.ca.assert_that_pv_is("LMT:PLATE1:ENGAGED", convert(states[1]))
        self.ca.assert_that_pv_is("LMT:PLATE2:HOME", convert(states[2]))
        self.ca.assert_that_pv_is("LMT:PLATE2:ENGAGED", convert(states[3]))
        self.ca.assert_that_pv_is("LMT:SAMPLE:HOME", convert(states[4]))
        self.ca.assert_that_pv_is("LMT:SAMPLE:ENGAGED", convert(states[5]))
        
    @parameterized.expand(parameterized_list(AIR_SUPPLY))
    def test_WHEN_air_supply_set_via_backdoor_THEN_air_supply_updates(self, _, code, string):
        self._lewis.backdoor_set_on_device("air_supply", code)
        self.ca.assert_that_pv_is("AIR", string)

    @parameterized.expand(parameterized_list(ERRORS))
    def test_WHEN_error_set_via_backdoor_THEN_error_updates(self, _, code, string, state):
        self._lewis.backdoor_set_on_device("error_state", code)
        self.ca.assert_that_pv_is("ERR", string)
        self.ca.assert_that_pv_alarm_is("ERR", state)

    @parameterized.expand(parameterized_list(MODES))
    def test_WHEN_mode_set_THEN_mode_updates(self, _, mode):
        self.ca.set_pv_value("MODE:SP", mode)
        self.ca.assert_that_pv_is("MODE", mode)

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
