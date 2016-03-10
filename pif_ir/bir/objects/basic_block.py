import logging

from pif_ir.bir.objects.control_state import ControlState
from pif_ir.bir.objects.instructions import Instructions

from pif_ir.bir.utils.exceptions import BIRRefError
from pif_ir.bir.utils.validate import check_attributes
from pif_ir.bir.utils.validate import check_control_state
from pif_ir.bir.utils.validate import check_instructions

class BasicBlock(object):
    """
    @brief Class for a basic block that can be executed within a control flow

    A basic block in BIR carries out a set of instructions, within an optional
    context comprising a header of a packet at some offset and/or a table.
    It then optionally updates the packet offset, and either transitions
    to another basic block or terminates the control flow.
    """
    required_attributes = ['instructions', 'next_control_state']

    def __init__(self, name, bb_attrs, bir_headers, bir_tables, 
                 bir_other_modules, bir_parser):
        check_attributes(name, bb_attrs, BasicBlock.required_attributes)
        logging.debug("Adding basic_block {0}".format(name))

        self.name = name
        self.local_header = self._get_header(bb_attrs, bir_headers)
        self.local_table = self._get_table(bb_attrs, bir_tables)

        check_instructions(self.name, bb_attrs['instructions'])
        self.instructions = Instructions(bb_attrs['instructions'],
                                         self.local_table,
                                         self.local_header,
                                         bir_other_modules,
                                         bir_parser)

        check_control_state(self.name, bb_attrs['next_control_state'])
        self.control_state = ControlState(bb_attrs['next_control_state'],
                                          self.local_header,
                                          bir_parser)

    def _get_header(self, bb_attrs, bir_headers):
        header_name = bb_attrs.get('local_header', None)
        if header_name:
            header = bir_headers.get(header_name, None)
            if not header:
                raise BIRRefError(header_name, self.name)
        else:
            header = None
        return header

    def _get_table(self, bb_attrs, bir_tables):
        table_name = bb_attrs.get('local_table', None)
        if table_name:
            table = bir_tables.get(table_name, None)
            if not table:
                raise BIRRefError(table_name, self.name)
        else:
            table = None
        return table

    def process(self, packet, bit_offset=0):
        self.instructions.process(packet, bit_offset)
        return self.control_state.process(packet, bit_offset)
