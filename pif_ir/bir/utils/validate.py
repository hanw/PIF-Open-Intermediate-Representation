from pif_ir.bir.utils.exceptions import *

def check_attributes(obj_name, attributes, required_attributes):
    for attr in required_attributes:
        if attr not in attributes:
            raise BIRYamlAttrError(attr, obj_name)
