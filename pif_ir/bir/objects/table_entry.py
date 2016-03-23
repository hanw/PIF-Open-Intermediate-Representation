import logging

from pif_ir.meta_ir.common import meta_ir_valid_match_types as VALID_TYPES

class TableEntry(object):
    def __init__(self, type_, value, key, mask):
        self.type_ = type_
        self.value = value
        self.key = key
        self.mask = mask

    def check(self, request):
        if self.type_ == 'valid':
            return self._check_valid(request)
        elif self.type_ == 'exact':
            return self._check_exact(request)
        elif self.type_ == 'ternary':
            return self._check_ternary(request)
        elif self.type_ == 'lpm':
            return self._check_lpm(request)
        logging.warning("unknown TableEntry type")
        return False

    def _check_exact(self, request):
        for fld_name, value in self.key.items():
            if fld_name not in request.values:
                return False
            elif int(request.get_value(fld_name)) != int(value):
                return False
        return True

    def _apply_mask(self, fld_name, val):
        if self.mask == None or fld_name not in self.mask.keys():
            return int(val)
        return int(val) & int(self.mask[fld_name])

    def _check_ternary(self, request):
        for fld_name, value in self.key.items():
            if fld_name not in request.values:
                return False
            elif (self._apply_mask(fld_name, request.get_value(fld_name)) !=
                  self._apply_mask(fld_name, value)):
                return False
        return True

    def _check_valid(self, request):
        logging.warning("FIXME: implement TableEntry valid")
        return False
    def _check_lpm(self, request):
        logging.warning("FIXME: implement TableEntry lpm")
        return False
