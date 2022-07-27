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

class TjmperTests(unittest.TestCase):
    """
    Tests for the Tjmper IOC.
    """
    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Tjmper", DEVICE_PREFIX)
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX, default_wait_time=0)

    @parameterized.expand(
        parameterized_list(["Home", "Block 1", "Block 2"])
    )
    def test_WHEN_mode_set_THEN_mode_uodates(self, _, mode_name):
        self.ca.set_pv_value("MODE:SP", mode_name)
        self.ca.assert_that_pv_is("MODE", mode_name)
