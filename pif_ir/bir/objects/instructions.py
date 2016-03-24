from pif_ir.bir.utils.exceptions import BIRError

class Instructions(object):
    def __init__(self, inst_attrs, table, header, other_modules,  bir_parser):
        self.instructions = inst_attrs
        self.table = table
        self.header = header
        self.other_modules = other_modules
        self.bir_parser = bir_parser

    def _assign(self, sink, value, packet, bit_offset):
        sink = sink.split('.')
        if len(sink) == 2:
            packet.metadata[sink[0]].set_value(sink[1], value)
        else:
            size = self.header.field_size(sink[0])
            offset = bit_offset + self.header.field_offset(sink[0])
            packet.set_bits(value, size, offset) 

    def _handle_v_call(self, sig, packet, bit_offset):
        result = self.bir_parser.eval_inst(sig[1], self.header, packet,
                                           bit_offset)
        self._assign(sig[0], result, packet, bit_offset)

    # O Type instructions are the build-in functionality
    def _handle_o_call(self, sig, packet, bit_offset):
        op = sig[0]
        args = sig[1]

        if op == 'tLookup':
            resp = packet.metadata[args[0]]
            req = packet.metadata[args[1]]
            if self.table:
                resp.reset_values()
                self.table.lookup(req, resp)

        elif op == 'hInsert':
            length = args[0] if len(args) > 0 else len(self.header)
            packet.insert(length, bit_offset)
        elif op == 'hRemove':
            length = args[0] if len(args) > 0 else len(self.header)
            packet.remove(length, bit_offset)
        elif op == 'tInsert':
            mask = args[2] if len(args) > 2 else None
            if self.table:
                self.table.add_entry(args[0], args[1], mask)
        elif op == 'tRemove':
            mask = args[2] if len(args) > 2 else None
            if self.table:
                self.table.remove_entry(args[0], args[1], mask)
        else:
            raise BIRError("unknown build-in function: {}".format(op))

    def _handle_m_call(self, sig, packet, bit_offset):
        if len(sig[1]) != 2:
            raise BIRError("M instructions require 2 arguments")
        op = sig[0]
        data_out = sig[1][0]
        data_in = sig[1][1]

        if op not in self.other_modules.keys():
            raise BIRError("cannot find other_module: {}".format(sig[0]))
        module = self.other_modules[op]

        if data_out:
            data_out = packet.metadata[data_out]
        if data_in:
            # TODO: to ensure correctness, the data_in should be a copy of the 
            #       metadata instance.
            data_in = packet.metadata[data_in]
        module(data_in, data_out)

    def process(self, packet, bit_offset):
        for inst in self.instructions:
            if inst[0] == 'V':
                self._handle_v_call(inst[1:], packet, bit_offset)
            elif inst[0] == 'O':
                self._handle_o_call(inst[1:], packet, bit_offset)
            elif inst[0] == 'M':
                self._handle_m_call(inst[1:], packet, bit_offset)
            else:
                raise BIRError("unknown instruction type: {}".format(inst[0]))
