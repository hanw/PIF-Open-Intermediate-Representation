import logging

class TableEntryExact(object):
    def __init__(self, key, value):
        """
        @param key_values: A list of value Instances
        @param value_resp: A bytearray buffer
        """
        self.match_type = 'exact'
        self.key = key
        self.value = value

    def check(self, request):
        for fld_name, value in self.key.items():
            if fld_name not in request.values:
                return False
            elif int(request.get_value(fld_name)) != int(value):
                return False
        return True
