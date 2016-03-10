import logging

from pif_ir.bir.objects.control_state import ControlState
from pif_ir.bir.objects.processor import Processor

from pif_ir.bir.utils.validate import check_attributes
from pif_ir.bir.utils.validate import check_control_state

class ControlFlow(Processor):
    """
    @brief Class for a control flow object

    @param name The name of the control flow AIR object
    @param air_control_flow_attrs The attributes of the control_flow AIR object
    @param first_packet_offset The first packet offset
    @param first_basic_block The first basic block
    """
    required_attributes = ['start_control_state']
    def __init__(self, name, control_flow_attrs, basic_blocks, bir_parser):
        super(ControlFlow, self,).__init__(name)
        check_attributes(name, control_flow_attrs, 
                         ControlFlow.required_attributes)
        logging.debug("Adding Control Flow {0}".format(name))

        self.basic_blocks = basic_blocks

        cf = control_flow_attrs['start_control_state']
        check_control_state(self.name, cf)
        self.control_state = ControlState(cf, None, bir_parser)

    def process(self, packet, bit_offset=0):
        """
        @brief Pass a packet through this control_flow

        @param packet A packet instance to be processed
        @return result from the final basic block executed in control flow
        """
        offset, basic_block = self.control_state.process(packet, bit_offset)
        msg = "packet {} entered control_flow({}) with offset({})".format(
            packet.idx, self.name, offset)
        logging.debug(msg)
        while basic_block:
            logging.info("PROCESS: {}.{}".format(self.name, basic_block))
            offset, basic_block =self.basic_blocks[basic_block].process(packet,
                                                                        offset) 
