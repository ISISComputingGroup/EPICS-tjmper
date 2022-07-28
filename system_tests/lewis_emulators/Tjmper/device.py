from collections import OrderedDict
from .states import DefaultState
from lewis.devices import StateMachineDevice


class SimulatedTjmper(StateMachineDevice):

    def _initialize_data(self):
        self.connected = True
        self.reset()
        
    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])

    def reset(self):
        self.id = 0
        self.operating_mode = 0
        self.plate_1_home = 1
        self.plate_1_engaged = 0
        self.plate_2_home = 1
        self.plate_2_engaged = 0
        self.sample_home = 1
        self.sample_engaged = 0
        self.air_supply = 0
        self.error_state = 0

    def mode_0_set(self):
        self.plate_1_home = 1
        self.plate_1_engaged = 0
        self.plate_2_home = 1
        self.plate_2_engaged = 0
        self.sample_home = 1
        self.sample_engaged = 0

    def mode_1_set(self):
        self.plate_1_home = 0
        self.plate_1_engaged = 1
        self.plate_2_home = 1
        self.plate_2_engaged = 0
        self.sample_home = 0
        self.sample_engaged = 1

    def mode_2_set(self):
        self.plate_1_home = 1
        self.plate_1_engaged = 0
        self.plate_2_home = 0
        self.plate_2_engaged = 1
        self.sample_home = 0
        self.sample_engaged = 1

    def get_piston_limits_status(self):
        return f"{self.plate_1_home}{self.plate_1_engaged}{self.plate_2_home}{self.plate_2_engaged}{self.sample_home}{self.sample_engaged}"