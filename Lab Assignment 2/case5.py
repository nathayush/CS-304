from threading import Thread
import time
from barber import Barber
from customer import Customer
import createCustomers

class BarberShop:
    def __init__(self, N):
        self.queueSize = N
        self.queue = []
        self.totalCustomerCount = 0
        self.barber1 = Barber("Sweeny Todd")
        self.openShop()

    def openShop(self):
        print self.barber1.name + " has opened the Barber Shop."
        self.barber1.sleep()
        self.getCustomers("customerOrder.txt")

    def getCustomers(self, filename):
        with open(filename,'r') as openfileobject:
            for line in openfileobject:
                if line.rstrip() == "1":
                    try:
                        Thread(target = self.newCustomer, args=[]).start()
                    except:
                        print "Error0: unable to start thread"
                    time.sleep(1)
                else:
                    time.sleep(1)

    def newCustomer(self):
        self.totalCustomerCount += 1
        customer = Customer(self.totalCustomerCount)
        if self.barber1.sleeping:
            self.barber1.wakeup(customer)
            self.barber1.mutex.acquire()
            self.barber1.haircut(customer, customer.zipfTime(), self.queue)
            self.barber1.mutex.release()
        else:
            if self.barber1.busy:
                if len(self.queue) < self.queueSize:
                    self.queue.append(customer)
                    print self.barber1.name + " is busy, " + customer.name + " is waiting on chair " + str(self.queue.index(customer) + 1)
                    while self.queue.index(customer) != 0:
                        pass
                    self.barber1.mutex.acquire()
                    del self.queue[0]
                    self.broadcast()
                    self.barber1.haircut(customer, customer.zipfTime(), self.queue)
                    self.barber1.mutex.release()
                else:
                    print "Barbershop is full, " + customer.name + " has left."

    def broadcast(self):
        for i in self.queue:
            print i.name + " is sitting on chair " + str(self.queue.index(i) + 1)

# (number of customers, mod function)
createCustomers.main(7, 3)
# (number of regular chairs, haircut time)
shop = BarberShop(3)
