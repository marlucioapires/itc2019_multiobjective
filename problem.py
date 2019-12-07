# -*- coding: utf-8 -*-

from copy import deepcopy
from conflict_matrix import ConflictMatrixEsparse
from typing import Dict, Tuple, List
import random
# import math
from constants import Const
import itertools
import networkx as nx
from funcoes_constraints import Constraint
from functions import number_of_combinations, verify_is_time_conflicting_with_list,\
    combinations_of_two_lists, intersection_list


class Student:
    def __init__(self, id_param: int) -> None:
        self.id = id_param
        self.courses = []

    def add_course(self, id_course: int) -> None:
        self.courses.append(id_course)

    def __str__(self) -> str:
        str_return = 'Student id="%d"' % self.id
        str_return += '\n\tCourses: "%s"' % str(self.courses)
        return str_return


class TimeTuple:
    def __init__(self, id_param: int, days: int, start: int, length: int, weeks: int,
                 penalty: int = 0) -> None:
        self.id = id_param
        self.days = days
        self.start = start
        self.length = length
        self.end = start + length
        self.weeks = weeks
        self.penalty = penalty

    def __str__(self) -> str:
        return "<time days=\"%s\" start=\"%s\" length=\"%s\" weeks=\"%s\" penalty=\"%s\"/>" % (
            "{0:07b}".format(self.days),
            self.start,
            self.length,
            "{0:016b}".format(self.weeks),
            self.penalty)

    def str_to_xml(self, nr_days: int, nr_weeks: int) -> str:
        return "<time days=\"%s\" start=\"%d\" length=\"%d\" weeks=\"%s\" penalty=\"%d\"/>" % (
            "{0:b}".format(self.days).zfill(nr_days),
            self.start,
            self.length,
            "{0:b}".format(self.weeks).zfill(nr_weeks),
            self.penalty)


class Class:
    def __init__(self, id_param: int, limit: int, room: bool = True) -> None:
        self.id = id_param
        self.limit = limit
        self.room = room
        self.parent = None
        self.childs = []
        self.times = {}
        self.rooms = {}

    def add_time(self, id_time: int, time_tuple: TimeTuple) -> None:
        self.times[id_time] = time_tuple

    def add_room(self, id_room: int, penalty: int = 0) -> None:
        self.rooms[id_room] = penalty

    def fit(self, minimum: int = 1, percent: float = 0.9) -> None:
        nr_rooms = len(self.rooms)
        if nr_rooms > minimum:
            nr_exclusions = int(round(percent * nr_rooms))
            if nr_exclusions == nr_rooms:
                nr_exclusions -= 1
            if nr_rooms - nr_exclusions < minimum:
                nr_exclusions = nr_rooms - minimum
            list_of_rooms = list(self.rooms.keys())
            list_of_exclusions = []
            for i in range(0, nr_exclusions):
                pos = random.randint(0, (len(list_of_rooms) - 1))
                list_of_exclusions.append(list_of_rooms[pos])
                del list_of_rooms[pos]
            for key in list_of_exclusions:
                del self.rooms[key]
        nr_times = len(self.times)
        if nr_times > minimum:
            nr_exclusions = int(round(percent * nr_times))
            if nr_exclusions == nr_times:
                nr_exclusions -= 1
            if nr_times - nr_exclusions < minimum:
                nr_exclusions = nr_times - minimum
            list_of_times = list(self.times.keys())
            list_of_exclusions = []
            for i in range(0, nr_exclusions):
                pos = random.randint(0, (len(list_of_times) - 1))
                list_of_exclusions.append(list_of_times[pos])
                del list_of_times[pos]
            for key in list_of_exclusions:
                del self.times[key]

    def __str__(self) -> str:
        str_return = '\tClass id="%d", limit="%d"' % (self.id, self.limit)
        str_return += ', room="false"' if not self.room else ''
        str_return += ', parent="%s"' % str(self.parent) if self.parent else ''
        str_return += ', childs="%s"' % str(self.childs) if self.childs else ''
        str_return += '\n\tTimes ="%d", Rooms="%d"' % (
            len(self.times), len(self.rooms))
        return str_return


class Subpart:
    def __init__(self, id_param: int) -> None:
        self.id = id_param
        self.classes = {}

    def add_class(self, obj_class: Class) -> None:
        self.classes[obj_class.id] = obj_class

    def __str__(self) -> str:
        str_return = 'Subpart id="%d"' % self.id
        for c in self.classes.values():
            str_return += '\n' + str(c)
        return str_return


class Config:
    def __init__(self, id_param: int) -> None:
        self.id = id_param
        self.subparts = {}

    def add_subpart(self, subpart: Subpart) -> None:
        self.subparts[subpart.id] = subpart

    def __str__(self) -> str:
        str_return = 'Config id="%d"' % self.id
        for s in self.subparts.values():
            str_return += '\n' + str(s)
        return str_return


class Course:
    def __init__(self, id_param: int) -> None:
        self.id = id_param
        self.configs = {}
        self.max_class_combination = 0

    def add_config(self, config: Config) -> None:
        self.configs[config.id] = config

    def __str__(self) -> str:
        str_return = 'Course id="%d"' % self.id
        for c in self.configs.values():
            str_return += '\n' + str(c)
        return str_return


class Room:
    def __init__(self, id_param: int, capacity: int) -> None:
        self.id = id_param
        self.capacity = capacity
        self.travels = {}
        self.unavailables = []

    def add_travel(self, id_room: int, value: int) -> None:
        self.travels[id_room] = value

    def add_unavailable(self, id_unavailable: int) -> None:
        self.unavailables.append(id_unavailable)

    def __str__(self) -> str:
        return 'Room id="%d", capacity="%s"' % (self.id, str(self.capacity))

    def is_time_unavailable(self, id_time: int,
                            is_overlap_function) -> bool:
        """ Verifica se há conflito de horário entre um horário (time) e a
        lista de horários indisponíveis (self.unavailables) da room (sala).
        Retorna True caso haja conflito e False, caso contrário.
        """
        for id_unavailable in self.unavailables:
            if is_overlap_function(id_time, id_unavailable):
                return True
        return False


class DistributionConstraint:
    def __init__(self, id_param: int, type_param: int, required: bool = False,
                 penalty: int = 0, list_of_params: List[int] = None) -> None:
        self.id = id_param
        self.type = type_param
        self.required = required
        self.penalty = penalty
        self.classes = []
        self.list_of_params = list_of_params

    def __str__(self) -> str:
        str_return = 'Distribution:"'
        str_return += '\n\tClass: "%s"' % str(self.classes)
        return str_return


class Problem:
    def __init__(self, name: str = None, nr_days: int = 0, nr_weeks: int = 0,
                 slots_per_day: int = 0, weight_time: int = 1,
                 weight_room: int = 1, weight_distribution: int = 1,
                 weight_student: int = 1, max_penalties: int = 0) -> None:
        self.name = name
        self.nr_days = nr_days
        self.nr_weeks = nr_weeks
        self.slots_per_day = slots_per_day
        self.weight_time = weight_time
        self.weight_room = weight_room
        self.weight_distribution = weight_distribution
        self.weight_student = weight_student
        self.max_penalties = max_penalties
        self.conflict_ids_matrix = \
            ConflictMatrixEsparse()
        self.ids_count = 0
        self.id_to_time = {}
        self.id_time_to_time_tuple = {}
        self.time_to_id = {}
        self.times_travel_rooms = {}
        self.number_rooms_by_class = {}
        self.rooms = {}
        self.courses = {}
        self.classes = {}  # Permite o acesso direto às classes do problema
        self.distributions_hard = []
        self.distributions_soft = []
        self.constraints = []
        self.dict_constraints_by_id = {}
        self.constraints_conflict_matrix = []
        self.constraints_index = []  # Lista de índices para ordenação indireta.
        self.students = {}
        self.classes_per_student = {}
        self.combinations_per_course = {}
        self.classes_per_combination = {}
        self.combinations_per_student = {}
        self.classes_combinations_per_course = {}
        self.dict_list_id_combinations_per_id_course = {}
        self.dict_list_id_classes_per_id_combination = {}
        self.constraints_per_class = {}  # Permite o acesso às distributions constraints por classes
        self.fixed_classes = []
        self.number_of_fixed_classes = 0
        self.number_of_parcial_fixed_classes = 0
        self.number_of_not_fixed_classes = 0
        self.number_of_no_need_room_classes = 0
        self.not_fixed_classes = []
        self.group_subproblems = {}

        self.dict_neighborhood_coefficient_id_to_id = {}
        self.dict_neighborhood_coefficient_id_to_value = {}

        self.neighborhood_coefficient = {}

        # self.is_same_start = self.__verify_same_start
        # self.is_same_time = self.__verify_same_time
        # self.is_different_time = self.__verify_different_time
        # self.is_same_days = self.__verify_same_days
        # self.is_different_days = self.__verify_different_days
        # self.is_same_weeks = self.__verify_same_weeks
        # self.is_different_weeks = self.__verify_different_weeks
        # self.is_overlap = self.__verify_overlap
        # self.is_not_overlap = self.__verify_not_overlap
        # self.is_precedence = self.__verify_precedence
        # self.is_same_attendees = self.__verify_same_attendees
        # self.is_work_day = self.__verify_work_day
        # self.is_min_gap = self.__verify_min_gap

        self.is_same_start = self.verify_same_start
        self.is_same_time = self.verify_same_time
        self.is_different_time = self.verify_different_time
        self.is_same_days = self.verify_same_days
        self.is_different_days = self.verify_different_days
        self.is_same_weeks = self.verify_same_weeks
        self.is_different_weeks = self.verify_different_weeks
        self.is_overlap = self.verify_overlap
        self.is_not_overlap = self.verify_not_overlap
        self.is_precedence = self.verify_precedence
        self.is_same_attendees = self.verify_same_attendees
        self.is_work_day = self.verify_work_day
        self.is_min_gap = self.verify_min_gap

        # self.union_rooms_of_classes = self.__calculate_union_rooms_of_classes
        # self.intersection_rooms_of_classes = self.__calculate_intersection_rooms_of_classes

        # self.possible_times_per_room_and_class = self.__calculate_possible_id_times_per_room_and_class

        self.union_rooms_of_classes = self.calculate_union_rooms_of_classes
        self.intersection_rooms_of_classes = self.calculate_intersection_rooms_of_classes

        self.possible_times_per_room_and_class = self.calculate_possible_id_times_per_room_and_class

        # self.hard_distribution_independent_groups = []
        # self.classes_of_hard_dist_independent_groups = []

        self.same_room_constraints = {}

        self.course_dict_int_id_to_str_id = {}
        self.course_dict_str_id_to_int_id = {}

        self.config_dict_int_id_to_str_id = {}

        self.subpart_dict_int_id_to_str_id = {}

        self.class_dict_int_id_to_str_id = {}
        self.class_dict_str_id_to_int_id = {}

        self.room_dict_int_id_to_str_id = {}
        self.room_dict_str_id_to_int_id = {}

        self.student_dict_int_id_to_str_id = {}

        self.classes_combinations_per_student = {}

        # As estruturas a seguir são específicas para a resolução do problema
        # através do modelo de programação inteira.

        self.ids_times = []
        self.ids_rooms = []

        self.list_of_ids_unavailables_by_id_room = {}

        self.ids_classes = []
        self.penalties_times_rooms = {}

        self.list_of_ids_times_by_id_class = {}
        self.list_of_ids_rooms_by_id_class = {}
        self.limits_per_class = {}

        self.ids_constraints = []
        self.list_of_ids_hard_constraints_by_type = {}
        self.list_of_ids_soft_constraints_by_type = {}
        self.list_of_ids_classes_by_id_constraint = {}
        self.penalties_soft_constraints = {}

        self.matrix_classes_per_combination = set()
        self.matrix_combination_per_course = set()

        self.matrix_same_start = ConflictMatrixEsparse()
        self.matrix_same_time = ConflictMatrixEsparse()
        self.matrix_different_time = ConflictMatrixEsparse()
        self.matrix_same_days = ConflictMatrixEsparse()
        self.matrix_different_days = ConflictMatrixEsparse()
        self.matrix_same_weeks = ConflictMatrixEsparse()
        self.matrix_different_weeks = ConflictMatrixEsparse()
        self.matrix_precedence = ConflictMatrixEsparse()
        self.matrix_work_day = ConflictMatrixEsparse()
        self.matrix_min_gap = ConflictMatrixEsparse()

        self.matrix_same_attendees = ConflictMatrixEsparse()
        self.matrix_not_overlap = ConflictMatrixEsparse()
        self.matrix_overlap = ConflictMatrixEsparse()

        self.matrix_intersection_rooms_of_classes = {}
        self.matrix_union_rooms_of_classes = {}
        self.union_less_intersection_rooms_of_classes = {}

        self.matrix_possible_times_per_room_and_class = None

    def add_room(self, room: Room) -> None:
        self.rooms[room.id] = room
        for id_travel_room, value in room.travels.items():
            self.times_travel_rooms[room.id, id_travel_room] = value
            self.times_travel_rooms[id_travel_room, room.id] = value
        self.list_of_ids_unavailables_by_id_room[room.id] = []

        # Adicionando a sala às estruturas do MIP
        self.ids_rooms.append(room.id)
        for id_unavailable in room.unavailables:
            self.list_of_ids_unavailables_by_id_room[room.id].append(id_unavailable)

    def add_course(self, course: Course) -> None:
        self.courses[course.id] = course
        conjunto = []
        for config in course.configs.values():
            aux = []
            self.__make_class_combinations(conjunto, aux, list(config.subparts.values()))
        max_length_combination = 0
        for comb in conjunto:
            if len(comb) > max_length_combination:
                max_length_combination = len(comb)
        course.max_class_combination = max_length_combination
        self.classes_combinations_per_course[course.id] = conjunto

    def generate_ids_for_course_combinations(self):
        count_aux = 1
        for id_course, list_of_combinations in self.classes_combinations_per_course.items():
            nr_combinations = len(list_of_combinations)
            self.dict_list_id_combinations_per_id_course[id_course] = \
                [id_combination for id_combination in range(count_aux, (nr_combinations + count_aux))]
            count_aux += nr_combinations
            for i, id_combination in enumerate(self.dict_list_id_combinations_per_id_course[id_course]):
                self.dict_list_id_classes_per_id_combination[id_combination] = list_of_combinations[i]

    def generate_combinations_of_id_classes_by_id_student(self, id_student: int):
        obj_student = self.students.get(id_student)
        if not obj_student or len(obj_student.courses) == 0:
            return []
        first_id_course_of_student = obj_student.courses[0]
        list_final = \
            [[id_combination, ] for id_combination in
             self.dict_list_id_combinations_per_id_course[first_id_course_of_student]]
        for id_course in obj_student.courses[1:]:
            list_final = combinations_of_two_lists(
                list_final, self.dict_list_id_combinations_per_id_course[id_course])
        list_combinations_of_id_classes = []
        for list_of_id_combinations in list_final:
            list_aux = []
            for id_combination in list_of_id_combinations:
                list_aux.extend(list(self.dict_list_id_classes_per_id_combination[id_combination]))
            list_combinations_of_id_classes.append(list_aux)
        return list_combinations_of_id_classes

    def generate_list_of_possible_id_classes_by_id_student(self, id_student: int):
        list_combinations_of_id_classes = \
            self.generate_combinations_of_id_classes_by_id_student(id_student)
        set_of_id_classes = set()
        for list_of_id_classes in list_combinations_of_id_classes:
            for id_class in list_of_id_classes:
                set_of_id_classes.add(id_class)
        return list(set_of_id_classes)

    def generate_int_id_room(self, str_id_room: str) -> int:
        int_id = len(self.room_dict_int_id_to_str_id) + 1
        self.room_dict_int_id_to_str_id[int_id] = str_id_room
        self.room_dict_str_id_to_int_id[str_id_room] = int_id
        return int_id

    def generate_int_id_course(self, str_id_course: str) -> int:
        int_id = len(self.course_dict_int_id_to_str_id) + 1
        self.course_dict_int_id_to_str_id[int_id] = str_id_course
        self.course_dict_str_id_to_int_id[str_id_course] = int_id
        return int_id

    def generate_int_id_config(self, str_id_config: str) -> int:
        int_id = len(self.config_dict_int_id_to_str_id) + 1
        self.config_dict_int_id_to_str_id[int_id] = str_id_config
        return int_id

    def generate_int_id_subpart(self, str_id_subpart: str) -> int:
        int_id = len(self.subpart_dict_int_id_to_str_id) + 1
        self.subpart_dict_int_id_to_str_id[int_id] = str_id_subpart
        return int_id

    def generate_int_id_class(self, str_id_class):
        int_id = len(self.class_dict_int_id_to_str_id) + 1
        self.class_dict_int_id_to_str_id[int_id] = str_id_class
        self.class_dict_str_id_to_int_id[str_id_class] = int_id
        return int_id

    def generate_int_id_student(self, str_id_student):
        int_id = len(self.student_dict_int_id_to_str_id) + 1
        self.student_dict_int_id_to_str_id[int_id] = str_id_student
        return int_id

    def __make_class_combinations(self, conjunto, aux, subparts):
        if not subparts:
            conjunto.append(aux)
        else:
            for c in subparts[0].classes.values():
                if not c.parent or c.parent in aux:
                    aux_copy = deepcopy(aux)  # faz uma cópia da lista
                    aux_copy.append(c.id)
                    self.__make_class_combinations(conjunto, aux_copy, subparts[1:])

    def __make_class_combinations_per_student(self, id_student: int) -> List[List[int]]:
        student = self.students[id_student]
        list_of_courses = student.courses
        if not len(list_of_courses):
            return []

        curso_1 = list_of_courses[0]
        classes_combinations_per_student = deepcopy(
            self.classes_combinations_per_course[curso_1])
        count = 1
        while list_of_courses[count:]:
            aux1 = deepcopy(classes_combinations_per_student)
            for iter_combination, list_of_classes in enumerate(aux1):
                for list_of_classes_2 in self.classes_combinations_per_course[list_of_courses[count]][1:]:
                    aux = deepcopy(list_of_classes)
                    aux.extend(list_of_classes_2)
                    classes_combinations_per_student.append(aux)
                classes_combinations_per_student[iter_combination].extend(
                    self.classes_combinations_per_course[list_of_courses[count]][0])
            count += 1
        return classes_combinations_per_student

    def add_time_tuple(self, id_time: int, time_tuple: TimeTuple) -> None:
        if id_time not in list(self.id_time_to_time_tuple.keys()):
            self.id_time_to_time_tuple[id_time] = time_tuple

    def add_class(self, obj_class):
        self.classes[obj_class.id] = obj_class
        self.limits_per_class[obj_class.id] = obj_class.limit
        if obj_class.parent:
            self.classes[obj_class.parent].childs.append(obj_class.id)
        nr_rooms = len(obj_class.rooms)
        if nr_rooms:
            if nr_rooms in self.number_rooms_by_class.keys():
                self.number_rooms_by_class[nr_rooms].append(obj_class.id)
            else:
                self.number_rooms_by_class[nr_rooms] = [obj_class.id, ]

        # Lógica para construção do grupo de subproblemas:
        is_present = False
        list_of_groups = []
        for room in obj_class.rooms.keys():
            for g, list_of_rooms in self.group_subproblems.items():
                if room in list_of_rooms:
                    list_of_groups.append(g)
                    is_present = True

        if not is_present:
            self.group_subproblems[len(list_of_groups) + 1] = list(obj_class.rooms.keys())
        else:
            for g in list_of_groups:
                self.group_subproblems[g].extend(list(obj_class.rooms.keys()))

        nr_times = len(obj_class.times)
        if nr_rooms <= 1 and nr_times == 1:
            self.fixed_classes.append(obj_class.id)
            self.number_of_fixed_classes += 1
        else:
            if not obj_class.room:
                self.number_of_no_need_room_classes += 1
            elif nr_rooms <= 1 or nr_times == 1:
                self.number_of_parcial_fixed_classes += 1
            else:
                self.number_of_not_fixed_classes += 1
            self.not_fixed_classes.append(obj_class.id)

        # Adicionando a turma às estruturas do MIP
        self.ids_classes.append(obj_class.id)
        self.list_of_ids_times_by_id_class[obj_class.id] = list(obj_class.times.keys())
        self.list_of_ids_rooms_by_id_class[obj_class.id] = list(obj_class.rooms.keys())
        dict_times_penalties = {}
        for id_time, time_tuple in obj_class.times.items():
            dict_times_penalties[id_time] = time_tuple.penalty
        self.penalties_times_rooms[obj_class.id] = [dict_times_penalties, ]
        dict_rooms_penalties = {}
        for id_room, room_penalty in obj_class.rooms.items():
            dict_rooms_penalties[id_room] = room_penalty
        self.penalties_times_rooms[obj_class.id].append(dict_rooms_penalties)

    def add_constraint(self, constraint: DistributionConstraint):
        self.dict_constraints_by_id[constraint.id] = constraint
        if constraint.required:
            self.distributions_hard.append(constraint)
        else:
            self.distributions_soft.append(constraint)
        self.constraints_index.append(len(self.constraints))
        self.constraints.append(constraint)

        # Adicionando a restição às estruturas do MIP
        id_constraint = len(self.list_of_ids_classes_by_id_constraint) + 1
        self.ids_constraints.append(id_constraint)
        self.list_of_ids_classes_by_id_constraint[id_constraint] = constraint.classes

        if constraint.required:  # A constraint é hard!
            if constraint.type not in self.list_of_ids_hard_constraints_by_type:
                self.list_of_ids_hard_constraints_by_type[constraint.type] = [id_constraint, ]
            else:
                self.list_of_ids_hard_constraints_by_type[constraint.type].append(id_constraint)
        else:
            if constraint.type not in self.list_of_ids_soft_constraints_by_type:
                self.list_of_ids_soft_constraints_by_type[constraint.type] = [id_constraint, ]
            else:
                self.list_of_ids_soft_constraints_by_type[constraint.type].append(id_constraint)
            self.penalties_soft_constraints[id_constraint] = constraint.penalty

    def get_constraint_by_index(self, index):
        return self.constraints[self.constraints_index[index]]

    def add_student(self, student: Student) -> None:
        self.students[student.id] = student

    def select_id_time_compatible_with_room(self, id_class, id_room):
        obj_class = self.classes[id_class]
        for id_time in obj_class.times.keys():
            if not self.rooms[id_room].is_time_unavailable(
                    id_time, self.is_overlap):
                return id_time
        return 0

    def select_random_id_time_compatible_with_room(
            self, id_class: int, id_room: int) -> int:
        obj_class = self.classes[id_class]
        id_time = random.choice(list(obj_class.times.keys()))
        if not self.rooms[id_room].is_time_unavailable(
                id_time, self.is_overlap):
            return id_time
        return 0

    def remove_redundancies_of_instances(self):
        pass

    def make_dict_conflict_ids(self):
        for i in self.id_to_time.keys():
            self.conflict_ids_matrix.add_conflict(i, i)
            for j in list(self.id_to_time.keys())[(i + 1):]:
                tupla = self.id_to_time.get(i)
                t1_start = int(tupla[0])
                t1_length = int(tupla[1])
                t1_end = t1_start + t1_length
                t1_days = int(tupla[2], 2)
                t1_weeks = int(tupla[3], 2)

                tupla = self.id_to_time.get(j)
                t2_start = int(tupla[0])
                t2_length = int(tupla[1])
                t2_end = t2_start + t2_length
                t2_days = int(tupla[2], 2)
                t2_weeks = int(tupla[3], 2)
                if Constraint.overlap(t1_start, t1_end, t2_start, t2_end, t1_days,
                                      t2_days, t1_weeks, t2_weeks):
                    self.conflict_ids_matrix.add_conflict(i, j)
                else:
                    self.matrix_overlap.add_conflict(i, j)
        self.matrix_not_overlap = self.conflict_ids_matrix
        self.is_overlap = self.__verify_overlap_with_matrix
        self.is_not_overlap = self.__verify_not_overlap_with_matrix

    """def generate_dict_list_of_id_classes_per_room(self):
        dict_list_of_id_classes_per_room = {}
        for obj_class in self.classes.values():
            for id_room in obj_class.rooms.keys():
                if id_room not in dict_list_of_id_classes_per_room:
                    dict_list_of_id_classes_per_room[id_room] = []
                dict_list_of_id_classes_per_room[id_room].append(obj_class.id)
        return dict_list_of_id_classes_per_room"""

    def generate_dict_list_of_id_classes_per_room(self, list_of_id_classes):
        dict_list_of_id_classes_per_room = {}
        for id_class in list_of_id_classes:
            obj_class = self.classes[id_class]
            for id_room in obj_class.rooms.keys():
                if id_room not in dict_list_of_id_classes_per_room:
                    dict_list_of_id_classes_per_room[id_room] = []
                dict_list_of_id_classes_per_room[id_room].append(obj_class.id)
        return dict_list_of_id_classes_per_room

    def generate_same_attendees_ids_per_slot_in_a_room(self, list_of_ids_classes, id_room):
        dict_start_ids_per_week_day_and_slot = {}
        dict_end_ids_per_week_day_and_slot = {}
        for id_class in list_of_ids_classes:
            if id_room not in self.classes[id_class].rooms.keys():
                continue
            for id_time, time_tuple in self.classes[id_class].times.items():
                if self.__verify_is_time_unavailable(
                        id_time, id_room):
                    continue
                slot_start = time_tuple.start
                slot_end = time_tuple.end
                id_time_days = time_tuple.days
                id_time_weeks = time_tuple.weeks

                for w in range(self.nr_weeks):
                    str_2_w = ('{0:0' + str(self.nr_weeks) + 'b}').format(0)
                    str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]
                    binary_2_w = int(str_2_w, 2)

                    for d in range(self.nr_days):
                        str_2_d = ('{0:0' + str(self.nr_days) + 'b}').format(0)
                        str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]
                        binary_2_d = int(str_2_d, 2)

                        if ((id_time_days & binary_2_d != 0) and
                                (id_time_weeks & binary_2_w != 0)):
                            if ((w + 1), (d + 1), slot_start) not in \
                                    dict_start_ids_per_week_day_and_slot:
                                dict_start_ids_per_week_day_and_slot[
                                    ((w + 1), (d + 1), slot_start)] = set()
                            dict_start_ids_per_week_day_and_slot[
                                ((w + 1), (d + 1), slot_start)].add(
                                (id_class, id_time, id_room))
                            if ((w + 1), (d + 1), slot_end) not in \
                                    dict_end_ids_per_week_day_and_slot:
                                dict_end_ids_per_week_day_and_slot[
                                    ((w + 1), (d + 1), slot_end)] = set()
                            dict_end_ids_per_week_day_and_slot[
                                ((w + 1), (d + 1), slot_end)].add(
                                (id_class, id_time, id_room))

        return dict_start_ids_per_week_day_and_slot, dict_end_ids_per_week_day_and_slot

    def generate_same_attendees_ids_per_slot_in_a_room_v2(self, list_of_ids_classes, id_room):
        # input("PRESS ENTER...")
        dict_start_ids_per_week_day_and_slot = {}
        dict_end_ids_per_week_day_and_slot = {}

        dict_min_slot_start_per_week_day_and_slot = {}
        dict_min_slot_end_per_week_day_and_slot = {}
        for id_class in list_of_ids_classes:
            if id_room not in self.classes[id_class].rooms.keys():
                continue
            for id_time, time_tuple in self.classes[id_class].times.items():
                if self.__verify_is_time_unavailable(id_time, id_room):
                    continue
                # print("ID DA TURMA: %d" % id_class)
                # print("TIME TUPLE: %s" % str(time_tuple))
                # input("PRESS ENTER...")
                slot_start = time_tuple.start
                slot_end = time_tuple.end
                id_time_days = time_tuple.days
                id_time_weeks = time_tuple.weeks

                for w in range(self.nr_weeks):
                    str_2_w = ('{0:0' + str(self.nr_weeks) + 'b}').format(0)
                    str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]
                    binary_2_w = int(str_2_w, 2)

                    for d in range(self.nr_days):
                        str_2_d = ('{0:0' + str(self.nr_days) + 'b}').format(0)
                        str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]
                        binary_2_d = int(str_2_d, 2)

                        if ((id_time_days & binary_2_d != 0) and
                                (id_time_weeks & binary_2_w != 0)):

                            if ((w + 1), (d + 1), slot_start) not in \
                                    dict_start_ids_per_week_day_and_slot:
                                dict_start_ids_per_week_day_and_slot[
                                    ((w + 1), (d + 1), slot_start)] = set()
                                dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)] = slot_end
                            elif slot_end < dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)]:
                                dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)] = slot_end
                            dict_start_ids_per_week_day_and_slot[
                                ((w + 1), (d + 1), slot_start)].add(
                                (id_class, id_time, id_room))

                            if ((w + 1), (d + 1), slot_end) not in \
                                    dict_end_ids_per_week_day_and_slot:
                                dict_end_ids_per_week_day_and_slot[
                                    ((w + 1), (d + 1), slot_end)] = set()
                                dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)] = slot_start
                            elif slot_start > dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)]:
                                dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)] = slot_start
                            dict_end_ids_per_week_day_and_slot[
                                ((w + 1), (d + 1), slot_end)].add(
                                (id_class, id_time, id_room))

                            # if ((w + 1), (d + 1), slot_start) not in dict_min_slot_end_per_week_day_and_slot:
                            #     dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)] = slot_end
                            # elif slot_end < dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)]:
                            #     dict_min_slot_end_per_week_day_and_slot[((w + 1), (d + 1), slot_start)] = slot_end

                            # if ((w + 1), (d + 1), slot_end) not in dict_min_slot_start_per_week_day_and_slot:
                            #     dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)] = slot_start
                            # elif slot_start > dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)]:
                            #     dict_min_slot_start_per_week_day_and_slot[((w + 1), (d + 1), slot_end)] = slot_start

        # dict_start_ids_per_week_day_and_slot_aux = {}
        # for tuple_key, value in dict_start_ids_per_week_day_and_slot.items():
        #     dict_start_ids_per_week_day_and_slot_aux[
        #         tuple_key[0], tuple_key[1], tuple_key[2],
        #         dict_min_slot_end_per_week_day_and_slot[tuple_key]] = value
        #
        # dict_end_ids_per_week_day_and_slot_aux = {}
        # for tuple_key, value in dict_end_ids_per_week_day_and_slot.items():
        #     dict_end_ids_per_week_day_and_slot_aux[
        #         tuple_key[0], tuple_key[1], tuple_key[2],
        #         dict_min_slot_start_per_week_day_and_slot[tuple_key]] = value

        return (dict_start_ids_per_week_day_and_slot, dict_end_ids_per_week_day_and_slot,
                dict_min_slot_start_per_week_day_and_slot, dict_min_slot_end_per_week_day_and_slot)

    def generate_ids_per_slot_in_a_room(self, list_of_ids_classes, id_room):
        dict_ids_per_week_day_and_slot = {}
        for id_class in list_of_ids_classes:
            if id_room not in self.classes[id_class].rooms.keys():
                continue
            for id_time, time_tuple in self.classes[id_class].times.items():
                id_time_start = time_tuple.start
                id_time_end = time_tuple.end
                id_time_days = time_tuple.days
                id_time_weeks = time_tuple.weeks

                for w in range(self.nr_weeks):
                    str_2_w = ('{0:0' + str(self.nr_weeks) + 'b}').format(0)
                    str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]
                    binary_2_w = int(str_2_w, 2)

                    for d in range(self.nr_days):
                        str_2_d = ('{0:0' + str(self.nr_days) + 'b}').format(0)
                        str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]
                        binary_2_d = int(str_2_d, 2)

                        if ((id_time_days & binary_2_d != 0) and
                                (id_time_weeks & binary_2_w != 0)):
                            for slot in range(id_time_start, id_time_end):
                                if ((w + 1), (d + 1), slot) not in dict_ids_per_week_day_and_slot:
                                    dict_ids_per_week_day_and_slot[((w + 1), (d + 1), slot)] = set()
                                dict_ids_per_week_day_and_slot[((w + 1), (d + 1), slot)].add(
                                    (id_class, id_time, id_room))

        set_aux = set()
        pos = list(dict_ids_per_week_day_and_slot.keys())[0]
        original_tuple = dict_ids_per_week_day_and_slot[pos]
        for i in list(dict_ids_per_week_day_and_slot.keys())[1:]:
            if dict_ids_per_week_day_and_slot[i] == original_tuple:
                set_aux.add(i)
            else:
                original_tuple = dict_ids_per_week_day_and_slot[pos]
        for j in set_aux:
            del dict_ids_per_week_day_and_slot[j]

        return dict_ids_per_week_day_and_slot

    # def generate_ids_per_slot(self, list_of_ids_classes):
    #     dict_ids_per_slot = {}
    #     for id_class in list_of_ids_classes:
    #         for id_time, time_tuple in self.classes[id_class].times.items():
    #             id_time_start = time_tuple.start
    #             id_time_end = time_tuple.end
    #             for slot in range(id_time_start, id_time_end):
    #                 for id_room in self.classes[id_class].rooms.keys():
    #                     if slot not in dict_ids_per_slot:
    #                         dict_ids_per_slot[slot] = set()
    #                     dict_ids_per_slot[slot].add((id_class, id_time, id_room))
    #
    #     return dict_ids_per_slot

    def generate_constraints_conflict_matrix(self):
        print("COMPUTANDO INTERSECAO ENTRE SALAS...")
        self.compute_intersection_rooms_of_classes(list(self.classes.keys()))
        self.compute_union_rooms_of_classes(list(self.classes.keys()))
        self.compute_union_less_intersection_rooms_of_classes(list(self.classes.keys()))
        print("COMPUTANDO MATRIZES CONFLITOS...")
        print("ANALISANDO CONSTRAINTS:")
        for constraint in self.constraints:
            print("ANALISANDO CONSTRAINT (%d / %d)" % (constraint.id, len(self.constraints)))
            function = None
            matrix = None
            type_constraint = constraint.type
            if Const.SAME_START <= type_constraint <= Const.DIFFERENT_WEEKS:
                if type_constraint == Const.SAME_START:
                    function = self.is_same_start
                    matrix = self.matrix_same_start
                elif type_constraint == Const.SAME_TIME:
                    function = self.is_same_time
                    matrix = self.matrix_same_time
                elif type_constraint == Const.DIFFERENT_TIME:
                    function = self.is_different_time
                    matrix = self.matrix_different_time
                elif type_constraint == Const.SAME_DAYS:
                    function = self.is_same_days
                    matrix = self.matrix_same_days
                elif type_constraint == Const.DIFFERENT_DAYS:
                    function = self.is_different_days
                    matrix = self.matrix_different_days
                elif type_constraint == Const.SAME_WEEKS:
                    function = self.is_same_weeks
                    matrix = self.matrix_same_weeks
                elif type_constraint == Const.DIFFERENT_WEEKS:
                    function = self.is_different_weeks
                    matrix = self.matrix_different_weeks
                self.compute_time_based_constraints(constraint.classes, function, matrix)
            elif type_constraint == Const.OVERLAP:
                # Nao faz nada, pois a matriz de conflitos jah foi computada no inicio.
                pass
            elif type_constraint == Const.NOT_OVERLAP:
                # Nao faz nada, pois a matriz de conflitos jah foi computada no inicio.
                pass
            elif type_constraint == Const.SAME_ROOM:
                # self.compute_intersection_rooms_of_classes(list(self.classes.keys()))
                pass
            elif type_constraint == Const.DIFFERENT_ROOM:
                pass
            elif type_constraint == Const.SAME_ATTENDEES:
                self.compute_same_attendees(constraint.classes)
            elif type_constraint == Const.PRECEDENCE:
                self.compute_precedence(constraint.classes)
            elif type_constraint == Const.WORK_DAY:
                s = constraint.list_of_params[0]
                self.compute_work_day(constraint.classes, s)
            elif type_constraint == Const.MIN_GAP:
                g = constraint.list_of_params[0]
                self.compute_min_gap(constraint.classes, g)

        self.is_same_start = self.__verify_same_start_with_matrix
        self.is_same_time = self.__verify_same_time_with_matrix
        self.is_different_time = self.__verify_different_time_with_matrix
        self.is_same_days = self.__verify_same_days_with_matrix
        self.is_different_days = self.__verify_different_days_with_matrix
        self.is_same_weeks = self.__verify_same_weeks_with_matrix
        self.is_different_weeks = self.__verify_different_weeks_with_matrix
        self.is_precedence = self.__verify_precedence_with_matrix
        self.is_same_attendees = self.__verify_same_attendees_with_matrix
        self.is_work_day = self.__verify_work_day_with_matrix
        self.is_min_gap = self.__verify_min_gap_with_matrix

        print("FIM DA ANALISE DAS CONSTRAINTS")

    def __calculate_possible_id_times_per_room_and_class(
            self, id_class: int, id_room: int) -> List[int]:
        list_of_id_times = []
        obj_room = self.rooms[id_room]
        for id_time in self.classes[id_class].times.keys():
            if id_time is not obj_room.is_time_unavailable(
                    id_time, self.is_overlap):
                list_of_id_times.append(id_time)
        return list_of_id_times

    def calculate_possible_id_times_per_room_and_class(
            self, id_class: int, id_room: int) -> List[int]:
        list_of_id_times = []
        obj_room = self.rooms[id_room]
        for id_time in self.classes[id_class].times.keys():
            if id_time is not obj_room.is_time_unavailable(
                    id_time, self.is_overlap):
                list_of_id_times.append(id_time)
        return list_of_id_times

    def compute_possible_times_per_room(self):
        for id_class in self.classes.keys():
            for id_room in self.classes[id_class].rooms.keys():
                self.matrix_possible_times_per_room_and_class[
                    id_class, id_room] = \
                    self.__calculate_possible_id_times_per_room_and_class(
                        id_class, id_room
                    )
        self.possible_times_per_room_and_class = \
            self.__get_possible_id_times_per_room_and_class

    def __get_possible_id_times_per_room_and_class(
            self, id_class: int, id_room: int) -> List[int]:
        return self.matrix_possible_times_per_room_and_class[id_class, id_room]

    def __calculate_intersection_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        return [id_room for id_room in self.classes[id_class_1].rooms.keys()
                if id_room in self.classes[id_class_2].rooms.keys()]

    def calculate_intersection_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        return [id_room for id_room in self.classes[id_class_1].rooms.keys()
                if id_room in self.classes[id_class_2].rooms.keys()]

    def __get_intersection_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        return self.matrix_intersection_rooms_of_classes[id_class_1, id_class_2]

    def compute_intersection_rooms_of_classes(self, list_of_class_ids: List[int]) -> None:
        for i, id_class_i in enumerate(list_of_class_ids):
            for id_class_j in list_of_class_ids[(i + 1):]:
                if (id_class_i, id_class_j) in self.matrix_intersection_rooms_of_classes:
                    continue
                self.matrix_intersection_rooms_of_classes[id_class_i, id_class_j] = \
                    self.__calculate_intersection_rooms_of_classes(id_class_i, id_class_j)
                self.matrix_intersection_rooms_of_classes[id_class_j, id_class_i] = \
                    self.matrix_intersection_rooms_of_classes[id_class_i, id_class_j]

        self.intersection_rooms_of_classes = self.__get_intersection_rooms_of_classes

    def __calculate_union_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        union_of_rooms = set(self.classes[id_class_1].rooms.keys())
        for id_room_class_2 in self.classes[id_class_2].rooms.keys():
            union_of_rooms.add(id_room_class_2)
        return list(union_of_rooms)

    def calculate_union_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        union_of_rooms = set(self.classes[id_class_1].rooms.keys())
        for id_room_class_2 in self.classes[id_class_2].rooms.keys():
            union_of_rooms.add(id_room_class_2)
        return list(union_of_rooms)

    def __get_union_rooms_of_classes(self, id_class_1, id_class_2) -> List[int]:
        return self.matrix_union_rooms_of_classes[id_class_1, id_class_2]

    def compute_union_rooms_of_classes(self, list_of_class_ids: List[int]) -> None:
        for i, id_class_i in enumerate(list_of_class_ids):
            for id_class_j in list_of_class_ids[(i + 1):]:
                if (id_class_i, id_class_j) in self.matrix_union_rooms_of_classes:
                    continue
                self.matrix_union_rooms_of_classes[id_class_i, id_class_j] = \
                    self.__calculate_union_rooms_of_classes(id_class_i, id_class_j)
                self.matrix_union_rooms_of_classes[id_class_j, id_class_i] = \
                    self.matrix_union_rooms_of_classes[id_class_i, id_class_j]
        self.union_rooms_of_classes = self.__get_union_rooms_of_classes

    def compute_union_less_intersection_rooms_of_classes(self, list_of_class_ids: List[int]) -> None:
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                if (c1, c2) in self.union_less_intersection_rooms_of_classes:
                    continue
                union_less_intersection = []
                for id_room_class in self.union_rooms_of_classes(c1, c2):
                    if id_room_class not in self.intersection_rooms_of_classes(c1, c2):
                        union_less_intersection.append(id_room_class)
                self.union_less_intersection_rooms_of_classes[(c1, c2)] = union_less_intersection
                self.union_less_intersection_rooms_of_classes[(c2, c1)] = \
                    self.union_less_intersection_rooms_of_classes[(c1, c2)]

    def __verify_same_start(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c2_start = time_tuple_class2.start
        return Constraint.same_start(c1_start, c2_start)

    def __verify_same_time(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        return Constraint.same_time(c1_start, c1_end, c2_start, c2_end)

    def __verify_different_time(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        return Constraint.different_time(c1_start, c1_end, c2_start, c2_end)

    def __verify_same_days(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_days = time_tuple_class1.days
        c2_days = time_tuple_class2.days
        return Constraint.same_days(c1_days, c2_days)

    def __verify_different_days(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_days = time_tuple_class1.days
        c2_days = time_tuple_class2.days
        return Constraint.different_days(c1_days, c2_days)

    def __verify_same_weeks(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_weeks = time_tuple_class1.weeks
        c2_weeks = time_tuple_class2.weeks
        return Constraint.same_weeks(c1_weeks, c2_weeks)

    def __verify_different_weeks(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_weeks = time_tuple_class1.weeks
        c2_weeks = time_tuple_class2.weeks
        return Constraint.different_weeks(c1_weeks, c2_weeks)

    def __verify_overlap(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks
        return Constraint.overlap(c1_start, c1_end, c2_start, c2_end, c1_days,
                                  c2_days, c1_weeks, c2_weeks)

    def __verify_not_overlap(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks
        return Constraint.not_overlap(c1_start, c1_end, c2_start, c2_end,
                                      c1_days, c2_days, c1_weeks, c2_weeks)

    def __verify_precedence(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.precedence(c1_end, c2_start, c1_days, c2_days,
                                     c1_weeks, c2_weeks, self.nr_weeks)

    def __verify_same_attendees(self, id_time_class1, id_room_class1,
                                id_time_class2, id_room_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        travel_room = None
        if id_room_class1:
            travel_room = self.times_travel_rooms.get((id_room_class1,
                                                       id_room_class2))
        room_travel_value = travel_room if travel_room else 0

        return Constraint.same_attendees(c1_start, c1_end, c2_start, c2_end,
                                         c1_days, c2_days, c1_weeks, c2_weeks,
                                         room_travel_value)

    def __verify_work_day(self, id_time_class1, id_time_class2, s: int) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.work_day(c1_start, c1_end, c2_start, c2_end, c1_days,
                                   c2_days, c1_weeks, c2_weeks, s)

    def __verify_min_gap(self, id_time_class1, id_time_class2, g: int) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.min_gap(c1_start, c1_end, c2_start, c2_end, c1_days,
                                  c2_days, c1_weeks, c2_weeks, g)

    def generate_all_neighborhood_coefficient(self) -> None:
        list_of_id_classes = list(self.classes.keys())
        list_of_id_classes.sort()
        for id_class_1, id_class_2 in itertools.combinations(list_of_id_classes, 2):
            nb_cf = self.calculate_neighborhood_coefficient(id_class_1, id_class_2)
            if id_class_1 not in self.dict_neighborhood_coefficient_id_to_id:
                self.dict_neighborhood_coefficient_id_to_id[id_class_1] = {}
            if id_class_2 not in self.dict_neighborhood_coefficient_id_to_id:
                self.dict_neighborhood_coefficient_id_to_id[id_class_2] = {}
            self.dict_neighborhood_coefficient_id_to_id[id_class_1][id_class_2] = nb_cf
            self.dict_neighborhood_coefficient_id_to_id[id_class_2][id_class_1] = nb_cf

    def calculate_neighborhood_coefficient(self, id_class_1: int, id_class_2: int) -> int:
        set_aux = {id_class_1, id_class_2}
        list_aux = list(set_aux)
        id_class_1 = list_aux[0]
        id_class_2 = list_aux[1]

        nr_rooms_instersection = \
            len(intersection_list(list(self.classes[id_class_1].rooms.keys()),
                                  list(self.classes[id_class_2].rooms.keys())))

        nr_times_conflicting = 0
        for iter_id_time_class_1 in list(self.classes[id_class_1].times.keys()):
            for iter_id_time_class_2 in list(self.classes[id_class_2].times.keys()):
                if iter_id_time_class_1 == iter_id_time_class_2 or \
                        self.is_overlap(iter_id_time_class_1, iter_id_time_class_2):
                    nr_times_conflicting += 1

        nr_of_common_hard_constraints = 0
        for hard_constraint in self.distributions_hard:
            if id_class_1 in hard_constraint.classes and id_class_2 in hard_constraint.classes:
                nr_of_common_hard_constraints += 1

        nr_of_common_soft_constraints = 0
        for soft_constraint in self.distributions_soft:
            if id_class_1 in soft_constraint.classes and id_class_2 in soft_constraint.classes:
                nr_of_common_soft_constraints += 1

        return 1000 * nr_of_common_soft_constraints + nr_of_common_soft_constraints + \
               nr_rooms_instersection + nr_times_conflicting

    def verify_same_start(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c2_start = time_tuple_class2.start
        return Constraint.same_start(c1_start, c2_start)

    def verify_same_time(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        return Constraint.same_time(c1_start, c1_end, c2_start, c2_end)

    def verify_different_time(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        return Constraint.different_time(c1_start, c1_end, c2_start, c2_end)

    def verify_same_days(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_days = time_tuple_class1.days
        c2_days = time_tuple_class2.days
        return Constraint.same_days(c1_days, c2_days)

    def verify_different_days(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_days = time_tuple_class1.days
        c2_days = time_tuple_class2.days
        return Constraint.different_days(c1_days, c2_days)

    def verify_same_weeks(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_weeks = time_tuple_class1.weeks
        c2_weeks = time_tuple_class2.weeks
        return Constraint.same_weeks(c1_weeks, c2_weeks)

    def verify_different_weeks(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_weeks = time_tuple_class1.weeks
        c2_weeks = time_tuple_class2.weeks
        return Constraint.different_weeks(c1_weeks, c2_weeks)

    def verify_overlap(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks
        return Constraint.overlap(c1_start, c1_end, c2_start, c2_end, c1_days,
                                  c2_days, c1_weeks, c2_weeks)

    def verify_not_overlap(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks
        return Constraint.not_overlap(c1_start, c1_end, c2_start, c2_end,
                                      c1_days, c2_days, c1_weeks, c2_weeks)

    def verify_precedence(self, id_time_class1, id_time_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.precedence(c1_end, c2_start, c1_days, c2_days,
                                     c1_weeks, c2_weeks, self.nr_weeks)

    def verify_same_attendees(self, id_time_class1, id_room_class1,
                                id_time_class2, id_room_class2) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        travel_room = None
        if id_room_class1:
            travel_room = self.times_travel_rooms.get((id_room_class1,
                                                       id_room_class2))
        room_travel_value = travel_room if travel_room else 0

        return Constraint.same_attendees(c1_start, c1_end, c2_start, c2_end,
                                         c1_days, c2_days, c1_weeks, c2_weeks,
                                         room_travel_value)

    def verify_work_day(self, id_time_class1, id_time_class2, s: int) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.work_day(c1_start, c1_end, c2_start, c2_end, c1_days,
                                   c2_days, c1_weeks, c2_weeks, s)

    def verify_min_gap(self, id_time_class1, id_time_class2, g: int) -> bool:
        time_tuple_class1 = self.id_time_to_time_tuple[id_time_class1]
        time_tuple_class2 = self.id_time_to_time_tuple[id_time_class2]
        c1_start = time_tuple_class1.start
        c1_end = time_tuple_class1.end
        c1_days = time_tuple_class1.days
        c1_weeks = time_tuple_class1.weeks

        c2_start = time_tuple_class2.start
        c2_end = time_tuple_class2.end
        c2_days = time_tuple_class2.days
        c2_weeks = time_tuple_class2.weeks

        return Constraint.min_gap(c1_start, c1_end, c2_start, c2_end, c1_days,
                                  c2_days, c1_weeks, c2_weeks, g)

    def __verify_same_start_with_matrix(self, id_time_class1,
                                        id_time_class2) -> bool:
        return not self.matrix_same_start.has_conflict(id_time_class1, id_time_class2)

    def __verify_same_time_with_matrix(self, id_time_class1,
                                       id_time_class2) -> bool:
        return not self.matrix_same_time.has_conflict(id_time_class1, id_time_class2)

    def __verify_different_time_with_matrix(self, id_time_class1,
                                            id_time_class2) -> bool:
        return not self.matrix_different_time.has_conflict(id_time_class1, id_time_class2)

    def __verify_same_days_with_matrix(self, id_time_class1,
                                       id_time_class2) -> bool:
        return not self.matrix_same_days.has_conflict(id_time_class1, id_time_class2)

    def __verify_different_days_with_matrix(self, id_time_class1,
                                            id_time_class2) -> bool:
        return not self.matrix_different_days.has_conflict(id_time_class1, id_time_class2)

    def __verify_same_weeks_with_matrix(self, id_time_class1,
                                        id_time_class2) -> bool:
        return not self.matrix_same_weeks.has_conflict(id_time_class1, id_time_class2)

    def __verify_different_weeks_with_matrix(self, id_time_class1,
                                             id_time_class2) -> bool:
        return not self.matrix_different_weeks.has_conflict(id_time_class1, id_time_class2)

    def __verify_overlap_with_matrix(self, id_time_class1,
                                     id_time_class2) -> bool:
        return not self.matrix_overlap.has_conflict(id_time_class1, id_time_class2)

    def __verify_not_overlap_with_matrix(self, id_time_class1,
                                         id_time_class2) -> bool:
        return not self.matrix_not_overlap.has_conflict(id_time_class1, id_time_class2)

    def __verify_precedence_with_matrix(self, id_time_class1,
                                        id_time_class2) -> bool:
        return not self.matrix_precedence.has_conflict(id_time_class1, id_time_class2)

    def __verify_same_attendees_with_matrix(
            self, id_time_class1, id_room_class1, id_time_class2,
            id_room_class2) -> bool:
        return not self.matrix_same_attendees.has_conflict(
            (id_time_class1, id_room_class1), (id_time_class2, id_room_class2))

    def __verify_work_day_with_matrix(self, id_time_class1, id_time_class2, s: int) -> bool:
        return not self.matrix_work_day.has_conflict((id_time_class1, s), id_time_class2)

    def __verify_min_gap_with_matrix(self, id_time_class1, id_time_class2, g: int) -> bool:
        return not self.matrix_min_gap.has_conflict((id_time_class1, g), id_time_class2)

    def __verify_is_time_unavailable(
            self, id_time: int, id_room: int
    ) -> bool:
        """ Verifica se há conflito de horário entre um horário (id_time) e a
        lista de horários indisponíveis (list_of_unavailables).
        Retorna True caso haja conflito e False, caso contrário.
        """
        return verify_is_time_conflicting_with_list(
            id_time, self.rooms[id_room].unavailables, self.is_overlap)

    def compute_time_based_constraints(self, list_of_class_ids: List[int], function, matrix) -> None:
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                for id_time_class1, time_tuple_class1 in self.classes[c1].times.items():
                    for id_time_class2, time_tuple_class2 in self.classes[c2].times.items():
                        if not function(id_time_class1, id_time_class2):
                            matrix.add_conflict(id_time_class1, id_time_class2)

    def compute_same_attendees(self, list_of_class_ids):
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                for id_room_class1 in self.classes[c1].rooms.keys():
                    for id_room_class2 in self.classes[c2].rooms.keys():
                        for id_time_class1, time_tuple_class1 in self.classes[c1].times.items():
                            for id_time_class2, time_tuple_class2 in self.classes[c2].times.items():
                                if not self.is_same_attendees(id_time_class1, id_room_class1,
                                                              id_time_class2, id_room_class2):
                                    self.matrix_same_attendees.add_conflict(
                                        (id_time_class1, id_room_class1), (id_time_class2, id_room_class2))

    def compute_precedence(self, list_of_class_ids):
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                for id_time_class1, time_tuple_class1 in self.classes[c1].times.items():
                    for id_time_class2, time_tuple_class2 in self.classes[c2].times.items():
                        if not self.is_precedence(id_time_class1, id_time_class2):
                            self.matrix_precedence.add_conflict_one_way(id_time_class1, id_time_class2)

    def compute_work_day(self, list_of_class_ids, s: int):
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                for id_time_class1, time_tuple_class1 in self.classes[c1].times.items():
                    for id_time_class2, time_tuple_class2 in self.classes[c2].times.items():
                        if not self.is_work_day(id_time_class1, id_time_class2, s):
                            self.matrix_work_day.add_conflict((id_time_class1, s), id_time_class2)

    def compute_min_gap(self, list_of_class_ids, g: int):
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                for id_time_class1, time_tuple_class1 in self.classes[c1].times.items():
                    for id_time_class2, time_tuple_class2 in self.classes[c2].times.items():
                        if not self.is_min_gap(id_time_class1, id_time_class2, g):
                            self.matrix_min_gap.add_conflict((id_time_class1, g), id_time_class2)

    def fit(self, minimum: int, percent: float) -> None:
        for obj_class in self.classes.values():
            obj_class.fit(minimum, percent)

    def remove_class(self, id_class: int) -> None:
        for constraint in self.constraints:
            if id_class in constraint.classes:
                constraint.classes.remove(id_class)

    def keep_classes(self, list_of_classes_to_keep: List[int]) -> None:
        list_of_id_classes_to_remove = []

        for id_class in self.classes.keys():
            if id_class not in list_of_classes_to_keep:
                list_of_id_classes_to_remove.append(id_class)

        for id_class in list_of_id_classes_to_remove:
            self.remove_class(id_class)
            del self.classes[id_class]

    def fix_classes(self, rooms_of_classes: Dict[int, int],
                    times_of_classes: Dict[int, int]) -> None:
        for id_class in rooms_of_classes.keys():
            id_room = rooms_of_classes[id_class]
            dict_of_rooms = {id_room: self.classes[id_class].rooms[id_room]}
            self.classes[id_class].rooms = dict_of_rooms
            id_time = times_of_classes[id_class]
            dict_of_times = {id_time: self.classes[id_class].times[id_time]}
            self.classes[id_class].times = dict_of_times

    # def create_cliques(self):
    #     list_of_id_constraints = \
    #         self.list_of_ids_hard_constraints_by_type.get(Const.SAME_ATTENDEES)
    #     if list_of_id_constraints:
    #         for id_constraint in list_of_id_constraints:
    #             list_of_final_cliques = \
    #                 self.compute_cliques_same_attendees(self.constraints[(id_constraint - 1)].classes)

    def compute_cliques_same_attendees(
            self, list_of_id_classes: List[int], param_dominate_clique: int = 3
    ) -> List[List[Tuple[int, int, int]]]:
        graph_conflict_same_attendees = nx.Graph()
        nr_constraints = 0
        print("LISTA DE TURMAS DA RESTRICAO:")
        print(list_of_id_classes)
        for i, id_class_i in enumerate(list_of_id_classes):
            for id_class_j in list_of_id_classes[(i + 1):]:
                for id_time_i in self.classes[id_class_i].times.keys():
                    for id_time_j in self.classes[id_class_j].times.keys():
                        for id_room_i in self.classes[id_class_i].rooms.keys():
                            for id_room_j in self.classes[id_class_j].rooms.keys():
                                if (not self.rooms[id_room_i].is_time_unavailable(
                                        id_time_i, self.is_overlap) and
                                        not self.rooms[id_room_j].is_time_unavailable(
                                            id_time_j, self.is_overlap) and
                                        not self.is_same_attendees(
                                            id_time_i, id_room_i, id_time_j, id_room_j)):
                                    graph_conflict_same_attendees.add_nodes_from(
                                        [(id_class_i, id_time_i, id_room_i),
                                         (id_class_j, id_time_j, id_room_j)])
                                    graph_conflict_same_attendees.add_edge(
                                        (id_class_i, id_time_i, id_room_i),
                                        (id_class_j, id_time_j, id_room_j))
                                    nr_constraints += 1
        sort_criteria = lambda l: len(l)

        list_of_final_cliques = []
        list_of_cliques = list(nx.find_cliques(graph_conflict_same_attendees))
        list_of_cliques.sort(reverse=True, key=sort_criteria)
        max_clique_of_list = list_of_cliques[0]
        size_of_max_clique_of_list = len(max_clique_of_list)
        while size_of_max_clique_of_list >= 2 and \
                number_of_combinations(size_of_max_clique_of_list, 2) >= param_dominate_clique:
            for i, tuple1 in enumerate(max_clique_of_list):
                for tuple2 in max_clique_of_list[(i + 1):]:
                    graph_conflict_same_attendees.remove_edge(tuple1, tuple2)
            list_of_final_cliques.append(max_clique_of_list)
            list_of_cliques = list(nx.find_cliques(graph_conflict_same_attendees))
            list_of_cliques.sort(reverse=True, key=sort_criteria)
            max_clique_of_list = list_of_cliques[0]
            size_of_max_clique_of_list = len(max_clique_of_list)
        for clique in list_of_cliques:
            if len(clique) >= 2:
                list_of_final_cliques.append(clique)
            else:
                break

        print(list_of_final_cliques)
        print("\n\nNum. de Restricoes (com clique): " + str(len(list_of_final_cliques)))
        # input("Pressione ENTER...")
        print("\n\nNum. de Restricoes (sem clique): " + str(nr_constraints))
        # input("Pressione ENTER...")

        return list_of_final_cliques

    def __str__(self):
        str_return = 'Problem:'
        for r in self.rooms.values():
            str_return += '\n' + str(r)
        for c in self.courses.values():
            str_return += '\n' + str(c)
        for d in self.distributions_hard:
            str_return += '\n' + str(d)
        for d in self.distributions_soft:
            str_return += '\n' + str(d)
        for s in self.students.values():
            str_return += '\n' + str(s)
        return str_return
