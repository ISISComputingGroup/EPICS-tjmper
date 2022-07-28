from lewis.adapters.stream import StreamInterface, Cmd
from lewis.utils.command_builder import CmdBuilder
from lewis.core.logging import has_log
from lewis.utils.replies import conditional_reply


@has_log
class TjmperStreamInterface(StreamInterface):
    
    in_terminator = "\r"
    out_terminator = "\r"

    def __init__(self):
        super(TjmperStreamInterface, self).__init__()
        self.commands = {
            CmdBuilder(self.get_status).escape("?STS").eos().build(),
            CmdBuilder(self.set_operating_mode).escape("OPM").int().eos().build(),
        }

    def handle_error(self, request, error):
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    @conditional_reply("connected")
    def get_status(self):
        return f"ACK\rITJ{self.device.id},OPM{self.device.operating_mode},LMT{self.device.get_piston_limits_status()},AIR{self.device.air_supply},ERR{self.device.error_state}"
        
    @conditional_reply("connected")
    def set_operating_mode(self, operating_mode):
        self.device.operating_mode = operating_mode

        if operating_mode == 0:
            self.device.mode_0_set()
        elif operating_mode == 1:
            self.device.mode_1_set()
        else:
            self.device.mode_2_set()

        return "ACK"