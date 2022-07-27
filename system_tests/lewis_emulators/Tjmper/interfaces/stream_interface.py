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
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.get_status).escape("?STS").eos().build(),
            CmdBuilder(self.set_mode).escape("OPM").int().eos().build(),
        }

    def handle_error(self, request, error):
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    def get_status(self):
        return "ACK\rITJ0,OPM{},LMT000000,AIR0,ERR0".format(self.device.mode)

    def set_mode(self, mode):
        self.device.mode = mode
        return "ACK"