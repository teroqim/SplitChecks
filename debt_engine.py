#Documentation
"""
SplitCheck engine.
Add checks to system, print out resulting debts and so on.
This module will be split into several modules when it gets clearer
which areas there are of the problem.
"""

#Imports

#Classes

class Check(object):
    """
    Represents a payment for some check. It has information about who paid what and which people should share it.

    Example usage:
    payment = Payment('myGroup')
    payment.add_payments(('alice', 100.0), ('bob', 100.0))
    payment.add_sharers('alice', 'bob', 'cecil')

    """
    def __init__(self, debt_group_id, description = ''):
        if not debt_group_id:
            raise ValueError('Must give group id')

        self.debt_group_id = debt_group_id
        self.description = description
        self.payments = dict()
        self.sharers = set()

    def add_payments(self, *payments):
        """
        Adds payments for the check.

        Each payment should be a tuple in the format (name, sum).

        Note: Duplicate payments for the same person are just added to the payer's total sum.
        Names are case-insensitive.
        """
        for n, s in payments:
            self.payments.setdefault(n.lower(), float(0.0))
            self.payments[n] += float(s)

    def add_sharers(self, *names):
        self.sharers.update(names)

class Debt(object):
    def __init__(self, nameFrom, nameTo, sum):
        self.nameFrom = nameFrom
        self.nameTo = nameTo
        self.sum = sum

class DebtGroup(object):
    """
    A group of checks to be split among a group of people. This class calculates and keeps track of debts.

    Right now the model is simply a directed graph with debts as edge values.
    The graph is stored in an adjacency list.
    """
    def __init__(self, debt_group_id):
        self.debt_group_id = debt_group_id

        #This is the graph of persons (adjacency list)
        self.debts = dict()

        #A list of all checks added
        self.checks = list()

    def add_check(self, check):
        """
        Add a check to the group and updates debts.
        If performance hits are discovered this method should probably be looked over,
        but right now it seems unnecessary due to small groups.
        """
        self.checks.append(check)
        self.__add_debts_from_check_to_graph(check)

    def get_normalized_debts(self):
        """
        Normalized means positive in this case, so edges with negative values are turned around.
        """
        '''
        NOTE:
        Implemented as generator, but if several iterations are needed it might be better to wrap this generator in
        a class and return instances of that class through an __iter__ method
        '''
        for edge, debt in self.debts.items():
            if debt < 0:
                yield Debt(edge[1], edge[0], -debt)
            else:
                yield Debt(edge[0], edge[1], debt)

    def __add_debts_from_check_to_graph(self, check):
        """
            Algorithm as follows:
            For each check:
                * Calculate each sharers share (in money)
                * Reduce the intersection of payers and sharers:
                    For each payer in intersection:
                        if payers sum > sharers share
                            remove sharer and set payer's sum -= sharers share
                        else
                            remove payer and set sharers sum -= payers sum
                            if sharers sum == 0
                                remove sharer
                * Add debts to graph for each sharer towards each payer. The amount is the sharers current
                  total share (in percent) times the payers sum
        """
        #Calculate sharers debts.
        #At present, the entire check is split equally, but that assumption is subject to change in future versions.
        total_sum = sum(check.payments.values())
        equal_share = total_sum / len(check.sharers)

        #Copy payers and sharer (might be a performance hit if the lists are large.. but we assume they aren't..
        payers = dict(check.payments)
        sharers = dict((name, equal_share) for name in check.sharers)

        #Reduce intersection
        self.__reduce_intersection(payers, sharers)

        #sanity check
        payer_sum = sum (payers[n] for n in payers)
        sharer_sum = sum(sharers[n] for n in sharers)
        assert round(payer_sum, 3) == round(sharer_sum, 3), "ps: %f, ss: %f" % (payer_sum, sharer_sum)

        #Add debts to graph
        for n in sharers:
            percent_share = sharers[n] / sharer_sum
            for pn in payers:
                self.__update_edge(n,pn,payers[pn] * percent_share)

    def __reduce_intersection(self, payers, sharers):
        for n in set(payers).intersection(sharers):
            if payers[n] < sharers[n]:
                #reduce sharer value
                sharers[n] -= payers[n]
                assert(sharers[n] > float(0.0))
                #remove payer
                payers.pop(n)
            else:
                #reduce payer
                payers[n] -= sharers[n]
                assert(payers[n] >= float(0.0))
                #remove sharer
                sharers.pop(n)
                #remove payer if sum is 0
                if payers[n] == float(0.0):
                    payers.pop(n)

    def __update_edge(self, name1, name2, debt):
        """
        Updates the edge between name1 and name2 with debt from name1 to name2

        debts must be a positive number
        """
        '''
        NOTE:
        Edge are directed, but allow negative values that represent a debt in the opposite direction.
        If there is an edge from name2 to name1 then 'debt' is decreased from the value on that edge.
        An edge that end up with a value of 0 after updating represent a settled debt and is therefore removed.
        '''
        if debt <= float(0.0):
            raise ValueError('debt must be positive')
        inc_debt = debt
        n1 = name1
        n2 = name2
        if (n2,n1) in self.debts:
            tmp = n2
            n2 = n1
            n1 = tmp
            inc_debt *= -1

        self.debts.setdefault((n1,n2), float(0.0))
        self.debts[(n1, n2)] += inc_debt
        if self.debts[n1, n2] == float(0.0):
            self.debts.pop((n1, n2))

class DebtEngine(object):
    def __init__(self):
        #Temporarily represents db..
        self.debt_groups = dict()

    def add_checks(self, *checks):
        """
        Adds payments to system.

        Keyword arguments:
        checks -- list of payments that should be added to the system

        """
        for check in checks:
            #Fetch or create check group and add check to it
            self.debt_groups.setdefault(check.debt_group_id,
                                                    DebtGroup(check.debt_group_id)).add_check(check)


    def get_debts(self, debt_group_id):
        if not debt_group_id:
            raise ValueError('Must set group id')
        #Fetch group data
        group = self.debt_groups.setdefault(debt_group_id, DebtGroup(debt_group_id))

        return group.get_normalized_debts()


#Functions
DEBT_GROUP = "group"
def __print_debts(engine, group):
    for debt in engine.get_debts(group):
        print "%s\t->\t%s: %.2f " % (debt.nameFrom, debt.nameTo, debt.sum)

def test1():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',10), ('j', 15))
    check.add_sharers('p', 'j')

    engine = DebtEngine()
    engine.add_checks(check)

    debt = engine.get_debts(DEBT_GROUP).next()
    assert(debt.nameFrom == 'p')
    assert(debt.nameTo == 'j')
    assert(debt.sum == float(2.5))

def test2():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',100))
    check.add_sharers('p', 'j')

    engine = DebtEngine()
    engine.add_checks(check)

    debt = engine.get_debts(DEBT_GROUP).next()
    assert debt.nameFrom == 'j'
    assert debt.nameTo == 'p'
    assert debt.sum == float(50), "Received value: %f" % debt.sum

def test3():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',10), ('j', 10))
    check.add_sharers('p', 'j', 'f')

    engine = DebtEngine()
    engine.add_checks(check)

    #__print_debts(engine, DEBT_GROUP)
    #Assertions here..

def test4():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',10), ('j', 20))
    check.add_sharers('p')

    engine = DebtEngine()
    engine.add_checks(check)

    #__print_debts(engine, DEBT_GROUP)
    #Assertions here..

def test5():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',10), ('j', 12))
    check.add_sharers('f','r')

    engine = DebtEngine()
    engine.add_checks(check)

    #__print_debts(engine, DEBT_GROUP)
    #Assertions here..

def test6():

    check = Check(DEBT_GROUP)
    check.add_payments(('p',120))
    check.add_sharers('f','r','j')

    engine = DebtEngine()
    engine.add_checks(check)

    __print_debts(engine, DEBT_GROUP)
    #Assertions here..

#Main body
if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()