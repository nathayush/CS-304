from threading import Thread
import time
from barber import Barber
from customer import Customer
import createCustomers

class BarberShop:
    def __init__(self, N, P = 0):
        self.haircutTime = P
        self.queueSize = N
        self.queue = []
        self.totalCustomerCount = 0
        self.barber1 = Barber("Sweeny Todd")
        self.barber2 = Barber("Davy Collins")
        self.freeBarbers = []
        self.openShop()

    def openShop(self):
        print self.barber1.name + " has opened the Barber Shop."
        self.barber1.sleep()
        self.freeBarbers.append(self.barber1)
        self.barber2.sleep()
        self.freeBarbers.append(self.barber2)
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
        if self.freeBarbers != []:
            barber = self.freeBarbers[0]
            barber.mutex.acquire()
            del self.freeBarbers[0]
            if barber.sleeping:
                barber.wakeup(customer)
            barber.haircut(customer, self.haircutTime, self.queue)
            self.freeBarbers.append(barber)
            barber.mutex.release()
        else:
            if len(self.queue) < self.queueSize:
                self.queue.append(customer)
                print "Barbers are busy, " + customer.name + " is waiting on chair " + str(self.queue.index(customer) + 1)
                while self.queue.index(customer) != 0:
                    pass
                while self.freeBarbers == []:
                    pass
                barber = self.freeBarbers[0]
                barber.mutex.acquire()
                del self.freeBarbers[0]
                del self.queue[0]
                self.broadcast()
                barber.haircut(customer, self.haircutTime, self.queue)
                self.freeBarbers.append(barber)
                barber.mutex.release()
            else:
                print "Barbershop is full, " + customer.name + " has left."

    def broadcast(self):
        for i in self.queue:
            print i.name + " is sitting on chair " + str(self.queue.index(i) + 1)

# (number of customers, mod function)
createCustomers.main(7, 3)
# (number of regular chairs, haircut time)
shop = BarberShop(3, 7)
