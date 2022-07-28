from collections import OrderedDict
from .states import DefaultState
from lewis.devices import StateMachineDevice


class SimulatedTjmper(StateMachineDevice):

    def _initialize_data(self):
        self.connected = True

        self.id = 0
        self.operating_mode = 0
        self.piston_limits_state = 0
        self.air_supply = 0
        self.error_state = 0

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])
