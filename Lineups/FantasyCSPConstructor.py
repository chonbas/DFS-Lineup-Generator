from LineupDB import LineupDB
from CSP import CSP
from collections import OrderedDict

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
LINEUP = [2, 3, 1, 1, 1, 1]
MAX_SALARY = 60000


class FantasyCSPConstructor():

    def __init__(self, verbose=True, week=10, year=2016):
        """
        Saves the necessary data.

        @param verbose: decide if print information.
        @param week, year: what data to use CSP on.
        """
        self.db = LineupDB(week=week, year=year)
        self.positions = []
        for i, pos in enumerate(POSITIONS):
            for j in range(LINEUP[i]):
                self.positions.append((pos, j))
        self.verbose = verbose

    def add_variables(self, csp):
        """
        

        @param csp: The CSP where the additional constraints will be added to.
        """
        if self.verbose:
            print "---------------- Adding variables --------------------\n"
        for i, pos in enumerate(POSITIONS):
            for j in range(LINEUP[i]):
                variables = [(name, self.db.data[pos][name][self.db.salary]) for name in self.db.data[pos].keys()]

                if self.verbose:
                    print "adding variable ", (pos, j), variables, "... "
                csp.add_variable((pos, j), variables)
                if self.verbose:
                    print " done\n"

    def add_norepeating_contraint(self, csp):
        if self.verbose:
            print "---------------- Adding norepeating contraint --------------------\n"
        for pos1 in self.positions:
            for pos2 in self.positions:
                if pos1 == pos2:
                    continue
                csp.add_binary_factor(pos1, pos2, \
                        lambda (name1, sal1), (name2, sal2): name1 != name2) #and \
                         # (sal1 >= sal2 if pos1[1] < pos2[1] else sal2 >= sal1))

    #add ordering constraint only for players in same role
    def add_ordering_contraint(self, csp):
        if self.verbose:
            print "---------------- Adding ordering contraint --------------------\n"
        for i, pos in enumerate(POSITIONS):
            for j in range(LINEUP[i]):
                for k in range(j + 1, LINEUP[i]):
                    csp.add_binary_factor((pos, j), (pos,k), \
                        lambda player1, player2: player1 >= player2 )

    def add_request_weights(self, csp):
        if self.verbose:
            print "---------------- Adding weights --------------------\n"
        for pos in self.positions:
            if self.verbose:
                print "adding factor ", pos
            csp.add_unary_factor(pos, lambda (name, sal): pow(2.0,self.db.data[pos[0]][name][self.db.pts]))

    def add_salary_constraint(self, csp):
        if self.verbose:
            print "---------------- Adding salary contraint --------------------\n"
        min_salaries = OrderedDict() 
        max_salaries = OrderedDict()
        for (pos, j) in self.positions:
            salary = [self.db.data[pos][name][self.db.salary] for name in self.db.data[pos].keys()]
            # salary = list(set(salary)) #to remove duplicates
            if self.verbose:
                print "Adding salary constaint for ", (pos, j), ": ", salary, "..."
            min_salaries[(pos, j)] = min(salary)
            max_salaries[(pos, j)] = max(salary)
            if self.verbose:
                print "... done\n"
        csp.set_legal_sum(MAX_SALARY, min_salaries, max_salaries)



    def get_csp(self):
        csp = CSP()
        self.add_variables(csp)
        self.add_norepeating_contraint(csp)
        self.add_ordering_contraint(csp)
        self.add_request_weights(csp)
        self.add_salary_constraint(csp)
        if self.verbose:
            print "-------------------- Done constructing csp -------------------"
        return csp



    def print_players(self, players):
        totalPts = 0
        totalSalary = 0
        for (pos, j) in players.keys():
            (name, salary) = players[(pos,j)]
            print name, "\t", pos, "\t", self.db.data[pos][name], "\n"
            totalPts += self.db.data[pos][name][self.db.pts]
            totalSalary += self.db.data[pos][name][self.db.salary]
        print "total points expected: ", totalPts
        print "total salary used: ", totalSalary






