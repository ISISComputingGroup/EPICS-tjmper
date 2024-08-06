from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


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
