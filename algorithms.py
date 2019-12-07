# -*- coding: utf-8 -*-

from combinations import *
from funcoes_xml import FileXML
# import time
from typing import Callable, Set, Tuple
from itertools import combinations
from solution import Solution, ClassSolution
from problem import Problem
from constants import Const
from copy import deepcopy
from functions import *


class Algorithm:
    """
    @staticmethod
    def choose_random_same_room_for_classes_except_processed(
            list_of_id_classes: List[int], problem: Problem,
            processed: Dict[int, int]) -> int:
        first_room_found_in_processed = 0
        for id_class in list_of_id_classes:
            room_of_class = processed.get(id_class)
            if room_of_class:
                if not first_room_found_in_processed:
                    first_room_found_in_processed = room_of_class
                elif room_of_class != first_room_found_in_processed:
                    return 0

        list_of_rooms = []
        for id_class in list_of_id_classes:
            list_of_rooms.append(list(problem.classes[id_class].rooms.keys()))
        intersection_rooms = Algorithm.intersection(list_of_rooms)

        if first_room_found_in_processed:
            if first_room_found_in_processed in intersection_rooms:
                return first_room_found_in_processed
            else:
                return 0

        return random.choice(intersection_rooms)

    @staticmethod
    def choose_random_different_room_for_classes_except_processed(
            list_of_id_classes: List[int], problem: Problem,
            processed: Dict[int, int], max_iter: int) -> List[int]:
        list_of_rooms_processed = []
        for id_class in list_of_id_classes:
            room_of_class = processed.get(id_class)
            if room_of_class:
                if room_of_class in list_of_rooms_processed:
                    return []
                list_of_rooms_processed.append(room_of_class)

        list_of_rooms_picked = []
        num_classes = len(list_of_id_classes)
        for i in range(0, max_iter):
            for k, id_class in enumerate(list_of_id_classes):
                id_room = processed.get(id_class)
                if not id_room:
                    id_room = random.choice(list(problem.classes[id_class].rooms.keys()))
                if id_room not in list_of_rooms_picked:
                    list_of_rooms_picked.append(id_room)
                else:
                    list_of_rooms_picked = []
                    break
            if len(list_of_rooms_picked) == num_classes:
                break
        return list_of_rooms_picked

    @staticmethod
    def choose_random_rooms_for_classes_except_processed(
            list_of_id_classes: List[int], problem: Problem,
            processed: Dict[int, int]) -> List[int]:
        list_of_rooms_picked = []
        for id_class in list_of_id_classes:
            id_room = processed.get(id_class)
            if not id_room:
                id_room = random.choice(list(problem.classes[id_class].rooms.keys()))
            list_of_rooms_picked.append(id_room)
        return list_of_rooms_picked

    @staticmethod
    def choose_random_times_for_classes_except_processed(
            function, list_of_id_classes: List[int],
            list_of_id_rooms_of_classes: List[int], problem: Problem,
            processed: Dict[int, int], max_iter: int) -> List[int]:

        list_of_id_classes_processed = Algorithm.intersection(
            [list_of_id_classes, list(processed.keys())])
        for pos_i, id_class_i in enumerate(list_of_id_classes_processed):
            for id_class_j in list_of_id_classes_processed[(pos_i + 1):]:
                id_time_i = processed[id_class_i]
                id_time_j = processed[id_class_j]
                if not function(id_time_i, id_time_j):
                    return []

        list_of_times_picked = []
        num_classes = len(list_of_id_classes)
        fail = False
        for i in range(0, max_iter):
            for k, id_class in enumerate(list_of_id_classes):
                id_time = processed.get(id_class)
                if not id_time:
                    id_time = problem.select_random_id_time_compatible_with_room(
                        id_class, list_of_id_rooms_of_classes[k])
                if id_time:
                    for j in list_of_times_picked:
                        if not function(j, id_time):
                            fail = True
                            break
                    if not fail:
                        list_of_times_picked.append(id_time)
                else:
                    fail = True

                if fail:
                    list_of_times_picked = []
                    fail = False
                    break
            if len(list_of_times_picked) == num_classes:
                break
        return list_of_times_picked

    @staticmethod
    def choose_random_times_for_same_attendees_classes_except_processed(
            list_of_id_classes: List[int],
            list_of_id_rooms_of_classes: List[int], problem: Problem,
            processed_times: Dict[int, int], max_iter: int) -> List[int]:

        processed_rooms = {}
        for i, id_class in enumerate(list_of_id_classes):
            processed_rooms[id_class] = list_of_id_rooms_of_classes[i]

        list_of_id_classes_processed = Algorithm.intersection(
            [list_of_id_classes, list(processed_times.keys())])
        for pos_i, id_class_i in enumerate(list_of_id_classes_processed):
            for id_class_j in list_of_id_classes_processed[(pos_i + 1):]:
                id_time_i = processed_times[id_class_i]
                id_room_i = processed_rooms[id_class_i]
                id_time_j = processed_times[id_class_j]
                id_room_j = processed_rooms[id_class_j]
                if not problem.is_same_attendees(
                        id_time_i, id_room_i, id_time_j, id_room_j):
                    return []

        list_of_times_picked = []
        num_classes = len(list_of_id_classes)
        fail = False
        for i in range(0, max_iter):
            for pos_id_class, id_class in enumerate(list_of_id_classes):
                id_time = processed_times.get(id_class)
                if not id_time:
                    id_time = problem.select_random_id_time_compatible_with_room(
                        id_class, list_of_id_rooms_of_classes[pos_id_class])
                if id_time:
                    id_room = list_of_id_rooms_of_classes[pos_id_class]
                    for pos_j, id_time_j in enumerate(list_of_times_picked):
                        id_room_j = list_of_id_rooms_of_classes[pos_j]
                        if not problem.is_same_attendees(
                                id_time_j, id_room_j, id_time, id_room):
                            fail = True
                            break
                    if not fail:
                        list_of_times_picked.append(id_time)
                else:
                    fail = True

                if fail:
                    list_of_times_picked = []
                    fail = False
                    break
            if len(list_of_times_picked) == num_classes:
                break
        return list_of_times_picked

    @staticmethod
    def choose_random_times_for_classes_with_constraints_slots_except_processed(
            function, list_of_id_classes: List[int], s: int,
            list_of_id_rooms_of_classes: List[int], problem: Problem,
            processed: Dict[int, int], max_iter: int) -> List[int]:

        list_of_id_classes_processed = Algorithm.intersection(
            [list_of_id_classes, list(processed.keys())])
        for pos_i, id_class_i in enumerate(list_of_id_classes_processed):
            for id_class_j in list_of_id_classes_processed[(pos_i + 1):]:
                id_time_i = processed[id_class_i]
                id_time_j = processed[id_class_j]
                if not function(id_time_i, id_time_j, s):
                    return []

        list_of_times_picked = []
        num_classes = len(list_of_id_classes)
        fail = False
        for i in range(0, max_iter):
            for k, id_class in enumerate(list_of_id_classes):
                id_time = processed.get(id_class)
                if not id_time:
                    id_time = problem.select_random_id_time_compatible_with_room(
                        id_class, list_of_id_rooms_of_classes[k])
                if id_time:
                    for j in list_of_times_picked:
                        if not function(j, id_time, s):
                            fail = True
                            break
                    if not fail:
                        list_of_times_picked.append(id_time)
                else:
                    fail = True

                if fail:
                    list_of_times_picked = []
                    fail = False
                    break
            if len(list_of_times_picked) == num_classes:
                break
        return list_of_times_picked
    """

    @staticmethod
    def verify_respect_of_hard_constraints(
            problem: Problem, id_class: int,
            classes_rooms: Dict[int, int], classes_times: Dict[int, int],
            list_of_hard_id_constraints_per_class: Dict[int, List[int]]
    ):
        if not list_of_hard_id_constraints_per_class.get(id_class):
            return True

        for id_hard_dist in \
                list_of_hard_id_constraints_per_class[id_class]:
            hard_constraint = problem.constraints[(id_hard_dist - 1)]
            list_of_id_classes = hard_constraint.classes
            intersection_of_id_classes = \
                intersection_list(list_of_id_classes,
                                  list(classes_times.keys()))
            type_iter = hard_constraint.type
            function = select_function_by_id_constraint(problem, type_iter)
            if len(intersection_of_id_classes) > 1:
                if Const.SAME_START <= type_iter <= Const.PRECEDENCE:
                    if not validate_combination_with_times_constraint(
                            function,
                            intersection_of_id_classes, classes_times):
                        return False
                elif type_iter == Const.SAME_ATTENDEES:
                    if not validate_combination_with_same_attendees_constraint(
                            problem, intersection_of_id_classes, classes_rooms,
                            classes_times):
                        return False
                elif Const.SAME_ROOM <= type_iter <= Const.DIFFERENT_ROOM:
                    # function = None
                    # if type == Const.SAME_ROOM:
                    #     function = Constraint.same_room
                    # elif type == Const.DIFFERENT_ROOM:
                    #     function = Constraint.different_room
                    if not validate_combination_with_rooms_constraint(
                            function, intersection_of_id_classes,
                            classes_rooms):
                        return False
                elif Const.WORK_DAY <= type_iter <= Const.MIN_GAP:
                    # function = None
                    # if type == Const.WORK_DAY:
                    #     function = problem.is_work_day
                    # elif type == Const.MIN_GAP:
                    #     function = problem.is_min_gap
                    s = hard_constraint.list_of_params[0]
                    if not validate_combination_with_times_and_slots_constraint(
                            function, intersection_of_id_classes, s,
                            classes_times):
                        return False
                elif Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    if not function(
                            intersection_of_id_classes, s, problem, classes_times):
                        return False
                elif Const.MAX_BREAKS <= type_iter <= Const.MAX_BLOCK:
                    r = hard_constraint.list_of_params[0]
                    s = hard_constraint.list_of_params[1]
                    if not function(
                            intersection_of_id_classes, r, s, problem, classes_times):
                        return False
            elif len(intersection_of_id_classes) == 1:
                if Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    if not function(
                            intersection_of_id_classes, s, problem, classes_times):
                        return False
        return True

    @staticmethod
    def __enumerate_days_and_slots_constraint_conflicts_recursive(
            problem: Problem, function: Callable, list_of_id_classes: List[int], pos: int, s: int,
            classes_times: Dict[int, List[int]], classes_times_aux: Dict[int, int],
            list_of_conflicts: List[Set[Tuple[int, int]]]
    ) -> None:
        if pos < len(list_of_id_classes):
            id_class = list_of_id_classes[pos]
            for id_time in classes_times[id_class]:
                classes_times_aux[id_class] = id_time
                Algorithm.__enumerate_days_and_slots_constraint_conflicts_recursive(
                    problem, function, list_of_id_classes, (pos + 1), s,
                    classes_times, classes_times_aux, list_of_conflicts)
        else:
            if not function(list_of_id_classes, s, problem, classes_times_aux):
                conflict = set()
                for id_class in list_of_id_classes:
                    id_time = classes_times_aux[id_class]
                    conflict.add((id_class, id_time))
                list_of_conflicts.append(conflict)

    @staticmethod
    def enumerate_days_and_slots_constraint_conflicts(
            problem: Problem, function: Callable, list_of_id_classes: List[int],
            s: int, classes_times: Dict[int, List[int]]
    ) -> List[Set[Tuple[int, int]]]:
        if len(list_of_id_classes) >= 1:
            list_of_conflicts = []
            classes_times_aux = {}
            pos = 0
            Algorithm.__enumerate_days_and_slots_constraint_conflicts_recursive(
                problem, function, list_of_id_classes, pos, s,
                classes_times, classes_times_aux, list_of_conflicts)
            return list_of_conflicts

    @staticmethod
    def __enumerate_breaks_blocks_and_slots_constraint_conflicts_recursive(
            problem: Problem, function: Callable, list_of_id_classes: List[int], pos: int,
            r: int, s: int, classes_times: Dict[int, List[int]],
            classes_times_aux: Dict[int, int], list_of_conflicts: List[Set[Tuple[int, int]]]
    ) -> None:
        if pos < len(list_of_id_classes):
            id_class = list_of_id_classes[pos]
            for id_time in classes_times[id_class]:
                classes_times_aux[id_class] = id_time
                Algorithm.__enumerate_breaks_blocks_and_slots_constraint_conflicts_recursive(
                    problem, function, list_of_id_classes, (pos + 1), r, s,
                    classes_times, classes_times_aux, list_of_conflicts)
        else:
            if not function(list_of_id_classes, r, s, problem, classes_times_aux):
                conflict = set()
                for id_class in list_of_id_classes:
                    id_time = classes_times_aux[id_class]
                    conflict.add((id_class, id_time))
                list_of_conflicts.append(conflict)

    @staticmethod
    def enumerate_breaks_blocks_and_slots_constraint_conflicts(
            problem: Problem, function: Callable, list_of_id_classes: List[int],
            r: int, s: int, classes_times: Dict[int, List[int]]
    ) -> List[Set[Tuple[int, int]]]:
        if len(list_of_id_classes) >= 1:
            list_of_conflicts = []
            classes_times_aux = {}
            pos = 0
            Algorithm.__enumerate_breaks_blocks_and_slots_constraint_conflicts_recursive(
                problem, function, list_of_id_classes, pos, r, s,
                classes_times, classes_times_aux, list_of_conflicts)
            return list_of_conflicts

    # def __generate_combinations_of_conflict_classes(self, list_of_id_classes, m, s, times_classes, r):
    #     list_of_conflicts = []
    #     list_of_id_classes_combinations = list(combinations(list_of_id_classes, r))
    #     for combination in list_of_id_classes_combinations:
    #         if not Constraint.max_block_hard(list_of_id_classes, m, s, self.problem, times_classes):
    #             list_of_conflicts.append(combination)
    #     return list_of_conflicts

    @staticmethod
    def is_same_attendees_conflict_pair(
            problem, id_class_1, id_class_2, classes_rooms, classes_times):
        for k, id_time_1 in enumerate(classes_times.get(id_class_1)):
            id_room_1 = classes_rooms.get(id_class_1)[k]
            for l, id_time_2 in enumerate(classes_times.get(id_class_2)):
                id_room_2 = classes_rooms.get(id_class_2)[l]
                if id_room_1 != id_room_2 and not problem.is_same_attendees(
                        id_time_1, id_room_1, id_time_2, id_room_2):
                    return True
        return False

    @staticmethod
    def verify_respect_of_hard_constraints_for_relaxed_model(
            problem: Problem, classes_assigned: List[int], classes_rooms: Dict[int, List[int]],
            classes_times: Dict[int, List[int]], hard_constraints_to_add_cuts: Dict[int, bool]
    ):
        dict_of_conflicts = {Const.CT_PAIR: [],
                             Const.CTR_PAIR: [],
                             Const.CR_PAIR: [],
                             Const.CT_GROUP: [],
                             Const.CTR_GROUP: []}

        for hard_constraint in problem.distributions_hard:
            type_iter = hard_constraint.type
            if not hard_constraints_to_add_cuts.get(type_iter):
                continue
            list_of_id_classes = intersection_int(hard_constraint.classes, classes_assigned)
            function = select_function_by_id_constraint(problem, type_iter)
            if len(list_of_id_classes) > 1:
                if Const.SAME_START <= type_iter <= Const.PRECEDENCE:
                    list_of_conflicts = enumerate_times_constraint_conflicts(
                        function, list_of_id_classes, classes_times)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CT_PAIR]:
                                dict_of_conflicts[Const.CT_PAIR].append(c)
                elif type_iter == Const.SAME_ATTENDEES:
                    # list_of_conflicts = enumerate_same_attendees_constraint_conflicts(
                    #     problem, list_of_id_classes, classes_rooms,
                    #     classes_times)
                    list_of_conflicts = []
                    for id_class_i, id_class_j in combinations(list_of_id_classes, 2):
                        pair = [id_class_i, id_class_j]
                        conflicts_pair = enumerate_same_attendees_constraint_conflicts(
                            problem, pair, classes_rooms,
                            classes_times)
                        list_of_conflicts.extend(conflicts_pair)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CTR_PAIR]:
                                dict_of_conflicts[Const.CTR_PAIR].append(c)
                elif Const.SAME_ROOM <= type_iter <= Const.DIFFERENT_ROOM:
                    list_of_conflicts = enumerate_rooms_constraint_conflicts(
                        function, list_of_id_classes, classes_rooms)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CR_PAIR]:
                                dict_of_conflicts[Const.CR_PAIR].append(c)
                elif Const.WORK_DAY <= type_iter <= Const.MIN_GAP:
                    s = hard_constraint.list_of_params[0]
                    list_of_conflicts = enumerate_times_and_slots_constraint_conflicts(
                        function, list_of_id_classes, s,
                        classes_times)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CT_PAIR]:
                                dict_of_conflicts[Const.CT_PAIR].append(c)
                elif Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    list_of_conflicts = \
                        Algorithm.enumerate_days_and_slots_constraint_conflicts(
                            problem, function, list_of_id_classes, s, classes_times)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CT_GROUP]:
                                dict_of_conflicts[Const.CT_GROUP].append(c)
                elif Const.MAX_BREAKS <= type_iter <= Const.MAX_BLOCK:
                    r = hard_constraint.list_of_params[0]
                    s = hard_constraint.list_of_params[1]
                    list_of_conflicts = \
                        Algorithm.enumerate_breaks_blocks_and_slots_constraint_conflicts(
                            problem, function, list_of_id_classes, r, s, classes_times)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CT_GROUP]:
                                dict_of_conflicts[Const.CT_GROUP].append(c)
            elif len(list_of_id_classes) == 1:
                if Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    list_of_conflicts = \
                        Algorithm.enumerate_days_and_slots_constraint_conflicts(
                            problem, function, list_of_id_classes, s, classes_times)
                    if list_of_conflicts:
                        for c in list_of_conflicts:
                            if c not in dict_of_conflicts[Const.CT_GROUP]:
                                dict_of_conflicts[Const.CT_GROUP].append(c)

        return dict_of_conflicts

    @staticmethod
    def validate_respect_of_hard_constraints_in_solution(
            problem: Problem, classes_rooms: Dict[int, List[int]],
            classes_times: Dict[int, List[int]]
    ):
        for hard_constraint in problem.distributions_hard:
            type_iter = hard_constraint.type
            # if hard_constraints_to_add.get(type_iter):
            #     continue
            list_of_id_classes = hard_constraint.classes
            function = select_function_by_id_constraint(problem, type_iter)
            if len(list_of_id_classes) > 1:
                if Const.SAME_START <= type_iter <= Const.PRECEDENCE:
                    if not validate_combination_with_times_constraint(
                            function,
                            list_of_id_classes, classes_times):
                        return False
                elif type_iter == Const.SAME_ATTENDEES:
                    if not validate_combination_with_same_attendees_constraint(
                            problem, list_of_id_classes, classes_rooms,
                            classes_times):
                        return False
                elif Const.SAME_ROOM <= type_iter <= Const.DIFFERENT_ROOM:
                    if not validate_combination_with_rooms_constraint(
                            function, list_of_id_classes,
                            classes_rooms):
                        return False
                elif Const.WORK_DAY <= type_iter <= Const.MIN_GAP:
                    s = hard_constraint.list_of_params[0]
                    if not validate_combination_with_times_and_slots_constraint(
                            function, list_of_id_classes, s,
                            classes_times):
                        return False
                elif Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    if not function(
                            list_of_id_classes, s, problem, classes_times):
                        return False
                elif Const.MAX_BREAKS <= type_iter <= Const.MAX_BLOCK:
                    r = hard_constraint.list_of_params[0]
                    s = hard_constraint.list_of_params[1]
                    if not function(
                            list_of_id_classes, r, s, problem, classes_times):
                        return False
            elif len(list_of_id_classes) == 1:
                if Const.MAX_DAYS <= type_iter <= Const.MAX_DAY_LOAD:
                    s = hard_constraint.list_of_params[0]
                    if not function(
                            list_of_id_classes, s, problem, classes_times):
                        return False
        return True

    @staticmethod
    def generate_list_of_classes_in_sequence_of_processing(
            problem: Problem,
            list_of_groups_of_hard_constraints,
            list_of_id_classes_in_sequence_of_processing,
            list_of_hard_id_constraints_per_class
    ):
        random.shuffle(list_of_groups_of_hard_constraints)
        for list_of_hard_id_constraints in list_of_groups_of_hard_constraints:
            # Seleciona as hard constraints de Same Room:
            for hard_id_constraint in list_of_hard_id_constraints:
                hard_constraint = problem.constraints[(hard_id_constraint - 1)]
                if hard_constraint.type == Const.SAME_ROOM:
                    for id_class in hard_constraint.classes:
                        if id_class not in problem.fixed_classes:
                            if id_class not in list_of_id_classes_in_sequence_of_processing:
                                list_of_id_classes_in_sequence_of_processing.append(id_class)
                            if id_class not in list_of_hard_id_constraints_per_class:
                                list_of_hard_id_constraints_per_class[id_class] = [hard_id_constraint, ]
                            else:
                                list_of_hard_id_constraints_per_class[id_class].append(hard_id_constraint)

            # Seleciona as hard constraints de Different Room:
            for hard_id_constraint in list_of_hard_id_constraints:
                hard_constraint = problem.constraints[(hard_id_constraint - 1)]
                if hard_constraint.type == Const.DIFFERENT_ROOM:
                    for id_class in hard_constraint.classes:
                        if id_class not in problem.fixed_classes:
                            if id_class not in list_of_id_classes_in_sequence_of_processing:
                                list_of_id_classes_in_sequence_of_processing.append(id_class)
                            if id_class not in list_of_hard_id_constraints_per_class:
                                list_of_hard_id_constraints_per_class[id_class] = [hard_id_constraint, ]
                            else:
                                list_of_hard_id_constraints_per_class[id_class].append(hard_id_constraint)

            # Seleciona as demais hard constraints:
            for hard_id_constraint in list_of_hard_id_constraints:
                hard_constraint = problem.constraints[(hard_id_constraint - 1)]
                if hard_constraint.type != Const.DIFFERENT_ROOM and \
                        hard_constraint.type != Const.SAME_ROOM:
                    for id_class in hard_constraint.classes:
                        if id_class not in problem.fixed_classes:
                            if id_class not in list_of_id_classes_in_sequence_of_processing:
                                list_of_id_classes_in_sequence_of_processing.append(id_class)
                            if id_class not in list_of_hard_id_constraints_per_class:
                                list_of_hard_id_constraints_per_class[id_class] = [hard_id_constraint, ]
                            else:
                                list_of_hard_id_constraints_per_class[id_class].append(hard_id_constraint)

    """@staticmethod
    def continue_build_solution(
            problem: Problem, classes_rooms, classes_times,
            list_of_id_times_per_room
    ) -> bool:
        list_of_id_classes_in_sequence_of_processing = []
        list_of_processed_classes = list(classes_rooms.keys())
        for id_class in list(problem.classes.keys()):
            if id_class not in list_of_processed_classes:
                list_of_id_classes_in_sequence_of_processing.append(id_class)

        combination_per_class = []

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        i = 0

        id_class_i = list_of_id_classes_in_sequence_of_processing[i]
        list_of_id_rooms_per_class[id_class_i] = list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list(problem.classes[id_class_i].rooms.keys()),
            list(problem.classes[id_class_i].times.keys())))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            return False

        must_increment_combination = False
        id_room_i = -1
        id_time_i = -1

        nr_processed = len(classes_times)
        tam = len(problem.classes)
        must_increment_combination = False
        while i >= 0:
            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (id_class_i, (i + 1 + nr_processed), tam))
            if must_increment_combination:
                combination = combination_per_class[-1]
                id_time_i = combination.time
                id_room_i = combination.room
                #classes_times[id_class_i] = id_time_i
                #classes_rooms[id_class_i] = id_room_i
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            combination = combination_per_class[-1]
            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i

            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]

                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list(problem.classes[id_class_i].rooms.keys()),
                    list(problem.classes[id_class_i].times.keys())))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                #pdb.set_trace()
                return True

        #pdb.set_trace()
        return False
    """

    """@staticmethod
    def build_solution_for_hard_distributions(problem: Problem, start_time: float) -> Solution:
        solution = Solution(problem)
        Algorithm.enroll_students(solution)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        list_of_groups_of_hard_constraints = \
            calculate_intersection_groups_of_hard_constraints(problem)

        list_of_id_classes_in_sequence_of_processing = []
        list_of_hard_id_constraints_per_class = {}

        # Gera a ordem de processamento das turmas do problema.
        Algorithm.generate_list_of_classes_in_sequence_of_processing(
            problem, list_of_groups_of_hard_constraints,
            list_of_id_classes_in_sequence_of_processing,
            list_of_hard_id_constraints_per_class)

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            input("PRESS ENTER...")
            return solution

        must_increment_combination = False
        count_solutions = 0
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + nr_fixed_classes
        while 0 <= i < len(list_of_id_classes_in_sequence_of_processing):

            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    #if id_class_i == 1:
                    #    print(combination_per_class[-1])
                    #    print("LIST_OF_ID_TIMES_PER_ROOM: %s" % str(list_of_id_times_per_room))
                    #    input("PRESS ENTER...")
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            #if id_class_i == 65 or id_class_i == 75:
            #    print(combination_per_class[-1])

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                print("ACHOU SOLUCAO PARA AS HARD CONSTRAINTS!")
                count_solutions += 1
                classes_rooms_copy = deepcopy(classes_rooms)
                classes_times_copy = deepcopy(classes_times)
                list_of_id_times_per_room_copy = deepcopy(list_of_id_times_per_room)
                if Algorithm.continue_build_solution(
                        problem, classes_rooms_copy, classes_times_copy,
                        list_of_id_times_per_room_copy):
                    print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
                    for id_class_k in list(classes_times_copy.keys())[(len(problem.fixed_classes)):]:
                        id_room = classes_rooms_copy[id_class_k]
                        id_time = classes_times_copy[id_class_k]
                        solution.classes_solution[id_class_k] = ClassSolution(id_class_k, id_time, id_room)
                    end_time = (time.time() - start_time)
                    solution.runtime = "%s" % round(end_time, 1)
                    file_name = "output\\saida_" + solution.problem.name + "\\saida_" + solution.problem.name + \
                               "_nr_" + str(count_solutions) + ".xml"
                    FileXML.write_file_xml(file_name, solution)
                i -= 1
                must_increment_combination = True

        print("ACHOU TODAS AS SOLUCOES POSSIVEIS!")
        input("PRESS ENTER...")
        pdb.set_trace()

        return solution
    """

    """@staticmethod
    def build_initial_feasible_solution(problem: Problem, start_time: float) -> Solution:
        solution = Solution(problem)
        Algorithm.enroll_students(solution)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        # list_of_groups_of_hard_constraints = \
        #    calculate_intersection_groups_of_hard_constraints(problem)

        list_of_groups_of_hard_constraints = \
            generate_list_of_groups_of_hard_constraints(problem.distributions_hard)

        list_of_id_classes_in_sequence_of_processing = []
        list_of_hard_id_constraints_per_class = {}

        # Gera a ordem de processamento das turmas do problema.
        Algorithm.generate_list_of_classes_in_sequence_of_processing(
            problem, list_of_groups_of_hard_constraints,
            list_of_id_classes_in_sequence_of_processing,
            list_of_hard_id_constraints_per_class)

        list_aux = []
        for id_class in list(problem.classes.keys()):
            if id_class not in problem.fixed_classes and id_class not in \
                    list_of_id_classes_in_sequence_of_processing:
                list_aux.append(id_class)
        random.shuffle(list_aux)
        list_of_id_classes_in_sequence_of_processing.extend(list_aux)

        if len(list_of_id_classes_in_sequence_of_processing) != \
                len(problem.classes) - len(problem.fixed_classes):
            print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
                  len(list_of_id_classes_in_sequence_of_processing))
            print("len(problem.classes) = %d" % len(problem.classes))
            print("ERRO!")
            return solution

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            input("PRESS ENTER...")
            return solution

        must_increment_combination = False
        count_solutions = 0
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + \
              nr_fixed_classes
        while i >= 0:

            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (
                id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                count_solutions += 1
                print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
                for id_class_k in list(classes_times.keys())[(len(
                        problem.fixed_classes)):]:
                    id_room = classes_rooms[id_class_k]
                    id_time = classes_times[id_class_k]
                    solution.classes_solution[id_class_k] = ClassSolution(
                        id_class_k, id_time, id_room)
                end_time = (time.time() - start_time)
                solution.runtime = "%s" % round(end_time, 1)
                Algorithm.enroll_students(solution)
                file_name = "output\\" + solution.problem.name + \
                            "\\saida_" + solution.problem.name + "_nr_" + \
                            str(count_solutions) + ".xml"
                FileXML.write_file_xml(file_name, solution)
                break

        # print("ACHOU TODAS AS SOLUCOES POSSIVEIS!")
        input("PRESS ENTER...")
        pdb.set_trace()

        return solution"""

    @staticmethod
    def build_solutions(problem: Problem, list_of_hard_id_constraints_per_class,
                        list_of_id_classes_in_sequence_of_processing,
                        start_time: float, time_limit, count_of_files):
        solution = Solution(problem)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        # if len(list_of_id_classes_in_sequence_of_processing) != \
        #         len(problem.classes) - len(problem.fixed_classes):
        #     print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
        #           len(list_of_id_classes_in_sequence_of_processing))
        #     print("len(problem.classes) = %d" % len(problem.classes))
        #     print("ERRO!")
        #     return solution

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            # input("PRESS ENTER...")
            # pdb.set_trace()
            return solution

        must_increment_combination = False
        count_solutions = count_of_files
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + nr_fixed_classes

        initial_time = time.time()
        while i >= 0:
            if (time.time() - initial_time) >= time_limit:
                return i, None
            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (
               id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):
                if (time.time() - initial_time) >= time_limit:
                    return i, None
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                count_solutions += 1
                print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
                for id_class_k in list(classes_times.keys())[
                                  (len(problem.fixed_classes)):]:
                    id_room = classes_rooms[id_class_k]
                    id_time = classes_times[id_class_k]
                    solution.classes_solution[id_class_k] = ClassSolution(
                        id_class_k, id_time, id_room)
                end_time = (time.time() - start_time)
                solution.runtime = "%s" % round(end_time, 1)
                Algorithm.enroll_students(solution)
                file_name = "output\\" + "{0:02d}".format(count_solutions) + "_saida_" + \
                            solution.problem.name + ".xml"
                FileXML.write_file_xml(file_name, solution)
                break

        return i, solution

    @staticmethod
    def build_solutions_without_backtrack(
            problem: Problem, list_of_hard_id_constraints_per_class,
            list_of_id_classes_in_sequence_of_processing,
            start_time: float, time_limit, count_of_files):
        solution = Solution(problem)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        # if len(list_of_id_classes_in_sequence_of_processing) != \
        #        len(problem.classes) - len(problem.fixed_classes):
        #    print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
        #          len(list_of_id_classes_in_sequence_of_processing))
        #    print("len(problem.classes) = %d" % len(problem.classes))
        #    print("ERRO!")
        #    return solution

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            # input("PRESS ENTER...")
            # pdb.set_trace()
            return solution

        must_increment_combination = False
        count_solutions = count_of_files
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + nr_fixed_classes

        initial_time = time.time()
        while True:
            # if (time.time() - initial_time) >= time_limit:
            #     return i, None
            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (
                id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):
                # if (time.time() - initial_time) >= time_limit:
                #     return i, None
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                count_solutions += 1
                print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
                for id_class_k in list(classes_times.keys())[(len(
                        problem.fixed_classes)):]:
                    id_room = classes_rooms[id_class_k]
                    id_time = classes_times[id_class_k]
                    solution.classes_solution[id_class_k] = ClassSolution(
                        id_class_k, id_time, id_room)
                end_time = (time.time() - start_time)
                solution.runtime = "%s" % round(end_time, 1)
                Algorithm.enroll_students(solution)
                file_name = "output\\" + "{0:02d}".format(count_solutions) + "_saida_" + \
                            solution.problem.name + ".xml"
                FileXML.write_file_xml(file_name, solution)
                break

        return i, solution

    """@staticmethod
    def build_solutions_techniques_mixing(
            problem: Problem, list_of_hard_id_constraints_per_class,
            list_of_id_classes_in_sequence_of_processing,
            start_time: float, time_limit, count_of_files):
        solution = Solution(problem)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        # if len(list_of_id_classes_in_sequence_of_processing) != \
        #        len(problem.classes) - len(problem.fixed_classes):
        #    print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
        #          len(list_of_id_classes_in_sequence_of_processing))
        #    print("len(problem.classes) = %d" % len(problem.classes))
        #    print("ERRO!")
        #    return solution

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            input("PRESS ENTER...")
            pdb.set_trace()
            return solution

        must_increment_combination = False
        count_solutions = count_of_files
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + \
              nr_fixed_classes

        initial_time = time.time()
        while i >= 0:
            if (time.time() - initial_time) >= time_limit:
                return i, None
            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (
                id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):
                if (time.time() - initial_time) >= time_limit:
                    return i, None
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].rooms.keys())
                    random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].times.keys())
                    random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                count_solutions += 1
                print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)

                problem_aux = deepcopy(problem)
                problem_aux.fix_classes(classes_rooms, classes_times)
                mip = UCTPModelIntegerProgramming(problem_aux)
                solution = mip.build_model_and_get_solution()

                end_time = (time.time() - start_time)
                solution.runtime = "%s" % round(end_time, 1)
                print("--- SOLUCAO: %s seconds ---" % round(end_time, 3))

                file_name = "output\\" + "{0:02d}".format(count_solutions) + "_saida_" + \
                            solution.problem.name + ".xml"
                FileXML.write_file_xml(file_name, solution)
                break

        return i, solution"""

    """@staticmethod
    def build_solutions_test(problem: Problem, list_of_hard_id_constraints_per_class,
                             list_of_id_classes_in_sequence_of_processing,
                             start_time: float, time_limit, count_of_files):
        solution = Solution(problem)
        solution.cores = 8
        solution.technique = "Greedy Algorithm"
        solution.author = "Marlucio Pires"
        solution.institution = "UFOP"
        solution.country = "Brasil"

        solution.allocate_fixed_classes()

        list_of_id_rooms_per_class = {}
        list_of_id_times_per_class = {}

        list_of_id_times_per_room = {}

        classes_times = {}
        classes_rooms = {}
        for id_class in problem.fixed_classes:
            id_time = solution.classes_solution[id_class].id_time
            classes_times[id_class] = id_time
            id_room = solution.classes_solution[id_class].id_room
            classes_rooms[id_class] = id_room
            if id_room not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room] = [id_time, ]
            else:
                list_of_id_times_per_room[id_room].append(id_time)

        combination_per_class = []

        #if len(list_of_id_classes_in_sequence_of_processing) != \
        #        len(problem.classes) - len(problem.fixed_classes):
        #    print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
        #          len(list_of_id_classes_in_sequence_of_processing))
        #    print("len(problem.classes) = %d" % len(problem.classes))
        #    print("ERRO!")
        #    return solution

        i = 0
        id_class_i = list_of_id_classes_in_sequence_of_processing[i]

        list_of_id_rooms_per_class[id_class_i] = \
            list(problem.classes[id_class_i].rooms.keys())
        # random.shuffle(list_of_id_rooms_per_class[id_class_i])
        list_of_id_times_per_class[id_class_i] = \
            list(problem.classes[id_class_i].times.keys())
        # random.shuffle(list_of_id_times_per_class[id_class_i])

        combination_per_class.append(CombinationClass(
            id_class_i, list_of_id_rooms_per_class[id_class_i],
            list_of_id_times_per_class[id_class_i]))

        if not combination_per_class[-1].start_combination(
                problem, list_of_id_times_per_room):
            print("PROBLEM INFEASIBLE!")
            input("PRESS ENTER...")
            pdb.set_trace()
            return solution

        must_increment_combination = False
        count_solutions = count_of_files
        nr_fixed_classes = problem.number_of_fixed_classes
        tam = len(list_of_id_classes_in_sequence_of_processing) + \
              nr_fixed_classes

        initial_time = time.time()
        while i >= 0:
            if (time.time() - initial_time) >= time_limit:
                return i, None
            id_class_i = list_of_id_classes_in_sequence_of_processing[i]
            print("RESOLVENDO C%d (%d / %d)" % (
                id_class_i, (i + 1 + nr_fixed_classes), tam))
            combination = combination_per_class[-1]
            if must_increment_combination:
                id_time_i = combination.time
                id_room_i = combination.room
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination_per_class[-1].increment_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    del classes_times[id_class_i]
                    del classes_rooms[id_class_i]
                    i -= 1
                    must_increment_combination = True
                    continue
                else:
                    must_increment_combination = False

            id_time_i = combination.time
            id_room_i = combination.room
            classes_times[id_class_i] = id_time_i
            classes_rooms[id_class_i] = id_room_i
            if id_room_i in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            else:
                list_of_id_times_per_room[id_room_i] = [id_time_i, ]

            if not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, classes_rooms, classes_times,
                    list_of_hard_id_constraints_per_class):

                if (time.time() - initial_time) >= time_limit:
                    return i, None
                must_increment_combination = True
                continue

            i += 1
            if i < len(list_of_id_classes_in_sequence_of_processing):
                id_class_i = list_of_id_classes_in_sequence_of_processing[i]
                if not list_of_id_rooms_per_class.get(id_class_i):
                    list_of_id_rooms_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].rooms.keys())
                    # random.shuffle(list_of_id_rooms_per_class[id_class_i])
                    list_of_id_times_per_class[id_class_i] = \
                        list(problem.classes[id_class_i].times.keys())
                    # random.shuffle(list_of_id_times_per_class[id_class_i])

                combination_per_class.append(CombinationClass(
                    id_class_i, list_of_id_rooms_per_class[id_class_i],
                    list_of_id_times_per_class[id_class_i]))

                if not combination_per_class[-1].start_combination(
                        problem, list_of_id_times_per_room):
                    if (time.time() - initial_time) >= time_limit:
                        return i, None
                    del combination_per_class[-1]
                    i -= 1
                    must_increment_combination = True
            else:
                count_solutions += 1
                print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
                for id_class_k in list(classes_times.keys())[(len(
                        problem.fixed_classes)):]:
                    id_room = classes_rooms[id_class_k]
                    id_time = classes_times[id_class_k]
                    solution.classes_solution[id_class_k] = ClassSolution(
                        id_class_k, id_time, id_room)
                end_time = (time.time() - start_time)
                solution.runtime = "%s" % round(end_time, 1)
                Algorithm.enroll_students(solution)
                file_name = "output\\" + "{0:02d}".format(count_solutions) + "_saida_" + \
                            solution.problem.name + ".xml"
                FileXML.write_file_xml(file_name, solution)
                break

        return i, solution"""

    @staticmethod
    def enroll_students(solution: Solution) -> None:
        if len(solution.classes_solution):
            classes_per_student, students_per_class = \
                solution.allocate_all_students()
            for id_student, student_courses in classes_per_student.items():
                solution.classes_per_students[id_student] = []
                for classes in student_courses.values():
                    solution.classes_per_students[id_student].extend(classes)

            for id_class in solution.indirect_sort_index:
                if students_per_class.get(id_class):
                    solution.classes_solution[id_class].students.extend(
                        students_per_class[id_class])

    @staticmethod
    def finalize_students_enrollment(
            solution: Solution, classes_per_student: Dict[int, List[int]],
            students_per_class: Dict[int, List[int]]) -> None:
        if len(solution.classes_solution):
            for id_student, list_of_id_classes in classes_per_student.items():
                solution.classes_per_students[id_student] = []
                solution.classes_per_students[id_student].extend(list_of_id_classes)

            for id_class in students_per_class.keys():
                solution.classes_solution[id_class].students.extend(
                    students_per_class[id_class])

    """
    @staticmethod
    def rebuild_random_solution(solution: Solution):
        solution.clear_allocation_of_classes()
        for id_class in Algorithm.intersection(
                [solution.indirect_sort_index,
                 solution.problem.not_fixed_classes]):
            best_id_room, id_time = \
                Algorithm.rand_room_and_time_for_a_class(id_class, solution)
            solution.classes_solution[id_class] = \
                ClassSolution(id_class, id_time, best_id_room)
            if best_id_room:
                if best_id_room in solution.classes_solution_in_rooms.keys():
                    solution.classes_solution_in_rooms[best_id_room].append(
                        id_class)
                else:
                    solution.classes_solution_in_rooms[best_id_room] = \
                        [id_class, ]
                        
    @staticmethod
    def build_random_solution(problem: Problem) -> Solution:
        solution = Solution(problem)

        solution.allocate_fixed_classes()

        for id_class in Algorithm.intersection(
                [solution.indirect_sort_index,
                 solution.problem.not_fixed_classes]):
            best_id_room, id_time = \
                Algorithm.rand_room_and_time_for_a_class(id_class, solution)
            solution.classes_solution[id_class] = \
                ClassSolution(id_class, id_time, best_id_room)
            if best_id_room:
                if best_id_room in solution.classes_solution_in_rooms.keys():
                    solution.classes_solution_in_rooms[best_id_room].append(
                        id_class)
                else:
                    solution.classes_solution_in_rooms[best_id_room] = \
                        [id_class, ]

        return solution
    """

    @staticmethod
    def build_greedy_initial_solution(problem: Problem) -> Solution:
        solution = Solution(problem)

        solution.allocate_fixed_classes()

        for id_class in intersection(
                solution.indirect_sort_index,
                solution.problem.not_fixed_classes):
            best_id_room, id_time = \
                Algorithm.best_fit_effort_class(id_class, solution)
            solution.classes_solution[id_class] = \
                ClassSolution(id_class, id_time, best_id_room)
            if best_id_room:
                if best_id_room in solution.classes_solution_in_rooms.keys():
                    solution.classes_solution_in_rooms[best_id_room].append(
                        id_class)
                else:
                    solution.classes_solution_in_rooms[best_id_room] = \
                        [id_class, ]
        return solution

    @staticmethod
    def rand_room_and_time_for_a_class(id_class: int, solution: Solution):
        # Obtém a lista de salas permitidas para a turma.
        rooms_of_class = solution.problem.classes.get(id_class).rooms

        # Variável que armazena o id da sala escolhido na primeira iteração.
        id_room_first_iteration = None

        found_time_available = False
        id_time = 0

        times_of_class = solution.problem.classes[id_class].times

        if rooms_of_class:
            # Escolhe-se uma sala aleatória.
            pos_room = random.randint(0, (len(rooms_of_class.keys()) - 1))
            id_room_picked = list(rooms_of_class.keys())[pos_room]

            first_iteration = True
            list_of_remanescent_rooms = deepcopy(list(rooms_of_class.keys()))

            while list_of_remanescent_rooms:
                # for id_time_iter in list(times_of_class.keys()):
                for i in range(0, len(times_of_class.keys())):
                    pos_time = random.randint(0, (len(times_of_class.keys()) - 1))
                    id_time_picked = list(times_of_class.keys())[pos_time]
                    if solution.problem.rooms[id_room_picked].is_time_unavailable(
                            id_time_picked, solution.problem.is_overlap):
                        continue
                    if solution.is_time_available(id_time_picked, id_room_picked):
                        return id_room_picked, id_time_picked

                list_of_remanescent_rooms.remove(id_room_picked)
                if list_of_remanescent_rooms:
                    pos_room = random.randint(0, (len(list_of_remanescent_rooms) - 1))
                    id_room_picked = list(list_of_remanescent_rooms)[pos_room]

                if first_iteration:
                    id_room_first_iteration = id_room_picked
                    first_iteration = False

            solution.classes_not_assigned.append(id_class)
            solution.classes_not_assigned_with_times_rooms_conflict.append(id_class)

            # for id_time_iter in list(times_of_class.keys()):
            for i in range(0, len(times_of_class.keys())):
                pos_time = random.randint(0, (len(times_of_class.keys()) - 1))
                id_time_picked = list(times_of_class.keys())[pos_time]
                if solution.problem.rooms[id_room_first_iteration].is_time_unavailable(
                        id_time_picked, solution.problem.is_overlap):
                    continue
                id_time = id_time_picked
                found_time_available = True
                break

        if not found_time_available:
            pos_time = random.randint(0, (len(times_of_class.keys()) - 1))
            id_time = list(times_of_class.keys())[pos_time]
        list_of_id_classes = solution.conflicting_classes_in_room(
            id_time, id_room_first_iteration)
        for id_class_conflicting in list_of_id_classes:
            solution.classes_conflict.add_conflict_without_check(
                id_class, id_class_conflicting)
        return id_room_first_iteration, id_time
        
    @staticmethod
    def best_fit_effort_class(id_class: int, solution: Solution):
        # Retorna a melhor sala (room) e id de horário (time) para uma turma
        # (class), baseada no critério best fit (seleciona a sala em que há menos
        # desperdício de vagas ociosas).

        # Evita-se retornar um horário (time) conflitante com outra turma (class)
        # já alocada na sala (room).
        
        # Obtém a lista de salas permitidas para a turma.
        rooms_of_class = solution.problem.classes.get(id_class).rooms

        best_id_room_first_iteration = None  # Se a turma não necessita de sala, retorna-se somente um horário.

        found_time_available = False
        id_time = 0

        if rooms_of_class:
            # Inicialmente, a melhor sala para a turma é a primeira da lista.
            best_id_room = list(rooms_of_class.keys())[0]
            best_rem = \
                solution.problem.rooms[best_id_room].capacity - \
                solution.problem.classes[id_class].limit

            first_iteration = True
            list_of_remanescent_rooms = deepcopy(list(rooms_of_class.keys()))

            # Percorrem-se todas as demais salas para computar a adequação
            # entre vagas necessárias para a turma e a capacidade das salas.
            while list_of_remanescent_rooms:
                for id_room in list_of_remanescent_rooms:
                    rem = solution.problem.rooms[id_room].capacity - \
                          solution.problem.classes[id_class].limit
                    if rem < best_rem:
                        best_id_room = id_room
                        best_rem = rem

                for id_time_iter in list(solution.problem.classes[id_class].times.keys()):
                    if solution.problem.rooms[best_id_room].is_time_unavailable(id_time_iter,
                                                                                solution.problem.is_overlap):
                        continue
                    if solution.is_time_available(id_time_iter, best_id_room):
                        return best_id_room, id_time_iter

                list_of_remanescent_rooms.remove(best_id_room)
                if list_of_remanescent_rooms:
                    best_id_room = list_of_remanescent_rooms[0]
                    best_rem = \
                        solution.problem.rooms[best_id_room].capacity - \
                        solution.problem.classes[id_class].limit

                if first_iteration:
                    best_id_room_first_iteration = best_id_room
                    first_iteration = False

            solution.classes_not_assigned.append(id_class)
            solution.classes_not_assigned_with_times_rooms_conflict.append(id_class)
            # print("CLASS %d NOT ASSIGNED" % id_class)

            for id_time_iter in list(solution.problem.classes[id_class].times.keys()):
                if solution.problem.rooms[best_id_room_first_iteration].is_time_unavailable(
                        id_time_iter, solution.problem.is_overlap):
                    continue
                id_time = id_time_iter
                found_time_available = True
                break

        if not found_time_available:
            id_time = list(solution.problem.classes[id_class].times.keys())[0]
        list_of_id_classes = solution.conflicting_classes_in_room(id_time, best_id_room_first_iteration)
        for id_class_conflicting in list_of_id_classes:
            solution.classes_conflict.add_conflict_without_check(id_class, id_class_conflicting)
        return best_id_room_first_iteration, id_time
