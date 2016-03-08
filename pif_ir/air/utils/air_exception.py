"""
AIR exception definitions
"""

class AirParamError(Exception):
    """
    Error validating some MetaIR representation
    """
    pass

class AirPacketModError(Exception):
    """
    Error during some packet modification
    Examples:
      A header didn't exist that should, 
      A header existed on add
      A header stack overflowed
      Incompatible field value assignment
    """
    pass

class AirReferenceError(Exception):
    """
    Error refencing some AIR object
    """
    pass

class AirImplementationError(Exception):
    """
    Implementation error in AIR; for example, uninstantiated pure
    virtual function.
    """
    pass
