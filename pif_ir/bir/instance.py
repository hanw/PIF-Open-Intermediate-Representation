# @file
# @brief The top level BIR configuration object
#
# This holds the Python representation of the YAML top level
# description of the BIR instance and provides some basic features
# such as iterators over objects in the instance (by type).
#

import os
import yaml
import logging

from importlib import import_module

from pif_ir.meta_ir.instance import MetaIRInstance

from pif_ir.bir.objects.basic_block import BasicBlock
from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.control_flow import ControlFlow
from pif_ir.bir.objects.metadata_instance import MetadataInstance
from pif_ir.bir.objects.packet_instance import PacketInstance
from pif_ir.bir.objects.processor import Processor
from pif_ir.bir.objects.processor import ThreadedProcessor
from pif_ir.bir.objects.table import Table
from pif_ir.bir.objects.table_entry import TableEntry

from pif_ir.bir.utils.exceptions import BIRError
from pif_ir.bir.utils.bir_parser import BIRParser

def hexify(buf, bpl=16):
    """
    @param buf bytearray
    @param bpl Bytes Per Line
    """
    ret = ""
    for pos in range(0, len(buf), bpl):
        line = ":".join(["%02X" % b for b in buf[pos:pos+bpl]])
        ret += "\n\tByte %02d: %s" % (pos, line)
    return ret

class BirInstance(MetaIRInstance):
    def __init__(self, name, input, transmit_handler):
        """
        @brief BirInstance constructor

        @param name The name of the instance
        @param input An object with the YAML description of the BIR instance
        @param transmit_handler A function to be called to transmit pkts
        """
        local_dir = os.path.dirname(os.path.abspath(__file__))
        bir_meta_yml = os.path.join(local_dir, 'bir_meta.yml')
        super(BirInstance, self).__init__(bir_meta_yml)

        self.name = name
        self.add_content(input)
        self.transmit_processor = TransmitProcessor(transmit_handler)

        self.disabled = True
        self.other_processors_running = False

        # create parsers to handle next_control_states, and the
        # F instructions
        bir_parser = BIRParser()

        # BIR objects
        self.bir_structs = {}
        self.bir_tables = {}
        self.bir_other_modules = {}
        self.bir_basic_blocks = {}
        self.bir_control_flows = {}
        self.bir_other_processors = {}
        self.start_processor = []
        self.table_init = []

        for name, val in self.struct.items():
            self.bir_structs[name] = BIRStruct(name, val)
        for name, val in self.table.items():
            self.bir_tables[name] = Table(name, val)
        for name, val in self.other_module.items():
            for op in val['operations']:
                module = "{}.{}".format(name, op)
                self.bir_other_modules[module] = self._load_module(name, op)
        for name, val in self.basic_block.items():
            self.bir_basic_blocks[name] = BasicBlock(name, val, 
                                                     self.bir_structs, 
                                                     self.bir_tables, 
                                                     self.bir_other_modules,
                                                     bir_parser)
        for name, val in self.control_flow.items():
            self.bir_control_flows[name] = ControlFlow(name, val,
                                                       self.bir_basic_blocks,
                                                      bir_parser)
        for name, val in self.other_processor.items():
            self.bir_other_processors[name] = self._load_processor(name,
                                                                   val['class'])

        # BIR processor layout
        for layout in self.processor_layout.values():
            if layout['format'] != 'list':
                logging.error("usupported layout format")
                exit(1)

            last_proc = None
            for proc_name in layout['implementation']:
                curr_proc = self._get_processor(proc_name)
                if last_proc == None:
                    self.start_processor = curr_proc
                else:
                    last_proc.next_processor = curr_proc
                last_proc = curr_proc
            last_proc.next_processor = self.transmit_processor

        # Table initialization is part of the YAML until an API can be 
        # created
        ext_objs = self.external_object_map
        if 'table_initialization' in ext_objs.keys():
            self.table_init = ext_objs['table_initialization']

    def _load_module(self, name, operation):
        module_name = "pif_ir.bir.objects.other_module.{}".format(name)
        other_module = import_module(module_name)
        return getattr(other_module, operation)

    def _load_processor(self, name, class_name):
        proc_name = "pif_ir.bir.objects.other_processor.{}".format(name)
        other_processor = import_module(proc_name)
        return getattr(other_processor, class_name)

    def _get_processor(self, name):
        if name in self.bir_control_flows.keys():
            return self.bir_control_flows[name]
        elif name in self.bir_other_processors.keys():
            return self.bir_other_processors[name]
        else:
            raise BIRError("unknown processor: {}".format(name))

    def process_table_init(self):
        for init_entry in self.table_init:
            for table_name, entry_desc in init_entry.items():
                ent = TableEntry(entry_desc['match_type'],
                                 entry_desc['value'],
                                 entry_desc['key'],
                                 entry_desc.get('mask', None))
                self.bir_tables[table_name].add_entry(ent)

    def enable(self):
        # if the other processors are not running start them
        if not self.other_processors_running:
            for name, proc in self.bir_other_processors.items():
                if isinstance(proc, ThreadedProcessor):
                    logging.debug("starting Processor: {}".format(name))
                    proc.start()
            self.other_processors_running = True

        logging.debug("enabling switch {}".format(self.name))
        self.disabled = False

    def disable(self):
        logging.debug("disabling switch {}".format(self.name))
        self.disabled = True

    def kill(self):
        if self.other_processors_running:
            for name, proc in self.bir_other_processors.items():
                if isinstance(proc, ThreadedProcessor):
                    logging.debug("stopping processor: {}".format(name))
                    proc.kill()
                    proc.join()

    def process_packet(self, in_port, packet_data):
        if self.disabled:
            logging.debug("Switch is disabled; discarding packet")
        else:
            buf = bytearray(packet_data)
            packet = PacketInstance(buf, self.metadata, self.bir_structs)
            logging.info("Packet {} start: {}".format(packet.idx, hexify(buf)))

            try:
                self.start_processor.process(packet)
            except BIRError as e:
                print e.value
                exit(1)

class TransmitProcessor(Processor):
    def __init__(self, transmit_handler):
        super(TransmitProcessor, self).__init__("transmit")
        self.transmit_handler = transmit_handler

    def process(self, packet, bit_offset=0):
        buf = packet.packet_data
        logging.info("Packet {} result: {}".format(packet.idx, hexify(buf)))
        logging.info("----- ----- ----- ----- ----- ----- ----- -----")
        self.transmit_handler(1, packet.packet_data)
