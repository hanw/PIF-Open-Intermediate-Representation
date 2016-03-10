from pif_ir.bir.utils.exceptions import BIRError

class ControlState(object):
    def __init__(self, control_state_attr, bir_parser):
        # control_state format:
        #   - [[cond, new_offset], [,], [,], ..., default_offset]
        #   - [[cond, new_bb], [,], [,], ..., default_bb]
        self.offset = control_state_attr[0]
        self.basic_block = control_state_attr[1]
        self.bir_parser = bir_parser

    def _get_offset(self, header, packet, bit_offset):
        for cond in self.offset:
            if isinstance(cond, str) or isinstance(cond, int):
                return self.bir_parser.eval_inst(cond, header, packet,
                                                 bit_offset)
            elif self.bir_parser.eval_cond(cond[0], header, packet, 
                                           bit_offset):
                return self.bir_parser.eval_inst(cond[1], header, packet,
                                                 bit_offset)
        raise BIRError("didn't find offset!")

    def _get_basic_block(self, header, packet, bit_offset):
        for cond in self.basic_block:
            if isinstance(cond, str):
                return cond
            elif self.bir_parser.eval_cond(cond[0], header, packet, 
                                           bit_offset):
                return cond[1]
        raise BIRError("didn't find basic_block!")

    def process(self, header, packet, bit_offset):
        offset = self._get_offset(header, packet, bit_offset)
        basic_block = self._get_basic_block(header, packet, bit_offset)
        if basic_block == "$done$":
            basic_block = None
        return offset, basic_block
