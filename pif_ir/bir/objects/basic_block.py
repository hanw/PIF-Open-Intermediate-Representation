import logging

from pif_ir.bir.objects.bir_exception import BIRControlStateError
from pif_ir.bir.objects.bir_exception import BIRRefError
from pif_ir.bir.objects.bir_validate import check_attributes

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
                 ncs_parser, inst_parser):
        check_attributes(name, bb_attrs, BasicBlock.required_attributes)
        logging.debug("Adding basic_block {0}".format(name))

        # set the name
        self.name = name
        self.local_header = None
        self.local_table = None
        self.instructions = []
        self.instructions = bb_attrs['instructions']

        self.next_offset = []   # based on 'next_control_state'
        self.next_state = []    # based on 'next_control_state'
        self._handle_next_control_state(bb_attrs['next_control_state'])

        self.inst_parser = inst_parser
        self.ncs_parser = ncs_parser

        # set the local_header
        header_name = bb_attrs.get('local_header', None)
        if header_name:
            if  header_name not in bir_headers.keys():
                raise BIRRefError(header_name, self.name)
            self.local_header = bir_headers[header_name]

        # set the local_table
        table_name = bb_attrs.get('local_table', None)
        if table_name:
            if  table_name not in bir_tables.keys():
                raise BIRRefError(table_name, self.name)
            self.local_table = bir_tables[table_name]


    def _handle_next_control_state(self, ncs_attrs):
        # next_control_state format:
        #   - [cond, offset_expr]       // any number
        #   - offset_expr               // default
        #   - [cond, next_basic_block]  // any number
        #   - next_basic_block          // default
        target = self.next_offset
        for attr in ncs_attrs:
            if not isinstance(attr, list):
                target.append([True, attr])
                target = self.next_state
            else:
                target.append(attr)
        # we need know what the next_offset is, and what state to go to.
        if len(self.next_offset) < 1 or self.next_offset[-1][0] != True:
            raise BIRControlStateError(self.name)
        if len(self.next_state) < 1 or self.next_state[-1][0] != True:
            raise BIRControlStateError(self.name)

    def _assign(self, sink, value, header, packet, bit_offset):
        sink = sink.split('.')
        if len(sink) == 2:
            packet.metadata[sink[0]].set_value(sink[1], value)
        else:
            size = header.field_size(sink[0])
            offset = bit_offset + header.field_offset(sink[0])
            packet.set_bits(value, size, offset) 

    def _get_next_offset(self, packet, bit_offset):
        for cond in self.next_offset:
            if cond[0] == True:
                return self.ncs_parser.evaluate(cond[1], self.local_header,
                                                packet, bit_offset)

            elif self.ncs_parser.evaluate(cond[0], self.local_header, packet,
                                        bit_offset):
                return self.ncs_parser.evaluate(cond[1], self.local_header,
                                                packet, bit_offset)
        raise BIRControlStateError(self.name)

    def _get_next_state(self, packet, bit_offset):
        for cond in self.next_state:
            if cond[0] == True:
                return cond[1]
            elif self.ncs_parser.evaluate(cond[0], self.local_header, packet, 
                                 bit_offset):
                return cond[1]

    def process(self, packet, bit_offset=0):
        for inst in self.instructions:
            if inst[0] == 'V':
                result = self.inst_parser.evaluate(inst[2], self.local_header, 
                                                   packet, bit_offset)
                self._assign(inst[1], result, self.local_header, packet, 
                             bit_offset)
            elif inst[0] == 'S':
                resp = packet.metadata[inst[1]]
                req = packet.metadata[inst[2]]
                if self.local_table:
                    self.local_table.lookup(req, resp)
            else:
                raise BIRRefError("{} call".format(inst[0]), self.name)

        next_offset = self._get_next_offset(packet, bit_offset)
        if next_offset < bit_offset:
            raise BIRControlStateError(self.name)

        next_state = self._get_next_state(packet, bit_offset)
        if next_state == "$done$":
            next_state = None
        return next_offset, next_state

