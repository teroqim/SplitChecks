#! /usr/local/bin/python

#Documentation
"""Program used to calculate debts"""

#Imports
import sys
from debt_engine import DebtEngine, Check

#Globals
DEBT_GROUP = "group"

#Classes
class MenuItem(object):
    def __init__(self, description, action):
        self.description = description
        self.action = action

class ConsoleMenu(object):

    def __init__(self):
        self.items = list()
        self.engine = DebtEngine()

    def print_items(self):
        print ""
        print "Menu:"
        for i,item in enumerate(self.items):
            print str(i+1) + ".", item.description
        print ""

    def handle_action(self, alt):
        if alt < 1 or alt > len(self.items):
            raise ValueError('Index out-of-bounds')
        self.items[alt-1].action()

    def print_header(self, header):
        print '-'*20
        print header
        print '-'*20


class MainMenu(ConsoleMenu):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.items = [MenuItem("Add check", self.add_check),
                      MenuItem("List debts", self.list_debts),
                      MenuItem("Quit (everything will be lost..)", sys.exit)]

    def add_check(self):
        self.print_header("New check")

        #take in description
        description = raw_input("Describe check: ")

        #start new check
        check = Check(DEBT_GROUP, description)

        #add payers..
        print "Enter all payers"
        while True:
            input = raw_input("Please enter name and amount separated by a front slash (e.g. 'peter/20'): ")
            inputs = input.split('/')
            if len(inputs) != 2:
                continue
            try:
                check.add_payments((inputs[0].strip().lower(), float(inputs[1].strip())))
            except ValueError:
                continue
            ans = raw_input("Add another payer? (y/n): ")
            if ans != 'y':
                break

        #add sharers
        print ""
        print "Enter the names of everyone who should split the check. (The check is split evenly)"
        i = 1
        while True:
            input = raw_input("Name %2d: " % i)
            input = input.strip()
            if not input:
                continue
            check.add_sharers(input)
            i += 1
            ans = raw_input("Add another sharer? (y/n): ")
            if ans != "y":
                break

        #Add check to debt group
        self.engine.add_checks(check)
        print "Check added."


    def list_debts(self):
        self.print_header("Debts")

        for debt in self.engine.get_debts(DEBT_GROUP):
            print "%s\t->\t%s: %.2f " % (debt.nameFrom, debt.nameTo, debt.sum)

#Functions
def main():
    print "Welcome!"
    menu = MainMenu()
    while True:
        menu.print_items()

        print "Please enter your action (number): ",

        alt = raw_input()
        try:
            menu.handle_action(int(alt))
        except ValueError:
            print "Invalid action."



#Main body
if __name__ == '__main__':
    main()
