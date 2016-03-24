import logging
from threading import Condition

from pif_ir.bir.objects.processor import ThreadedProcessor

class TrafficManager(ThreadedProcessor):
    job_lock = Condition()

    def __init__(self):
        super(TrafficManager, self).__init__("TrafficManager")

        self.queues = []
        for port in range(10): # 10 queues
            self.queues.append([]) 

    def process(self, packet, bit_offset=0):
        job_queue = packet.idx % len(self.queues)

        TrafficManager.job_lock.acquire()
        self.queues[job_queue].append((packet, bit_offset))
        TrafficManager.job_lock.release()

    def run(self):
        active = 0
        while self.running:
            active = (active + 1) % len(self.queues)
            if len(self.queues[active]) < 1:
                continue

            TrafficManager.job_lock.acquire()
            packet, bit_offset = self.queues[job_queue].pop(0)
            TrafficManager.job_lock.release()

            if self.next_processor:
                self.next_processor.process(packet, bit_offset)
