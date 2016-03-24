import logging
from collections import OrderedDict

from pif_ir.bir.objects.metadata_instance import MetadataInstance
from pif_ir.bir.objects.table_entry import TableEntry
from pif_ir.bir.utils.exceptions import BIRTableEntryError
from pif_ir.bir.utils.validate import check_attributes

class Table(object):
    required_attributes = ['match_type', 'depth', 'request', 'response',
                           'operations']

    def __init__(self, name, table_attrs):
        check_attributes(name, table_attrs, Table.required_attributes)
        logging.debug("Adding table {0}".format(name)) 

        self.name = name
        self.match_type = table_attrs['match_type']
        self.depth = table_attrs['depth']
        # FIXME: unused, but could be used for type checking?
        self.req_attrs = {'type':'metadata', 'values':table_attrs['request']}
        self.resp_attrs = {'type':'metadata', 'values':table_attrs['response']}
        self.operations = table_attrs.get('operations', None )
        
        # The list of table entries
        self.entries = []

    def add_entry(self, *args):
        # accepted formats: add_entry(TableEntry)
        #                   add_entry(val_metadata, key_metadata)
        #                   add_entry(val_meta, key_meta, mask_meta)
        if len(args) == 1:
            entry = args[0]
        elif len(args) == 2:
            val = args[0].to_dict()
            key = args[1].to_dict()
            entry = TableEntry(self.match_type, val, key, None)
        elif len(args) == 3:
            val = args[0].to_dict()
            key = args[1].to_dict()
            mask = args[2].to_dict() if args[2] else None
            entry = TableEntry(self.match_type, val, key, mask)
        else:
            raise BIRTableEntryError(self.name, "bad table.add_entry() args")
        logging.debug("Adding entry to {0}".format(self.name))
        self.entries.append(entry)

    def remove_entry(self, key, mask):
        if isinstance(key, MetadataInstance):
            key = key.to_dict()
        if isinstance(mask, MetadataInstance):
            mask = mask.to_dict()
        for pos, ent in enumerate(self.entries):
            if ent.key != key:
                pass
            elif mask != None and ent.mask != mask:
                pass
            else:
                del self.entries[pos]

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
                return
