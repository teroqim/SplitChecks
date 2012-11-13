#! /usr/local/bin/python

#Documentation
"Program used to calculate who owns who how much money"

#Imports
import sys

#Globals

#Classes
class MenuItem:
    def __init__(self, id, description, action):
        self.id = id
        self.description = description
        self.action = action

#Functions
def printMenu(menuItems):
    print ""
    print "Menu:"
    for mi in menuItems:
        print str(mi.id) + ".", mi.description
    #print "1. Add payment"
    #print "2. List current participants"
    #print "3. Who owns what?"
    #print "4. Quit"
    print ""
    
def addPayment():
    print "payment"
    
def listParticipants():
    print "Participants"
    
def calcDepts():
    print "Depts"

def main():
    print "Welcome!"
    menuItems = [MenuItem(1, "Add payment", addPayment), MenuItem(2, "List participants", listParticipants), MenuItem(3, "Who owns what?", calcDepts), MenuItem(4, "Quit", sys.exit)]
    while True:
        printMenu(menuItems)
        print "Please enter your action (number): ",
        alt = raw_input()
        
        if alt.isdigit():
            for mi in menuItems:
                if mi.id == int(alt):
                    mi.action();
        else:
            print "Unrecognized alternative:", alt
    

#Main body
if __name__ == '__main__':
    main()
