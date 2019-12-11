# -*- coding: utf-8 -*-

# from algorithms import Algorithm
from typing import Dict, List
from constants import Const
from problem import Problem
from conflict_matrix import ConflictMatrixEsparse
from funcoes_constraints import Constraint
from copy import deepcopy
import random
from functions import *


def is_time_available(
        id_time: int, list_of_unavailables: List[int],
        list_of_times_in_room: List[int],
        is_overlap_function) -> bool:
    if not is_time_unavailable(
            id_time, list_of_unavailables, is_overlap_function) and \
            not is_time_unavailable(
                id_time, list_of_times_in_room, is_overlap_function):
        return True
    return False


def is_time_unavailable(
        id_time: int, list_of_unavailables: List[int],
        is_overlap_function
) -> bool:
    """ Verifica se há conflito de horário entre um horário (id_time) e a
    lista de horários indisponíveis (list_of_unavailables).
    Retorna True caso haja conflito e False, caso contrário.
    """
    return is_time_conflicting_with_list(
        id_time, list_of_unavailables, is_overlap_function)


def is_time_conflicting_with_list(
        id_time: int, list_of_times: List[int],
        is_overlap_function
) -> bool:
    """ Verifica se há conflito de horário entre um horário (id_time) e a
    lista de horários (list_of_times).
    Retorna True caso haja conflito e False, caso contrário.
    """
    if list_of_times:
        for id_time_iter in list_of_times:
            if is_overlap_function(id_time, id_time_iter):
                return True
    return False


def increment_combination_control_for_time_and_room(
        problem: Problem, list_of_id_classes: List[int],
        combination_control_room, processed_rooms,
        combination_control_time, processed_times
) -> bool:
    tam = len(combination_control_time)
    for i, item in enumerate(combination_control_time):
        id_class = list_of_id_classes[(tam - i - 1)]
        if id_class not in processed_times:
            num_of_times = len(problem.classes[id_class].times.keys())
            combination_control_time[(tam - i - 1)] = \
                (combination_control_time[(tam - i - 1)] + 1) % num_of_times
            if combination_control_time[(tam - i - 1)] != 0:
                return True
            else:
                if id_class not in processed_rooms:
                    num_of_rooms = len(problem.classes[id_class].rooms.keys())
                    combination_control_room[(tam - i - 1)] = \
                        (combination_control_room[(tam - i - 1)] + 1) % \
                        num_of_rooms
                    if combination_control_room[(tam - i - 1)] != 0:
                        return True
    return False


def validate_combination_with_times_available(
        problem: Problem, list_of_id_classes: List[int],
        times_in_rooms, processed_rooms, combination_control_room,
        processed_times, combination_control_time
) -> bool:
    for i, id_class_i in enumerate(list_of_id_classes):
        id_time_i = processed_times.get(id_class_i)
        if not id_time_i:
            id_time_i = list(problem.classes[id_class_i].times.keys())[
                combination_control_time[i]]
        id_room_i = processed_rooms.get(id_class_i)
        if not id_room_i:
            id_room_i = list(problem.classes[id_class_i].rooms.keys())[
                combination_control_room[i]]
        if is_time_unavailable(
                id_time_i, problem.rooms[id_room_i].unavailables,
                problem.is_overlap) or \
                is_time_unavailable(
                    id_time_i, times_in_rooms[id_room_i],
                    problem.is_overlap):
            return False
        for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
            id_time_j = processed_times.get(id_class_j)
            if not id_time_j:
                id_time_j = list(problem.classes[id_class_j].times.keys())[
                    combination_control_time[j]]
            id_room_j = processed_rooms.get(id_class_j)
            if not id_room_j:
                id_room_j = list(problem.classes[id_class_j].rooms.keys())[
                    combination_control_room[j]]
            if id_room_i != 0 and \
                id_room_i == id_room_j and \
                    problem.is_overlap(id_time_i, id_time_j):
                return False
    return True


def select_function_by_id_constraint(problem: Problem, type_param):
    function = None

    if type_param == Const.SAME_START:
        function = problem.is_same_start
    elif type_param == Const.SAME_TIME:
        function = problem.is_same_time
    elif type_param == Const.DIFFERENT_TIME:
        function = problem.is_different_time
    elif type_param == Const.SAME_DAYS:
        function = problem.is_same_days
    elif type_param == Const.DIFFERENT_DAYS:
        function = problem.is_different_days
    elif type_param == Const.SAME_WEEKS:
        function = problem.is_same_weeks
    elif type_param == Const.DIFFERENT_WEEKS:
        function = problem.is_different_weeks
    elif type_param == Const.OVERLAP:
        function = problem.is_overlap
    elif type_param == Const.NOT_OVERLAP:
        function = problem.is_not_overlap
    elif type_param == Const.PRECEDENCE:
        function = problem.is_precedence
    elif type_param == Const.SAME_ATTENDEES:
        function = problem.is_same_attendees
    elif type_param == Const.WORK_DAY:
        function = problem.is_work_day
    elif type_param == Const.MIN_GAP:
        function = problem.is_min_gap
    elif type_param == Const.SAME_ROOM:
        function = Constraint.same_room
    elif type_param == Const.DIFFERENT_ROOM:
        function = Constraint.different_room

    return function


def validate_combination_with_rooms_constraint(
        function, list_of_id_classes: List[int],
        processed_rooms
) -> bool:
    return validate_combination_with_times_constraint(
        function, list_of_id_classes, processed_rooms)


def enumerate_rooms_constraint_conflicts(
        function, list_of_id_classes: List[int],
        processed_rooms
):
    return enumerate_times_constraint_conflicts(
        function, list_of_id_classes, processed_rooms)


def validate_combination_with_times_constraint(
        function, list_of_id_classes: List[int],
        processed_times
) -> bool:
    for i, id_class_i in enumerate(list_of_id_classes):
        id_time_i = processed_times.get(id_class_i)
        for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
            id_time_j = processed_times.get(id_class_j)
            if not function(id_time_i, id_time_j):
                return False
    return True


def enumerate_times_constraint_conflicts(
        function, list_of_id_classes: List[int],
        processed_times
):
    conflicts = []
    for i, id_class_i in enumerate(list_of_id_classes):
        for k, id_time_i in enumerate(processed_times.get(id_class_i)):
            for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
                for l, id_time_j in enumerate(processed_times.get(id_class_j)):
                    if not function(id_time_i, id_time_j) and \
                            {(id_class_i, id_time_i),
                             (id_class_j, id_time_j)} not in conflicts:
                        conflicts.append({(id_class_i, id_time_i),
                                          (id_class_j, id_time_j)})
    return conflicts


def validate_combination_with_same_attendees_constraint(
        problem: Problem, list_of_id_classes: List[int],
        processed_rooms, processed_times
) -> bool:
    for i, id_class_i in enumerate(list_of_id_classes):
        id_time_i = processed_times.get(id_class_i)
        id_room_i = processed_rooms.get(id_class_i)
        for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
            id_time_j = processed_times.get(id_class_j)
            id_room_j = processed_rooms.get(id_class_j)
            if not problem.is_same_attendees(id_time_i, id_room_i,
                                             id_time_j, id_room_j):
                return False
    return True


def enumerate_same_attendees_constraint_conflicts(
        problem: Problem, list_of_id_classes: List[int],
        processed_rooms, processed_times
):
    conflicts = []
    for i, id_class_i in enumerate(list_of_id_classes):
        for k, id_time_i in enumerate(processed_times.get(id_class_i)):
            id_room_i = processed_rooms.get(id_class_i)[k]
            for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
                for l, id_time_j in enumerate(processed_times.get(id_class_j)):
                    id_room_j = processed_rooms.get(id_class_j)[l]
                    if id_room_i != id_room_j and not problem.is_same_attendees(
                            id_time_i, id_room_i, id_time_j, id_room_j) and \
                            {(id_class_i, id_time_i, id_room_i),
                             (id_class_j, id_time_j, id_room_j)} not in conflicts:
                        conflicts.append({(id_class_i, id_time_i, id_room_i),
                                          (id_class_j, id_time_j, id_room_j)})
    return conflicts


def validate_combination_with_times_and_slots_constraint(
        function, list_of_id_classes: List[int], s: int,
        processed_times
) -> bool:
    for i, id_class_i in enumerate(list_of_id_classes):
        id_time_i = processed_times.get(id_class_i)
        for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
            id_time_j = processed_times.get(id_class_j)
            if not function(id_time_i, id_time_j, s):
                return False
    return True


def enumerate_times_and_slots_constraint_conflicts(
        function, list_of_id_classes: List[int], s,
        processed_times
):
    conflicts = []
    for i, id_class_i in enumerate(list_of_id_classes):
        for k, id_time_i in enumerate(processed_times.get(id_class_i)):
            for j, id_class_j in enumerate(list_of_id_classes[(i + 1):]):
                for l, id_time_j in enumerate(processed_times.get(id_class_j)):
                    if not function(id_time_i, id_time_j, s) and \
                            {(id_class_i, id_time_i),
                             (id_class_j, id_time_j)} not in conflicts:
                        conflicts.append({(id_class_i, id_time_i),
                                          (id_class_j, id_time_j)})
    return conflicts


def increment_combination_control_for_room(
        problem: Problem, list_of_id_classes, combination_control,
        processed_rooms
) -> bool:
    tam = len(combination_control)
    for i, item in enumerate(combination_control):
        id_class = list_of_id_classes[(tam - i - 1)]
        if id_class not in processed_rooms:
            num_of_rooms = len(problem.classes[id_class].rooms.keys())
            combination_control[(tam - i - 1)] = \
                (combination_control[(tam - i - 1)] + 1) % num_of_rooms
            if combination_control[(tam - i - 1)] != 0:
                return True
    return False


def pick_next_different_room_position(
        list_of_rooms: List[int], list_of_rooms_picked: List[int],
        last_combination: int
) -> int:
    for i, room in enumerate(list_of_rooms[last_combination:]):
        if room not in list_of_rooms_picked:
            return i + last_combination
    return Const.COMBINATION_OVERFLOWED


def pick_next_room_position(list_of_rooms: List[int],
                            last_combination: int) -> int:
    if last_combination < len(list_of_rooms):
        return list_of_rooms[last_combination]
    else:
        return Const.COMBINATION_OVERFLOWED


def pick_next_time_position(
        list_of_id_times: List[int],
        times_in_room: List[int], matrix_conflict: ConflictMatrixEsparse,
        last_combination: int
) -> int:
    for i, id_time in enumerate(list_of_id_times[last_combination:]):
        if not is_time_unavailable(id_time, times_in_room, matrix_conflict):
            return i + last_combination
    return Const.COMBINATION_OVERFLOWED


def pick_valid_combination_different_room(
        list_of_id_classes: List[int],
        list_of_list_of_rooms: List[List[int]],
        list_of_rooms_picked: List[int],
        list_of_last_combinations: List[int],
        processed: Dict[int, int]
) -> List[int]:
    id_room_of_class = processed.get(list_of_id_classes[0])
    while True:
        new_combination = 1  # Inicialização de variável.
        if not id_room_of_class:
            new_combination = \
                pick_next_different_room_position(
                    list_of_list_of_rooms[0], list_of_rooms_picked,
                    list_of_last_combinations[0])
            if new_combination == Const.COMBINATION_OVERFLOWED:
                list_of_last_combinations[0] = 0
                return []
            else:
                list_of_rooms_picked.append(
                    list_of_list_of_rooms[0][new_combination])
                list_of_last_combinations[0] = new_combination
        if len(list_of_id_classes) == 1:
            if not id_room_of_class:
                list_of_rooms_picked.remove(
                    list_of_list_of_rooms[0][new_combination])
            return [new_combination, ]
        else:
            subsequent = pick_valid_combination_different_room(
                list_of_id_classes[1:], list_of_list_of_rooms[1:],
                list_of_rooms_picked, list_of_last_combinations[1:],
                processed)
            if not subsequent:
                list_of_last_combinations[1] = 0
                if id_room_of_class:
                    return []
                else:
                    list_of_rooms_picked.remove(
                        list_of_list_of_rooms[0][new_combination])
                    list_of_last_combinations[0] += 1
            else:
                if not id_room_of_class:
                    list_of_rooms_picked.remove(
                        list_of_list_of_rooms[0][new_combination])
                aux_list = [new_combination, ]
                aux_list.extend(subsequent)
                return aux_list


"""def pick_valid_combination_room_and_time(
        list_of_id_classes: List[int],
        list_of_list_of_rooms: List[List[int]],
        list_of_list_of_times: List[List[int]],
        list_of_times_in_rooms: Dict[int, List[int]],
        list_of_last_combinations: List[List[int]],
        rooms_processed: Dict[int, int],
        times_processed: Dict[int, int],
        matrix_conflict: ConflictMatrixEsparse,
        times_in_rooms_picked: Dict[int, List[int]], function
) -> Tuple[List[int], List[int]]:
    id_room_of_class = rooms_processed.get(list_of_id_classes[0])
    id_time_of_class = times_processed.get(list_of_id_classes[0])
    while True:
        new_combination_room = 1  # Inicialização de variável.
        new_combination_time = 1  # Inicialização de variável.

        new_id_room = id_room_of_class
        if not id_room_of_class:
            new_combination_room = \
                pick_next_room_position(
                    list_of_list_of_rooms[0], list_of_last_combinations[0][0])
            list_of_last_combinations[0][0] = new_combination_room
            if new_combination_room == Const.COMBINATION_OVERFLOWED:
                return [], []
            new_id_room = list_of_list_of_rooms[0][new_combination_room]

        times_in_room = list_of_times_in_rooms[new_id_room]
        new_id_time = id_time_of_class
        if not id_time_of_class:
            new_combination_time = \
                pick_next_time_position(
                    list_of_list_of_times[0], times_in_room,
                    matrix_conflict, list_of_last_combinations[0][1])
            list_of_last_combinations[0][1] = new_combination_time
            if new_combination_time == Const.COMBINATION_OVERFLOWED:
                if id_room_of_class:
                    return [], []
                list_of_last_combinations[0][0] += 1
                continue  # Volta ao início do while pra tentar achar outra
                            # sala que seja compatível.
            new_id_time = list_of_list_of_times[0][new_combination_time]

        list_of_times_in_rooms[new_id_room].append(new_id_time)

        if len(list_of_id_classes) == 1:
            return [new_combination_room, ], [new_combination_time, ]
        else:
            subsequent_room, subsequent_time = \
                pick_valid_combination_room_and_time(
                    list_of_id_classes[1:], list_of_list_of_rooms[1:],
                    list_of_list_of_times[1:], list_of_times_in_rooms,
                    list_of_last_combinations[1:], rooms_processed,
                    times_processed, matrix_conflict, times_in_rooms_picked,
                    function
                )
            if not subsequent_room:
                list_of_last_combinations[1][0] = 0
                list_of_last_combinations[1][1] = 0
                if id_room_of_class and id_time_of_class:
                    return [], []
                elif id_time_of_class:
                    list_of_last_combinations[0][0] += 1
                else:
                    list_of_last_combinations[0][1] += 1
            else:

                if not id_room_of_class:
                    list_of_rooms_picked.remove(
                        list_of_list_of_rooms[0][new_combination_room])
                aux_list = [new_combination_room, ]
                aux_list.extend(subsequent)
                return aux_list
"""


class CombinationsClassesDistribution:
    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.combination_control = {}

    def get_next_valid_combination_for_same_room(
            self, id_constraint: int,
            processed: Dict[int, int]
    ) -> int:
        constraint = self.problem.constraints[(id_constraint - 1)]
        list_of_id_classes = constraint.classes

        first_room_found_in_processed = 0
        for id_class in list_of_id_classes:
            room_of_class = processed.get(id_class)
            if room_of_class:
                if not first_room_found_in_processed:
                    first_room_found_in_processed = room_of_class
                elif room_of_class != first_room_found_in_processed:
                    return Const.COMBINATION_INFEASIBLE

        list_of_rooms = []
        for id_class in list_of_id_classes:
            list_of_rooms.append(list(self.problem.classes[id_class].rooms.keys()))
        intersection_rooms = intersection(list_of_rooms)

        if first_room_found_in_processed:
            if first_room_found_in_processed in intersection_rooms:
                return first_room_found_in_processed
            else:
                return Const.COMBINATION_INFEASIBLE

        last_combination = self.combination_control.get(id_constraint)
        if not last_combination:
            new_combination = 1
        else:
            new_combination = last_combination + 1

        self.combination_control[id_constraint] = new_combination

        if new_combination > len(intersection_rooms):
            return Const.COMBINATION_OVERFLOWED  # Todas as combinações foram esgotadas.

        return intersection_rooms[(new_combination - 1)]

    def get_next_valid_combination_for_different_room(
            self, id_constraint: int,
            processed: Dict[int, int]
    ) -> List[int]:
        constraint = self.problem.constraints[(id_constraint - 1)]
        list_of_id_classes = constraint.classes
        num_of_classes = len(list_of_id_classes)

        list_of_rooms_processed = []
        list_of_list_of_rooms = []
        for id_class in list_of_id_classes:
            room_of_class = processed.get(id_class)
            if room_of_class:
                if room_of_class in list_of_rooms_processed:
                    return []
                list_of_rooms_processed.append(room_of_class)
            list_of_list_of_rooms.append(list(self.problem.classes[id_class].rooms.keys()))

        if len(list_of_rooms_processed) == num_of_classes:
            return [0] * num_of_classes  # Todas as turmas já estão alocadas!

        list_of_last_combinations = deepcopy(self.combination_control.get(id_constraint))
        if not list_of_last_combinations:
            list_of_last_combinations = [0] * num_of_classes

        list_of_new_combinations = pick_valid_combination_different_room(
            list_of_id_classes, list_of_list_of_rooms, list_of_rooms_processed,
            list_of_last_combinations, processed)

        if list_of_new_combinations:
            list_of_last_combinations = deepcopy(list_of_new_combinations)
            tam = len(list_of_new_combinations)
            for i, item in enumerate(list_of_new_combinations):
                id_class = list_of_id_classes[(tam - i - 1)]
                if not processed.get(id_class):
                    list_of_last_combinations[(tam - i - 1)] += 1
                    break

            self.combination_control[id_constraint] = list_of_last_combinations
        return list_of_new_combinations

    def get_valid_combination(self, rand=True) -> None:
        pass


class CombinationClass:
    def __init__(self, id_param: int, list_of_id_rooms: List[int],
                 list_of_id_times: List[int], increment_mode: int = 1) -> None:
        self.id = id_param
        self.list_of_id_rooms = list_of_id_rooms
        self.nr_rooms = len(self.list_of_id_rooms)
        self.list_of_id_times = list_of_id_times
        self.nr_times = len(self.list_of_id_times)
        self.next_room = -1  # Controle de combinação de salas da turma
        self.next_time = -1  # Controle de combinação de horários da turma
        self.increment_mode = increment_mode
        if increment_mode == 1:
            self.increment_mode_function = \
                self.__increment_combination_iterating_by_time_first
        else:
            self.increment_mode_function = \
                self.__increment_combination_iterating_by_room_first

    def clear_combination(self):
        self.next_room = 0
        self.next_time = 0

    def rand_index_of_rooms(self):
        random.shuffle(self.list_of_id_rooms)

    def rand_index_of_times(self):
        random.shuffle(self.list_of_id_times)

    @property
    def room(self) -> int:
        return self.list_of_id_rooms[self.next_room]

    @property
    def time(self) -> int:
        return self.list_of_id_times[self.next_time]

    def __increment_combination_iterating_by_room_first(
            self, problem: Problem,
            list_of_id_times_per_room: Dict[int, List[int]]) -> bool:
        id_time = self.list_of_id_times[self.next_time]
        while True:  # Altera room e time até encontrar valores sem conflitos.
            self.next_room = (self.next_room + 1) % self.nr_rooms
            if self.next_room == 0:
                self.next_time = (self.next_time + 1) % self.nr_times
                if self.next_time == 0:
                    return False
                id_time = self.list_of_id_times[self.next_time]
            id_room = self.list_of_id_rooms[self.next_room]
            if not id_room:
                return True
            list_of_unavailables = problem.rooms[id_room].unavailables
            list_of_times_in_room = list_of_id_times_per_room.get(id_room)

            if is_time_available(id_time, list_of_unavailables,
                                 list_of_times_in_room,
                                 problem.is_overlap):
                return True

    def __increment_combination_iterating_by_time_first(
            self, problem: Problem,
            list_of_id_times_per_room: Dict[int, List[int]]) -> bool:
        id_room = self.list_of_id_rooms[self.next_room]
        while True:
            self.next_time = (self.next_time + 1) % self.nr_times
            if self.next_time == 0:
                self.next_room = (self.next_room + 1) % self.nr_rooms
                if self.next_room == 0:
                    return False
                id_room = self.list_of_id_rooms[self.next_room]
            if not id_room:
                return True
            id_time = self.list_of_id_times[self.next_time]
            list_of_unavailables = problem.rooms[id_room].unavailables
            list_of_times_in_room = list_of_id_times_per_room.get(id_room)

            if is_time_available(id_time, list_of_unavailables,
                                 list_of_times_in_room,
                                 problem.is_overlap):
                return True

    def start_combination(
            self, problem: Problem,
            list_of_id_times_per_room: Dict[int, List[int]]) -> bool:
        self.clear_combination()
        id_time = self.list_of_id_times[self.next_time]
        id_room = self.list_of_id_rooms[self.next_room]
        if not id_room:
            return True
        list_of_unavailables = problem.rooms[id_room].unavailables
        list_of_times_in_room = list_of_id_times_per_room.get(id_room)
        if is_time_available(id_time, list_of_unavailables,
                             list_of_times_in_room,
                             problem.is_overlap):
            return True
        return self.increment_combination(problem, list_of_id_times_per_room)

    def increment_combination(
            self, problem: Problem,
            list_of_id_times_per_room: Dict[int, List[int]]) -> bool:
        return self.increment_mode_function(problem, list_of_id_times_per_room)

    def __str__(self) -> str:
        return "C%d, NR_ROOMS: %d, NR_TIMES: %d, NEXT_ROOM: %d, NEXT_TIME: %d" % \
               (self.id, self.nr_rooms, self.nr_times, self.next_room, self.next_time)
