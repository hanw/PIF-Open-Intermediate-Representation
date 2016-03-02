import logging

from pif_ir.bir.objects.bir_exception import BIRControlStateError
from pif_ir.bir.objects.bir_validate import check_attributes
from pif_ir.bir.objects.basic_block import BasicBlock
from pif_ir.bir.objects.processor import Processor

class ControlFlow(Processor):
    """
    @brief Class for a control flow object

    @param name The name of the control flow AIR object
    @param air_control_flow_attrs The attributes of the control_flow AIR object
    @param first_packet_offset The first packet offset
    @param first_basic_block The first basic block
    """
    required_attributes = ['start_control_state']
    def __init__(self, name, control_flow_attrs, basic_blocks):
        super(ControlFlow, self,).__init__(name)
        check_attributes(name, control_flow_attrs, 
                         ControlFlow.required_attributes)
        logging.debug("Adding Control Flow {0}".format(name))

        start_control_state = control_flow_attrs['start_control_state']
        if (len(start_control_state) != 2 or
            not isinstance(start_control_state[0],int)):
            raise BIRControlStateError(self.name)

        self.start_offset = []   # based on 'start_control_state'
        self.start_state = []    # based on 'start_control_state'
        self._handle_control_state(control_flow_attrs['start_control_state'])
        self.basic_blocks = basic_blocks

    def _handle_control_state(self, ncs_attrs):
        # FIXME: this needs to be expanded. The implementation will differ
        #        from the BB next_control_state (i.e. no local_header)
        if len(ncs_attrs) != 2:
            raise BIRControlStateError(self.name)

        self.start_offset = ncs_attrs[0]
        self.start_state = ncs_attrs[1]

    def process(self, packet, bit_offset=0):
        """
        @brief Pass a packet through this control_flow

        @param packet A packet instance to be processed
        @return result from the final basic block executed in control flow
        """
        basic_block = self.start_state
        curr_offset = self.start_offset
        logging.debug("Control flow %s, pkt %d, offset %d: starting at bb %s",
                      self.name, packet.idx, curr_offset, basic_block)
        while basic_block:
            logging.info("process {}.{}".format(self.name, basic_block))
            ret = self.basic_blocks[basic_block].process(packet, curr_offset) 
            curr_offset, basic_block = ret

