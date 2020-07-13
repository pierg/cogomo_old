from typing import Set, Union
from checks.nusmv import check_satisfiability, check_validity
from checks.tools import And, Implies, Not, Or
from typescogomo.variables import Variables, extract_variable


class LTL:

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['LTL'] = None,
                 skip_checks: bool = False):
        """Basic LTL formula.
        It can be build by a single formula (str) or by a conjunction of other LTL formulae (CNF form)"""

        if formula is not None and cnf is None:

            if variables is None:
                variables = extract_variable(str(formula))

            """String representing the LTL"""
            self.__formula: str = formula

            """Variables present in the formula"""
            self.__variables: Variables = variables

            """Set of LTL that conjoined result in the formula"""
            self.__cnf: Set['LTL'] = {self}

            if not skip_checks:
                if not self.is_satisfiable():
                    raise InconsistentException(self, self)

        elif cnf is not None and formula is None:

            cnf_str = [x.formula for x in cnf]

            self.__formula: str = And(cnf_str)

            self.__variables: Variables = Variables()

            for x in cnf:
                self.__variables |= x.variables

            self.__cnf: Set[Union['LTL']] = cnf

            if not skip_checks:
                if not self.is_satisfiable():
                    raise InconsistentException(self, self)

        elif cnf is None and formula is None:
            self.__formula: str = "TRUE"
            self.__cnf: Set['LTL'] = {self}
            self.__variables: Variables = Variables()

        else:
            raise Exception("Wrong parameters LTL construction")

    @property
    def formula(self) -> str:
        return self.__formula

    @property
    def variables(self) -> Variables:
        return self.__variables

    @property
    def cnf(self) -> Set['LTL']:
        return self.__cnf

    """Logic Operators"""

    def __iand__(self, other):
        """self &= other
        Modifies self with the conjunction with other"""
        if not isinstance(other, LTL):
            return AttributeError

        self.__formula = And([self.formula, other.formula])
        self.__variables = Variables(self.variables | other.variables)
        self.__cnf |= other.cnf

        if not self.is_satisfiable():
            raise InconsistentException(self, other)
        return self

    def __ior__(self, other):
        """self |= other
        Modifies self with the disjunction with other"""
        if not isinstance(other, LTL):
            return AttributeError

        self.__formula = Or([self.formula, other.formula])
        self.__variables = Variables(self.variables | other.variables)

        """TODO: maybe not needed"""
        if not self.is_satisfiable():
            raise InconsistentException(self, other)

        return self



    def __and__(self, other):
        """self & other
        Returns a new LTL with the conjunction with other"""
        if not isinstance(other, LTL):
            return AttributeError

        return LTL(cnf={self, other})

    def __or__(self, other):
        """self | other
        Returns a new LTL with the disjunction with other"""
        if not isinstance(other, LTL):
            return AttributeError

        formula = Or([self.formula, other.formula])
        variables = Variables(self.variables | other.variables)

        return LTL(formula=formula, variables=variables)


    """Refinement operators"""

    def __lt__(self, other: 'LTL'):
        """Check if the set of behaviours is smaller in the other set of behaviours"""
        lt = self <= other
        neq = self != other
        return lt and neq

    def __le__(self, other: 'LTL'):
        if other.is_true():
            return True
        """Check if the set of behaviours is smaller or equal in the other set of behaviours"""
        variables_a = set(self.variables.get_nusmv_names())
        variables_b = set(other.variables.get_nusmv_names())
        variables = variables_a | variables_b
        return check_validity(list(variables), "((" + self.formula + ") -> (" + other.formula + "))")

    def __eq__(self, other: 'LTL'):
        """Check if the set of behaviours is equal to the other set of behaviours"""
        if self.formula == other.formula:
            return True
        implied_a = self >= other
        implied_b = self <= other
        return implied_a and implied_b

    def __ne__(self, other: 'LTL'):
        """Check if the set of behaviours is different from the other set of behaviours"""
        return not (self == other)

    def __gt__(self, other: 'LTL'):
        """Check if the set of behaviours is bigger than the other set of behaviours"""
        gt = self >= other
        neq = self != other
        return gt and neq

    def __ge__(self, other: 'LTL'):
        if self.is_true():
            return True
        """Check if the set of behaviours is bigger of equal than the other set of behaviours"""
        variables_a = set(self.variables.get_nusmv_names())
        variables_b = set(other.variables.get_nusmv_names())
        variables = variables_a | variables_b
        return check_validity(list(variables), "((" + other.formula + ") -> (" + self.formula + "))")

    def __hash__(self):
        return hash(self.__formula)

    def copy(self):
        """Return a new LTL which is a copy of self"""
        return self & self

    def negate(self):
        """Modifies the LTL formula with its negation"""
        self.__formula = Not(self.formula)

    def remove(self, element):
        self.cnf.remove(element)
        self.__init__(cnf = self.cnf, skip_checks=True)

    def is_true(self):
        return self.formula == "TRUE"

    def is_satisfiable(self):
        if self.formula == "TRUE":
            return True
        if self.formula == "FALSE":
            return False
        return check_satisfiability(self.variables.get_nusmv_names(), self.formula)

    def is_satisfiable_with(self, other):
        try:
            self.__and__(other)
        except InconsistentException:
            return False
        return True

    def can_provide_for(self, other):
        """Check if the set of behaviours is smaller or equal in the other set of behaviours but on the types"""
        variables = self.variables | other.variables
        proposition = Implies(self.formula, other.formula)
        for v in variables:
            proposition = proposition.replace(v.name, v.port_type)
        return check_validity(variables.get_nusmv_types(), proposition)

    # def conjoin_with(self, others: Union['LTL', List['LTL']]) -> List['LTL']:
    #     """Returns list of LTL that have been successfully conjoined"""
    #     conjoined_formulae = []
    #     if isinstance(others, list):
    #         for other in others:
    #             if self.conjoin_with_formula(other):
    #                 conjoined_formulae.append(other)
    #     elif isinstance(others, LTL):
    #         if self.conjoin_with_formula(others):
    #             conjoined_formulae.append(others)
    #     else:
    #         Exception("Type error when conjoining formulas")
    #
    #     return conjoined_formulae
    #
    # def conjoin_with_formula(self, other: 'LTL') -> bool:
    #     """Returns True if other has been conjoined"""
    #
    #     if self.formula == "FALSE":
    #         print("The conjunction has no effects since the current formula is FALSE")
    #         return False
    #     if self.formula == "TRUE":
    #         self.formula = deepcopy(other.formula)
    #         self.variables = deepcopy(other.variables)
    #         return True
    #
    #     if other.formula == "FALSE":
    #         self.formula = "FALSE"
    #         return True
    #     if other.formula == "TRUE":
    #         print("The conjunction has no effects since the other formula is FALSE")
    #         return False
    #
    #     if other <= self:
    #         """the other formula is a refinement of the current formula"""
    #         self.formula = deepcopy(other.formula)
    #         self.variables = deepcopy(other.variables)
    #         return True
    #
    #     if self.is_satisfiable_with(other):
    #
    #         new_formula = deepcopy(self)
    #         new_formula.variables.extend(other.variables)
    #         new_formula.formula = And([new_formula.formula, other.formula])
    #
    #         """If by conjoining other, the result should be a refinement of the existing formula"""
    #         if new_formula <= self:
    #             self.formula = deepcopy(new_formula.formula)
    #             self.variables = deepcopy(new_formula.variables)
    #             return True
    #     else:
    #         raise InconsistentException(self, other)

    def __str__(self):
        return self.__formula


class InconsistentException(Exception):

    def __init__(self, conj_a: LTL, conj_b: LTL):
        self.conj_a = conj_a
        self.conj_b = conj_b
#
#
# def AndLTL(formulas: List[LTL]) -> LTL:
#     """Returns an LTL formula representing the logical AND of list_propoositions"""
#     if len(formulas) > 1:
#         vars = formulas[0].variables
#         for i in range(1, len(formulas)):
#             vars += formulas[i].variables
#         conj = ' & '.join(s.formula for s in formulas)
#         return LTL("(" + conj + ")", vars)
#     elif len(formulas) == 1:
#         return formulas[0]
#     else:
#         raise Exception("List of formulas is empty")
#
#
# def ImpliesLTL(one: LTL, two: LTL) -> LTL:
#     """Returns an LTL formula representing the logical implication of list_propoositions"""
#     vars = one.variables
#     vars += two.variables
#     formula = "(" + one.formula + ") -> (" + two.formula + ")"
#     return LTL(formula, vars)
#
#
# def NotLTL(element: LTL) -> LTL:
#     """Returns an str formula representing the logical AND of list_propoositions"""
#     vars = element.variables
#     formula = Not(element.formula)
#     return LTL(formula, vars)
#
#
# def OrLTL(formulas: List[LTL]) -> LTL:
#     """Returns an str formula representing the logical OR of list_propoositions"""
#     if len(formulas) > 1:
#         vars = formulas[0].variables
#         for i in range(1, len(formulas)):
#             vars += formulas[i].variables
#         conj = ' | '.join(s.formula for s in formulas)
#         return LTL("(" + conj + ")", vars)
#     elif len(formulas) == 1:
#         return formulas[0]
#     else:
#         raise Exception("List of formulas is empty")
