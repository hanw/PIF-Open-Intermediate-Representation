import logging
from collections import OrderedDict

from pif_ir.bir.objects.bir_exception import *
from pif_ir.bir.objects.bir_validate import check_attributes
from pif_ir.bir.objects.metadata_instance import MetadataInstance

class Table(object):
    required_attributes = ['match_type', 'depth', 'request', 'response',
                           'operations']

    def __init__(self, name, table_attrs):
        check_attributes(name, table_attrs, Table.required_attributes)
        logging.debug("Adding table {0}".format(name)) 

        # TODO: support types in meta_ir.common.meta_ir_valid_match_types
        if table_attrs['match_type'] != 'exact':
            raise BIRTableTypeError(name)

        self.name = name
        self.match_type = table_attrs['match_type']
        self.depth = table_attrs['depth']
        # FIXME: unused, but could be used for type checking?
        self.req_attrs = {'type':'metadata', 'values':table_attrs['request']}
        self.resp_attrs = {'type':'metadata', 'values':table_attrs['response']}
        self.operations = table_attrs.get('operations', None )
        
        # The list of table entries
        self.entries = []

    def add_entry(self, entry):
        if entry.match_type != self.match_type:
            raise BIRTableEntryError(self.name)
        logging.debug("Adding entry to {0}".format(self.name))
        self.entries.append(entry)

    def remove_entry(self, entry):
        pass    # TODO:

    def clear(self, entry):
        self.entries = []

    def _handle_hit(self, metadata, table_entry):
        logging.info("Table Match")
        for fld, val in table_entry.value.items():
            if fld in metadata.values.keys():
                metadata.set_value(fld, val)    
            else:
                logging.error("table hit invalid field({})".format(fld))

    def lookup(self, request, response):
        for ent in self.entries:
            if ent.check(request):
                self._handle_hit(response, ent)
