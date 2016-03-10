"""
BIR exception definitions
"""

class BIRError(Exception):
    """ a base class for all bir exceptions
    """
    def __init__(self, msg="BIR Error!"):
        self.value = msg

class BIRYamlAttrError(BIRError):
    """ YAML file is missing a required attribute
    """
    def __init__(self, attr, obj):
        super(BIRYamlAttrError, self).__init__()
        self.value = "missing required attribute({}) for object({})".format(
            attr, obj)

class BIRRefError(BIRError):
    """ reference to BIR object that doesn't exist
    """
    def __init__(self, ref, obj):
        super(BIRRefError, self).__init__()
        self.value = "bad reference({}) in object({})".format(ref, obj)

class BIRFieldWidthError(BIRError):
    """ bad field width
    """
    def __init__(self, width, field):
        super(BIRFieldWidthError, self).__init__()
        self.value = "bad width({}) for field({})".format(width, field)

class BIRTableTypeError(BIRError):
    """ table's match type is not supported
    """
    def __init__(self, name):
        super(BIRTableTypeError, self).__init__()
        self.value = "unsupported table type for table({})".format(name)

class BIRTableEntryError(BIRError):
    """ an entry couldn't be added to table
    """
    def __init__(self, name):
        super(BIRTableEntryError, self).__init__()
        self.value = "bad entry to table({})".format(name)

class BIRControlStateError(BIRError):
    """ incorrectly formatted ControlState object
    """
    def __init__(self, obj_name, msg):
        super(BIRControlStateError, self).__init__()
        self.value = "object({}): {}".format(obj_name, msg)

class BIRInstructionError(BIRError):
    """ incorrectly formatted Instruction object
    """
    def __init__(self, obj_name, msg):
        super(BIRInstructionListError, self).__init__()
        self.value = "object({}}: {}".format(obj_name, msg)

class BIRParsingError(BIRError):
    """ something went wrong while parsing an instruction or control state
    """
    def __init__(self, msg):
        super(BIRParsingError, self).__init__()
        self.value = msg
    
