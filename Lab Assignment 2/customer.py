from random import randint
from numpy import random

class Customer:
    def __init__(self, num):
        self.name = "Customer " + str(num)
        print self.name + " has arrived."

    def haircutTime(self):
        i = int(randint(5, 25))
        return i

    def zipfTime(self):
        i = random.zipf(1.3)
        return i
