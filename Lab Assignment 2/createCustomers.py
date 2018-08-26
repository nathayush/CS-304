from random import randint
import sys

def main(num, mod):
    def generate(num, mod):
        count = 0
        with open("customerOrder.txt",'w') as file1:
            while count != num:
                output = function(mod)
                if output == 0:
                    count += 1
                    file1.write("1\n")
                else:
                    file1.write("0\n")

    def function(mod):
        i = int(randint(100000, sys.maxsize))
        return i % mod

    generate(num, mod)
