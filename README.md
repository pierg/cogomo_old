# CoGoMo: Incremental Refinement of Goal Models with Contracts


We present CoGoMo, a requirement engineering framework combining the goal-oriented and contract-based requirement paradigms. CoGoMo uses a new formal model, termed *contract-based goal tree* (CGT) to represent goal models in terms of hierarchies of contracts. Based on this model, we propose algorithms that leverage contract operations and relations to verify goal consistency and completeness, and to perform incremental and hierarchical refinement of goals by mapping goals to promising component architectures.


\CoGoMo assists the designer in building a CGT from early requirement elicitation to component mapping.

The designer starts by eliciting goals from stakeholders and, with the support of the tool, incrementally formalises them as contracts following the steps:

1. The designer expresses the goals and their associated contracts in a structured text file. For example:

```
CONSTANTS:
    TR_min        := 3000000   # bit/s
    TR_max        := 27000000  # bit/s
    L             := 3200      # bit (message length)

GOAL: 	
    NAME: 		
        communicate     
    DESCRIPTION:
        communicate with the leader of the platoon
        using IEEE 802;11p VANET
    VARIABLES:
        tr        := REAL   # Transmission rate
        delay     := REAL   # Propagation delay 
        n         := INT    # N of vehicles
        comm      := BOOL   # Communication established
    ASSUMPTIONS:
        tr >= TR_min 	
        tr <= TR_max 	
    GUARANTEES:
        comm
        delay == (L * n) / tr
```
A goal has a name (unique identifier), a textual description, a list of variables (real, integer or Boolean), a list of logical propositions representing the assumptions of the contract and another list representing the guarantees and where each element of the lists is assumed to be conjunction with the other elements of that list.

2. The designer expresses theoperations(composition, conjunc-tion and mapping) and thelinksamong the goals (refinement orequality).

3. CoGoMo performs satisfiability and validity checks on the propositions forming the contracts compositionally. The checks are made every time a new operation is performed, by directly operating on the contracts that are involved in the operation.
Once a conflict or an incorrect refinement is detected, CoGoMo informs the designer about the set of assumptions or guarantees that are causing the conflict as well as the associated goals.

4. In case of incompleteness or conflict, the designer can go back to step 1 and 2 to modify the content of the contracts in the text file or combine the contracts differently using the operations offered by CoGoMo


The main APIs offered by CoGoMo are:

* ``conjoin_goals(list_of_goals, name=None, description=None)``
* ``compose_goals(list_of_goals, name=None, description=None)``
* ``mapping(component_library, specification)``
* ``refine_goal(abstract_goal, refined_goal)``
* ``prioritize_goal(first_priority_goal, second_priority_goal)``

CoGoMo runs with Python3.7 and depends only on z3-solver

