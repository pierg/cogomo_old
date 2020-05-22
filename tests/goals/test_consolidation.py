# from src.components.operations import *
# from src.goals.operations import *
# from src.helper.parser import parse
# from src.contracts.contract import BooleanContract
#
# def test_composition_pointers():
#     goal_1 = CGTGoal(
#             name="goal_1",
#             contracts=[BooleanContract(["a"], ["b"])]
#         )
#
#     goal_2 = CGTGoal(
#             name="goal_2",
#             contracts=[BooleanContract(["c"], ["d"])]
#         )
#
#     goal_2b = CGTGoal(
#             name="goal_2b",
#             contracts=[BooleanContract(["e"], ["f"])]
#         )
#
#     goal_2c = CGTGoal(
#         name="goal_2c",
#         contracts=[BooleanContract(["f"], ["g"])]
#     )
#
#     cgt = composition([goal_1, goal_2])
#     print(goal_1.connected_to.name)
#     print(goal_2.connected_to.name)
#
#     print(cgt)
#     c = composition([goal_2, goal_2c])
#     print(c)
#     print(cgt)
#     goal_2.update_with(c)
#     print(cgt)
#
#
#
#
#
# def test_consolidate():
#     goals = parse('../input_files/boolean_contracts.txt')
#
#     cgt = conjunction(
#         [goals["goal_1"], goals["goal_2"]],
#         name="goal_conjoined",
#         description="")
#
#     cgt = composition(
#         [cgt, goals["goal_3"]],
#         name="goal_composed",
#         description="description of goal_composed")
#
#     print(cgt)
#
#     goals["goal_1"] = composition([goals["goal_1"], goals["goal_4"]])
#
#     print(cgt)
#
#
#     # component_library = ComponentsLibrary(name="cogomoLTL")
#     #
#     # component_library.add_components(
#     #     [
#     #         Component(component_id="c0",
#     #                   variables={"a": "boolean", "b": "boolean"},
#     #                   assumptions=["a"],
#     #                   guarantees=["b"]),
#     #         Component(component_id="c1",
#     #                   variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "k": "boolean"},
#     #                   assumptions=["a", "l", "k"],
#     #                   guarantees=["b", "x > 5"]),
#     #         Component(component_id="c2_conditional_scope",
#     #                   variables={"b": "boolean", "x": "0..100", "y": "0..100"},
#     #                   assumptions=["b", "x > 10"],
#     #                   guarantees=["y > 20"]),
#     #         Component(component_id="c3",
#     #                   variables={"b": "boolean",
#     #                              "x": "0..100",
#     #                              "y": "0..100",
#     #                              "t": "boolean",
#     #                              "r": "boolean",
#     #                              "e": "boolean"
#     #                              },
#     #                   assumptions=["b", "x > 3", "t", "r", "e"],
#     #                   guarantees=["y > 40"]),
#     #         BooleanComponent(component_id="c9",  assumptions=["a3"], guarantees=["t"]),
#     #         BooleanComponent(component_id="c10", assumptions=["a2"], guarantees=["r"]),
#     #         BooleanComponent(component_id="c11", assumptions=["a1"], guarantees=["e"]),
#     #         BooleanComponent(component_id="c12", assumptions=["b"],  guarantees=["a3"]),
#     #         BooleanComponent(component_id="c5",  assumptions=["a"],  guarantees=["a2"]),
#     #         BooleanComponent(component_id="c6",  assumptions=["r4"], guarantees=["a1"]),
#     #         BooleanComponent(component_id="c7",  assumptions=["r4"], guarantees=["a3"]),
#     #         BooleanComponent(component_id="c8",  assumptions=["t4"], guarantees=["r4"])
#     #     ])
#     #
#     # specification = CGTGoal(
#     #     name="specification",
#     #     contracts=[Contract(variables={"y": "0..100"}, guarantees=["y > 10"])])
#     #
#     # mapping(component_library, specification)
#     #
#     # print(specification)