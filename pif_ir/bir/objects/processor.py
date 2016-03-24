from threading import Thread

from pif_ir.bir.utils.exceptions import BIRError

class Processor(object):
    def __init__(self, name, next_processor=None):
        self.name = name
        self.next_processor = next_processor

    def process(self, packet, bit_offset=0):
        msg = "Processor {}: does not implement process()".format(self.name)
        raise BIRError(msg)

class ThreadedProcessor(Thread, Processor):
    def __init__(self, name, next_processor=None):
        Thread.__init__(self)
        Processor.__init__(self, name, next_processor)
        self.running = True

    def run(self):
        msg = "Processor {}: does not implement run()".format(self.name)
        raise BIRError(msg)

    def kill(self):
        self.running = False

