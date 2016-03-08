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
from pif_ir.bir.objects import table_entry
from pif_ir.bir.objects.basic_block import BasicBlock
from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.control_flow import ControlFlow
from pif_ir.bir.objects.metadata_instance import MetadataInstance
#from pif_ir.bir.objects.other_processor import OtherProcessor
from pif_ir.bir.objects.packet_instance import PacketInstance
from pif_ir.bir.objects.processor import Processor
from pif_ir.bir.objects.table import Table
from pif_ir.bir.utils.exceptions import BIRError
from pif_ir.bir.utils.instruction_parser import InstructionParser
from pif_ir.bir.utils.ncs_parser import NCSParser

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
        self.transmit_handler = transmit_handler
        self.transmit_processor = TransmitProcessor(transmit_handler)

        self.disabled = True
        self.op_started = False

        # create parsers to handle next_control_states, and the
        # F instructions
        ncs_parser = NCSParser()
        inst_parser = InstructionParser()

        # BIR objects
        self.bir_structs = {}
        self.bir_tables = {}
        self.bir_other_modules = {}
        self.bir_basic_blocks = {}
        self.bir_control_flows = {}
        self.processors = []
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
                                                     ncs_parser, 
                                                     inst_parser)
        for name, val in self.control_flow.items():
            self.bir_control_flows[name] = ControlFlow(name, val,
                                                       self.bir_basic_blocks)
        
        # BIR processor layout
        for layout in self.processor_layout.values():
            if layout['format'] != 'list':
                logging.error("usupported layout format")
                exit(1)
            self.processors = layout['implementation']

        # Table initialization is part of the YAML until an API can be 
        # created
        ext_objs = self.external_object_map
        if 'table_initialization' in ext_objs.keys():
            self.table_init = ext_objs['table_initialization']

    def _load_module(self, name, operation):
        module_name = "pif_ir.bir.objects.other_module.{}".format(name)
        other_module = import_module(module_name)
        return getattr(other_module, operation)

    def process_table_init(self):
        for init_entry in self.table_init:
            for table_name, entry_desc in init_entry.items():
                ent = table_entry.TableEntryExact(entry_desc['key'],
                                                  entry_desc['value'])
                self.bir_tables[table_name].add_entry(ent)

    def enable(self):
        """
        @brief Enable the switch instance

        Start the other processor threads and allow packets to enter
        the processor chain
        """
        #if not self.op_started:
        #    for name, op in self.bir_other_processor.items():
        #        logging.debug("Starting OP %s" % name)
        #        op.start()
        #    op_started = True

        logging.debug("Enabling switch %s" % self.name)
        self.disabled = False

    def disable(self):
        """
        @brief Disable the switch instance
        Packets on ingress are discarded while the switch is disabled.
        Other processor threads are not stopped.
        """
        logging.debug("Disabling switch %s" % self.name)
        self.disabled = True

#    def kill(self):
#        """
#        """
#        if self.op_started:
#            for name, op in self.bir_other_processor.items():
#                logging.debug("Stopping OP %s" % name)
#                op.kill()
#                op.join()

    def process_packet(self, in_port, packet_data):
        if self.disabled:
            logging.debug("Switch is disabled; discarding packet")
        else:
            buf = bytearray(packet_data)
            packet = PacketInstance(buf, self.metadata, self.bir_structs)
            logging.info("Packet {} start: {}".format(packet.idx, hexify(buf)))

            for control_flow in self.processors:
                try:
                    self.bir_control_flows[control_flow].process(packet)
                except BIRError as e:
                    print e.value
                    exit(1)

            buf = packet.packet_data
            logging.info("Packet {} result: {}".format(packet.idx, 
                                                       hexify(buf)))
            logging.info("----- ----- ----- ----- ----- ----- ----- -----")

class TransmitProcessor(Processor):
    """
    @brief Wrapper class to connect processing with transmitting packets
    @param transmit_handler A function that knows how to send a packet to a port
    """
    def __init__(self, transmit_handler):
        self.transmit_handler = transmit_handler
        self.name = "transmit_processor"

    def process(self, packet):
        """
        @brief Process interface that sends a packet
        @param packet The packet instance to transmit
        """
        packet_data = packet.packet_data
        out_port= packet.get_field("intrinsic_metadata.egress_port")

        logging.debug("Transmit pkt id %d to %d" % (packet.id, out_port))
        buf = bytearray(packet_data)
        logging.debug(hexify(buf))
        self.transmit_handler(out_port, packet_data)

