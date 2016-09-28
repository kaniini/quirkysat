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

    Using weighting we can create models which have preferences:

    >>> from quirkysat.model import WeightedModel
    >>> wm = WeightedModel([
    ...    (lambda x: x > 1, 10),
    ...    (lambda x: x < 10, 10),
    ...    (lambda x: x % 2 == 0, 20)
    ... ], 20)
    ...
    >>> wm(2)
    True
    >>> wm(3)
    True
    >>> wm(11)
    False
    >>> wm(12)
    True
    >>> wm.score(11)
    10
    >>> wm.score(12)
    30

    ``SimpleModel`` is a variant of ``WeightedModel`` which assigns a value of 1 point
    for each clause, but otherwise works the same:

    >>> from quirkysat.model import SimpleModel
    >>> sm = SimpleModel([
    ...    lambda x: x > 1,
    ...    lambda x: x < 10,
    ...    lambda x: x % 2 == 0
    ... ], 2)
    ...
    >>> sm(2)
    True
    >>> sm(3)
    True
    >>> sm(11)
    False
    >>> sm(12)
    True
    >>> sm.score(11)
    1
    >>> sm.score(12)
    2
    >>> sm.score(6)
    3

    Finally, a model may accept multiple inputs.  As an example, we can create a model
    which verifies if three numbers are a valid pythagorean triple.

    >>> from quirkysat.model import AbsoluteModel
    >>> am = AbsoluteModel([
    ...    lambda a, b, c: (a * 2) + (b * 2) == (c * 2)
    ... ])
    ...
    >>> am(2, 3, 5)
    True
    >>> am(2, 3, 6)
    False
"""


class WeightedModel:
    def __init__(self, clauses, required_score=None):
        self._clauses = []

        [self.push_clause(clause[0], clause[1]) for clause in clauses]
        self.required_score = required_score
        if not self.required_score:
            self.required_score = sum([x[1] for x in self._clauses])

    def score(self, *args):
        score = 0

        for clause in self._clauses:
            score += clause[1] if clause[0](*args) else 0

        return score

    def __call__(self, *args):
        return self.score(*args) >= self.required_score

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

    def __call__(self, *args):
        for clause in self._clauses:
            if not clause[0](*args): return False

        return True


Model = SimpleModel


class AsyncWeightedModel(WeightedModel):
    @asyncio.coroutine
    def score(self, *args):
        score = 0

        results = yield from asyncio.gather(*[clause[0](*args) for clause in self._clauses])
        for clause, result in zip(self._clauses, results):
            score += clause[1] if result else 0

        return 0

    @asyncio.coroutine
    def __call__(self, *args):
        score = yield from self.score(*args)
        return score >= self.required_score


class AsyncSimpleModel(AsyncWeightedModel + SimpleModel):
    pass


class AsyncAbsoluteModel(AsyncSimpleModel + AbsoluteModel):
    @asyncio.coroutine
    def __call__(self, *args):
        for clause in self._clauses:
            result = yield from clause[0](*args)
            if not result: return False

        return True


AsyncModel = AsyncSimpleModel
