"""
    quirkysat.model
    ~~~~~~~~~~~~~~~

    This module actually implements a functor object that when called tests an input against a set of boolean conditions
    for satisfiability.

    Tests can be in the form of:
      - a function
      - a lambda expression
      - a Clause functor (see ``quirkysat.clause``)

    A basic example with only lambdas:

    >>> from quirkysat.model import AbsoluteModel
    >>> am = AbsoluteModel([
    ...    lambda x: x > 1,
    ...    lambda x: x < 3
    ... ])
    >>> am(1)
    False
    >>> am(3)
    False
    >>> am(2)
    True

    A basic example with a custom test functor:

    >>> from quirkysat.model import AbsoluteModel
    >>> from quirkysat.clause import Clause
    >>> class FibonacciClause(Clause):
    ...     prev = [0, 1]
    ...     def __call__(self, data):
    ...         next = self.prev[1] + self.prev.pop(0)
    ...         self.prev += [next]
    ...         return data == next
    ...
    >>> am = AbsoluteModel([FibonacciClause()])
    >>> am(1)
    True
    >>> am(2)
    True
    >>> am(3)
    True
    >>> am(5)
    True
    >>> am(6)
    False
    >>> am(13)
    True
"""


class WeightedModel:
    def __init__(self, clauses, required_score=None):
        self._clauses = []

        [self.push_clause(clause, weight) for clause in clauses]
        self.required_score = required_score
        if not self.required_score:
            self.required_score = sum([x[1] for x in self._clauses])

    def __call__(self, data):
        required_score = self.required_score
        score = 0

        for clause in self._clauses:
            score += clause[1] if clause[0](data) else 0

        return score >= required_score

    def push_clause(self, clause, weight=1):
        self._clauses += [(clause, weight)]


class SimpleModel(WeightedModel):
    def __init__(self, clauses, required_score=None):
        self._clauses = []

        [self.push_clause(clause) for clause in clauses]
        maximum_score = len(clauses)

        self.required_score = required_score
        if not self.required_score:
            self.required_score = maximum_clauses

        if self.required_score > len(clauses):
            self.required_score = maximum_clauses


class AbsoluteModel(SimpleModel):
    def __init__(self, clauses):
        super().__init__(clauses, required_score=len(clauses))

    def __call__(self, data):
        for clause in self._clauses:
            if not clause[0](data): return False

        return True


Model = SimpleModel
