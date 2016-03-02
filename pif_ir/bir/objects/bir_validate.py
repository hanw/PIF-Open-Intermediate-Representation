from pif_ir.bir.objects.bir_exception import *

def check_attributes(obj_name, attributes, required_attributes):
    for attr in required_attributes:
        if attr not in attributes:
            raise BIRYamlAttrError(attr, obj_name)
