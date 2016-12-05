import json, re
import collections, copy, math

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0
        self.optimalPts = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        if self.csp.sumVariable: #csp has sum variable with own function
            if not self.csp.is_temp_sum_reasonable(assignment, var, val):
                return 0
        return w


    

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that we want search to be terminated when one CSP is found,
        (since there are many poor solutions available), and we want to make sure
        this is the best solution. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        # self.print_stats()
        # print "players: ", self.optimalAssignment
        return self.optimalAssignment



    def get_salary(self, assignment):
        return sum([salary for (name, salary) in assignment.values()])

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        # if self.numOperations >= 1000000:
        #     return
        
        self.numOperations += 1
        # if self.numOperations % 1000 == 0:
        #     print "progress: ", self.numOperations, self.numAssignments
        assert weight > 0
        if numAssigned == self.csp.numVars:
            if weight >= self.optimalWeight * .9:
                
                # A satisfiable, good enough solution have been found. Update the statistics.
                self.numAssignments += 1
                newAssignment = {}
                for var in self.csp.variables:
                    newAssignment[var] = assignment[var]
                self.allAssignments.append(newAssignment)

                # print self.get_salary(assignment)
                # print "\n Found assignment: ", weight,  self.optimalWeight, \
                #         math.log(weight,2), self.optimalPts, newAssignment
            
                if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                    if weight == self.optimalWeight:
                        self.numOptimalAssignments += 1
                    else:
                        self.numOptimalAssignments = 1
                    self.optimalWeight = weight
                    self.optimalPts = math.log(weight,2)

                    self.optimalAssignment = newAssignment
                    if self.firstAssignmentNumOperations == 0:
                        self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        if var == None:
            return
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            mcv = None
            minValues = None
            for var in self.csp.variables:
                if var not in assignment:
                    numValues = 0
                    for val in self.domains[var]:
                        if self.get_delta_weight(assignment, var, val) > 0:
                            numValues += 1
                    if minValues == None or numValues < minValues:
                        mcv = var
                        minValues = numValues
            return mcv

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        toUpdate = [var]
        while len(toUpdate) > 0:
            var1 = toUpdate.pop(0)
            domain1 = []
            for val1 in self.domains[var1]:
                if not (self.csp.unaryFactors[var1] and self.csp.unaryFactors[var1][val1] == 0):
                    domain1.append(val1)
                    val1_works_so_far = True
            self.domains[var1] = domain1
            for var2 in self.csp.get_neighbor_vars(var1):
                domain2 = []
                for val2 in self.domains[var2]:
                    for val1 in domain1:
                        if not (self.csp.binaryFactors[var1] and self.csp.binaryFactors[var1][var2] and \
                            self.csp.binaryFactors[var1][var2][val1][val2] == 0):
                            domain2.append(val2)
                            break
                if self.domains[var2] != domain2:
                    toUpdate.append(var2)
                    self.domains[var2] = domain2



