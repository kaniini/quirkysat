"""
    quirkysat.clause
    ~~~~~~~~~~~~~~~~

    This module implements a framework for composing clauses for a model, using functors.
    Clauses may have stateful data encapsulated in the functor constructor.  Creating functor-based
    clauses is best accomplished by deriving from the ``Clause`` class.

    There are also some helper classes which can be used to mutate the input and pass it to a sub-model.
    XXX: actually implement those
"""


class Clause:
    """Clauses are functors which return True/False given an input."""
    def __call__(self, data):
        raise NotImplementedError()

