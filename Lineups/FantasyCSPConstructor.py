from LineupDB import LineupDB
import utilCSP

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
LINEUP = [2, 3, 1, 1, 1, 1]
MAX_SALARY = 60000
db = LineupDB(hashable=True)


class FantasyCSPConstructor():

    def __init__(self, verbose=True):
        """
        Saves the necessary data.

        @param bulletin: Stanford Bulletin that provides a list of courses
        @param profile: A student's profile and requests
        """
        # self.bulletin = bulletin
        # self.profile = profile
        #self.db = LineupDB(hashable=True)
        self.positions = []
        for i, pos in enumerate(POSITIONS):
            for i in range(LINEUP[i]):
                self.positions.append((pos, i))
        self.verbose = verbose

    def add_variables(self, csp):
        """
        

        @param csp: The CSP where the additional constraints will be added to.
        """
        if self.verbose:
            print "---------------- Adding variables --------------------\n"
        for i, pos in enumerate(POSITIONS):
            for i in range(LINEUP[i]):
                csp.add_variable((pos, i), db.data[pos].keys())
                if self.verbose:
                    print "adding variable ", (pos, i), db.data[pos].keys(), "\n"

    def add_norepeating_contraint(self, csp):
        if self.verbose:
            print "---------------- Adding norepeating contraint --------------------\n"
        for pos1 in self.positions:
            for pos2 in self.positions:
                if pos1 == pos2:
                    continue
                csp.add_binary_factor(pos1, pos2, \
                        lambda name1, name2: name1 != name2)

    def add_request_weights(self, csp):
        if self.verbose:
            print "---------------- Adding weights --------------------\n"
        for pos in self.positions:
            if self.verbose:
                print "adding factor ", pos, " \n"
            csp.add_unary_factor(pos, lambda name: db.data[pos[0]][name][db.pts])

    def add_salary_constraint(self, csp):
        if self.verbose:
            print "---------------- Adding salary contraint --------------------\n"
        salaries = []
        for pos in self.positions:

            domain = []
            if self.verbose:
                print "adding players: ", db.data[pos[0]].keys()
            for player in db.data[pos[0]].keys():
                salary = (db.data[pos[0]][player][db.salary]) / 1000
                if salary not in domain:
                    domain.append(salary)

            csp.add_variable(("salary", pos), domain)
            salaries.append(("salary", pos))
            csp.add_binary_factor(("salary", pos), pos, lambda salary, player: \
                salary == int(db.data[pos[0]][player][db.salary]/1000)  )
            if self.verbose:
                print "adding variable ", salaries[len(salaries)-1], "\n"
        sum_var = utilCSP.get_sum_variable(csp, "total salary", salaries, int(MAX_SALARY/1000))



    def get_csp(self):
        csp = utilCSP.CSP()
        self.add_variables(csp)
        self.add_norepeating_contraint(csp)
        self.add_request_weights(csp)
        self.add_salary_constraint(csp)
        if self.verbose:
            print "-------------------- Done constructing csp -------------------"
        return csp



    def print_players(self, players):
        totalPts = 0
        totalSalary = 0
        for pos, name in players:
            print name, "\t", pos, "\t", db.data[pos][name], "\n"
            totalPts += db.data[pos][name][db.pts]
            totalSalary += db.data[pos][name][db.salary]
        print "total points expected: ", totalPts
        print "total salary used: ", totalSalary






