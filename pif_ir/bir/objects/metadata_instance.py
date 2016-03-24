import logging
from collections import OrderedDict

from pif_ir.bir.objects.value_instance import ValueInstance
from pif_ir.bir.utils.validate import check_attributes

class MetadataInstance(object):
    required_attributes = ['values', 'visibility']

    def __init__(self, name, metadata_attrs, bir_structs, buf=None, 
                 bit_offset=0):
        check_attributes(name, metadata_attrs, 
                         MetadataInstance.required_attributes)

        logging.debug("Adding metadata {0}".format(name))
        self.name = name
        self.values = OrderedDict()
        # FIXME: used for syntactic checking
        self.visibility = metadata_attrs['visibility']

        struct_name = metadata_attrs['values']
        for f_name, f_size in bir_structs[struct_name].fields.items():
            self.values[f_name] = ValueInstance(f_name, f_size)

        if buf:
            self.extract(buf, bit_offset)

    def __len__(self):
        return sum([len(fld) for fld in self.values.values()])

    def __int__(self):
        value = 0;
        for fld in self.values.values():
            value = (value << len(fld)) + int(fld)
        return value

    def to_dict(self):
        return dict([(v.name,int(v)) for v in self.values.values()])

    def extract(self, buf, bit_offset=0):
        fld_offset = 0;
        for fld in self.values.values():
            fld.extract(buf, bit_offset + fld_offset);
            fld_offset += len(fld)

    def serialize(self):
        byte_list = bytearray(len(self)/8)
        bit_offset = 0;
        for fld in self.values.values():
            fld.update(byte_list, bit_offset)
            bit_offset += len(fld)
        return byte_list

    def get_value(self, value_name):
        if value_name not in  self.values:
            return 0
        return self.values[value_name].value

    def set_value(self, value_name, value):
        fld = self.values.get(value_name, None)
        if fld:
            fld.value = value

    def reset_values(self, new_val=0):
        for fld in self.values.values():
            fld.value = new_val

