import time
from threading import Lock, Thread
from customer import Customer

class Barber(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.sleeping = True
        self.busy = False
        self.mutex = Lock()

    def wakeup(self, customer):
        print customer.name + " has woken up " + self.name + "."
        self.sleeping = False

    def haircut(self, customer, haircutTime, queue):
        self.busy = True
        try:
            print customer.name + " is sitting in the barber chair."
            print self.name + " is cutting " + customer.name + "'s hair. (" + str(haircutTime) + " secs)"
            time.sleep(haircutTime)
            print customer.name + "'s haircut is complete."
        finally:
            self.busy = False
        if queue == []:
            self.sleep()

    def sleep(self):
        self.sleeping = True
        print self.name + " is sleeping."
