# -*- coding: utf-8 -*-

import sys
# from functions import *
from funcoes_xml import FileXML
from uctp_model import UCTPModelIntegerProgramming
from uctp_model_by_parts import UCTPModelIntegerProgrammingByParts
# from datetime import datetime
from combinations import *
from output_file import OutputFile
import json
from constants import StrConst
from solution import Solution
from algorithms import Algorithm
from typing import Tuple
import pdb
from multiprocessing import Pool


def generate_list_of_groups_of_id_classes_to_be_processed(problem: Problem):
    list_of_groups_of_hard_constraints = \
        generate_list_of_groups_of_hard_constraints(problem.distributions_hard)

    list_of_classes_not_added = list(problem.classes.keys())
    for id_class in problem.fixed_classes:
        list_of_classes_not_added.remove(id_class)

    # print("INTERSECTION GROUPS OF HARD CONSTRAINTS:")
    # print(list_of_groups_of_hard_constraints)
    # input("PRESS ENTER...")

    list_of_groups_of_id_classes_to_be_processed = []
    random.shuffle(list_of_groups_of_hard_constraints)
    for list_of_hard_id_constraints in list_of_groups_of_hard_constraints:
        list_aux = []
        for hard_id_constraint in list_of_hard_id_constraints:
            hard_constraint = problem.constraints[(hard_id_constraint - 1)]
            for id_class in hard_constraint.classes:
                if id_class not in problem.fixed_classes and id_class not in list_aux:
                    list_aux.append(id_class)
                    if id_class in list_of_classes_not_added:
                        list_of_classes_not_added.remove(id_class)
        if list_aux:
            list_of_groups_of_id_classes_to_be_processed.append(list_aux)
    if list_of_classes_not_added:
        list_of_groups_of_id_classes_to_be_processed.append(list_of_classes_not_added)
    # print("LIST OF GROUPS OF ID CLASSES TO BE PROCESSED:")
    # print(list_of_groups_of_id_classes_to_be_processed)
    # input("PRESS ENTER...")
    return list_of_groups_of_id_classes_to_be_processed


def transfer_solution(
        problem: Problem, rooms_of_classes: Dict[int, int],
        times_of_classes: Dict[int, int]) -> Solution:
    # O método a seguir é executado somente para realizar as matrículas
    # dos estudantes nos seus respectivos cursos.
    solution = Algorithm.build_greedy_initial_solution(problem)
    Algorithm.enroll_students(solution)
    solution.cores = 8
    solution.technique = "Greedy Algorithm"
    solution.author = "Marlucio Pires"
    solution.institution = "UFOP"
    solution.country = "Brasil"
    for id_class in rooms_of_classes.keys():
        solution.classes_solution[id_class].id_time = times_of_classes[id_class]
        solution.classes_solution[id_class].id_room = rooms_of_classes[id_class]
    return solution


def number_of_times_overlaping_between_two_classes(
        problem: Problem, id_class1: int, id_class2: int) -> int:
    obj_class1 = problem.classes[id_class1]
    obj_class2 = problem.classes[id_class2]
    count_aux = 0
    for id_time_class1 in obj_class1.times.keys():
        for id_time_class2 in obj_class2.times.keys():
            if problem.is_overlap(id_time_class1, id_time_class2):
                count_aux += 1
    return count_aux


def is_any_time_overlaping_between_two_classes(
        problem: Problem, id_class1: int, id_class2: int) -> bool:
    obj_class1 = problem.classes[id_class1]
    obj_class2 = problem.classes[id_class2]
    for id_time_class1 in obj_class1.times.keys():
        for id_time_class2 in obj_class2.times.keys():
            if problem.is_overlap(id_time_class1, id_time_class2):
                return True
    return False


def is_any_room_intersecting_between_two_classes(
        problem: Problem, id_class1: int, id_class2: int) -> bool:
    list_rooms_class1 = problem.classes[id_class1].rooms.keys()
    list_rooms_class2 = problem.classes[id_class2].rooms.keys()
    if has_intersection(list_rooms_class1, list_rooms_class2):
        return True
    return False


def generate_dict_of_common_resources(problem):
    dict_of_common_resources = {}
    for i, id_class_i in enumerate(problem.classes.keys()):
        # print("TURMA %d / %d" % ((i + 1), len(problem.classes.keys())))
        for id_class_j in list(problem.classes.keys())[i:]:
            if is_any_room_intersecting_between_two_classes(problem, id_class_i, id_class_j) and \
                    is_any_time_overlaping_between_two_classes(problem, id_class_i, id_class_j):
                if id_class_i not in dict_of_common_resources:
                    dict_of_common_resources[id_class_i] = [id_class_j, ]
                else:
                    dict_of_common_resources[id_class_i].append(id_class_j)
                if id_class_j not in dict_of_common_resources:
                    dict_of_common_resources[id_class_j] = [id_class_i, ]
                else:
                    dict_of_common_resources[id_class_j].append(id_class_i)
    return dict_of_common_resources


def select_id_classes_with_common_resources(problem: Problem, id_class):
    list_of_id_classes_aux = []
    for obj_class in problem.classes.values():
        obj_class_param = problem.classes[id_class]
        if has_intersection(obj_class.rooms.keys(), obj_class_param.rooms.keys()):
            list_of_id_classes_aux.append(obj_class.id)

    list_of_id_times_overlaping_per_id_class = []
    for id_class_i in list_of_id_classes_aux:
        if is_any_time_overlaping_between_two_classes(problem, id_class, id_class_i):
            list_of_id_times_overlaping_per_id_class.append(id_class_i)

    return list_of_id_times_overlaping_per_id_class


"""def select_classes_to_destroy_and_rebuild(problem, list_id_classes_not_allocated):
    if not list_id_classes_not_allocated:
        return []

    dict_list_of_id_constraints_per_class = \
        generate_dict_list_of_id_constraints_per_class(problem.distributions_hard)

    list_of_id_classes_selected = list(list_id_classes_not_allocated)

    for id_class in list_id_classes_not_allocated:
        if dict_list_of_id_constraints_per_class.get(id_class):
            for id_constraint in dict_list_of_id_constraints_per_class.get(id_class):
                list_of_classes = problem.constraints[(id_constraint - 1)].classes
                for id_class_i in list_of_classes:
                    if id_class_i not in list_of_id_classes_selected:
                        list_of_id_classes_selected.append(id_class_i)

    return list_of_id_classes_selected"""


def generate_dict_of_list_id_hard_constraints_per_class(problem: Problem):
    dict_of_list_id_hard_constraints_per_class = {}
    for constraint in problem.distributions_hard:
        for id_class in constraint.classes:
            if id_class not in dict_of_list_id_hard_constraints_per_class:
                dict_of_list_id_hard_constraints_per_class[id_class] = [constraint.id, ]
            else:
                dict_of_list_id_hard_constraints_per_class[id_class].append(constraint.id)
    return dict_of_list_id_hard_constraints_per_class


def generate_dict_of_id_classes_in_common_hard_constraints(problem: Problem):
    dict_of_list_id_hard_constraints_per_class = \
        generate_dict_of_list_id_hard_constraints_per_class(problem)

    dict_of_id_classes_in_common_hard_constraints = {}
    for id_class, list_of_id_hard_constraints in dict_of_list_id_hard_constraints_per_class.items():
        list_aux = []
        for id_hard_constraint in list_of_id_hard_constraints:
            constraint = problem.constraints[(id_hard_constraint - 1)]
            for id_class_i in constraint.classes:
                if id_class_i != id_class and id_class_i not in list_aux:
                    list_aux.append(id_class_i)
        dict_of_id_classes_in_common_hard_constraints[id_class] = list(list_aux)
    return dict_of_id_classes_in_common_hard_constraints


def select_classes_to_destroy_and_rebuild(
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated_param, limit: int):
    if not list_id_classes_not_allocated_param:
        return []

    list_id_classes_not_allocated = deepcopy(list_id_classes_not_allocated_param)
    half = limit // 2
    if len(list_id_classes_not_allocated) > half:
        del list_id_classes_not_allocated[half:]
    random.shuffle(list_id_classes_not_allocated)

    """list_of_id_classes_with_common_resources = []
    for id_class in list_id_classes_not_allocated:
        list_aux = select_id_classes_with_common_resources(problem, id_class)
        for id_class_i in list_aux:
            if id_class_i not in list_id_classes_not_allocated and \
                    id_class_i not in list_of_id_classes_with_common_resources:
                list_of_id_classes_with_common_resources.append(id_class)"""

    list_of_id_classes_to_destroy = []
    for id_class in list_id_classes_not_allocated:
        list_id_classes_in_common_hard_constraints = \
            dict_of_list_id_classes_in_common_hard_constraints.get(id_class)
        if list_id_classes_in_common_hard_constraints:
            for id_class_i in list_id_classes_in_common_hard_constraints:
                if id_class_i not in list_of_id_classes_to_destroy and \
                        id_class_i not in list_id_classes_not_allocated:
                    list_of_id_classes_to_destroy.append(id_class_i)

    number_remanescent = limit - len(list_id_classes_not_allocated)

    if len(list_of_id_classes_to_destroy) > number_remanescent:
        del list_of_id_classes_to_destroy[number_remanescent:]

    count_aux = 0
    max_iterations = number_remanescent * 10
    while len(list_of_id_classes_to_destroy) < number_remanescent and count_aux < max_iterations:
        id_class_not_allocated = list_id_classes_not_allocated[
            random.randrange(0, len(list_id_classes_not_allocated))]
        list_of_id_classes_with_common_resources = \
            dict_of_common_resources.get(id_class_not_allocated)
        if list_of_id_classes_with_common_resources:
            id_class = list_of_id_classes_with_common_resources[
                random.randrange(0, len(list_of_id_classes_with_common_resources))]
            if id_class not in list_of_id_classes_to_destroy and \
                    id_class not in list_id_classes_not_allocated:
                list_of_id_classes_to_destroy.append(id_class)
        count_aux += 1

    return list_of_id_classes_to_destroy


def select_common_id_classes(
        list_of_id_classes_selected,
        dict_of_list_common_id_classes,
        id_class, list_id_classes_allocated, list_of_fixed_classes, limit=0):
    if dict_of_list_common_id_classes.get(id_class):
        list_common_id_classes = \
            list(dict_of_list_common_id_classes.get(id_class))
        if not limit:
            list_of_id_classes_selected.extend(list_common_id_classes)
            return
        random.shuffle(list_common_id_classes)
        count_aux = 0
        for id_class_i in list_common_id_classes:
            if id_class_i not in list_of_id_classes_selected and \
                    id_class_i not in list_of_fixed_classes and \
                    id_class_i in list_id_classes_allocated:
                list_of_id_classes_selected.append(id_class_i)
                count_aux += 1
                if count_aux == limit:
                    break


def select_classes_to_destroy_and_rebuild_v2(
        rooms_of_classes,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, id_class, list_of_fixed_classes, limit: int):
    third = limit // 3

    list_of_id_classes_to_destroy = []

    count_aux = 0
    while len(list_of_id_classes_to_destroy) < limit and count_aux < 10:
        count_aux += 1
        select_common_id_classes(
            list_of_id_classes_to_destroy, dict_of_common_resources,
            id_class, rooms_of_classes.keys(), list_of_fixed_classes, third)

        if list_of_id_classes_to_destroy:
            id_class_neighbor = random.choice(list_of_id_classes_to_destroy)

            select_common_id_classes(
                list_of_id_classes_to_destroy, dict_of_common_resources,
                id_class_neighbor, rooms_of_classes.keys(), list_of_fixed_classes, third)

        select_common_id_classes(
            list_of_id_classes_to_destroy,
            dict_of_list_id_classes_in_common_hard_constraints,
            id_class, rooms_of_classes.keys(), list_of_fixed_classes,
            (limit - len(list_of_id_classes_to_destroy)))

    return list_of_id_classes_to_destroy


def select_classes_to_destroy_and_rebuild_v3(
        rooms_of_classes,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, id_class, list_of_fixed_classes,
        limit_extra_classes_of_hard_constraints: int = 10):
    half = limit_extra_classes_of_hard_constraints // 2

    list_of_id_classes_to_destroy = []

    select_common_id_classes(
        list_of_id_classes_to_destroy,
        dict_of_list_id_classes_in_common_hard_constraints,
        id_class, rooms_of_classes.keys(), list_of_fixed_classes)

    select_common_id_classes(
        list_of_id_classes_to_destroy, dict_of_common_resources,
        id_class, rooms_of_classes.keys(), list_of_fixed_classes, half)

    if list_of_id_classes_to_destroy:
        id_class_neighbor = random.choice(list_of_id_classes_to_destroy)

        select_common_id_classes(
            list_of_id_classes_to_destroy, dict_of_common_resources,
            id_class_neighbor, rooms_of_classes.keys(), list_of_fixed_classes, half)

    return list_of_id_classes_to_destroy


def select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, id_class, list_of_fixed_classes,
        limit_extra_classes_of_hard_constraints: int = 10):
    half = limit_extra_classes_of_hard_constraints // 2

    list_of_id_classes_to_destroy = []

    select_common_id_classes(
        list_of_id_classes_to_destroy,
        dict_of_list_id_classes_in_common_hard_constraints,
        id_class, rooms_of_classes.keys(), list_of_fixed_classes)

    id_class_neighbor = None
    if list_of_id_classes_to_destroy:
        id_class_neighbor = random.choice(list_of_id_classes_to_destroy)

        select_common_id_classes(
            list_of_id_classes_to_destroy,
            dict_of_list_id_classes_in_common_hard_constraints,
            id_class_neighbor, rooms_of_classes.keys(), list_of_fixed_classes)

    select_common_id_classes(
        list_of_id_classes_to_destroy, dict_of_common_resources,
        id_class, rooms_of_classes.keys(), list_of_fixed_classes, half)

    if list_of_id_classes_to_destroy:
        if not id_class_neighbor:
            id_class_neighbor = random.choice(list_of_id_classes_to_destroy)
        select_common_id_classes(
            list_of_id_classes_to_destroy, dict_of_common_resources,
            id_class_neighbor, rooms_of_classes.keys(), list_of_fixed_classes, half)

    return list(set(list_of_id_classes_to_destroy))


def destroy_and_rebuild_class_by_class(
        problem, dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated,
        rooms_of_classes_param, times_of_classes_param, limit):
    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild(
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated, limit)
    # print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_of_classes_to_destroy))

    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v2(
    #     rooms_of_classes_param,
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v3(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)
    print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_of_classes_to_destroy))

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)
    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    # random.shuffle(list_of_classes_to_destroy)
    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)
    random.shuffle(list_of_classes_in_sequence_of_processing)

    list_of_classes_must_be_allocated = []
    list_of_classes_must_be_allocated.extend(list(rooms_of_classes.keys()))

    class_to_be_processed = 0  # Processa-se a partir da segunda turma.
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        problem_aux = deepcopy(problem)
        list_of_classes_to_keep = list(list_of_classes_must_be_allocated)
        list_of_classes_to_keep.append(list_of_classes_in_sequence_of_processing[class_to_be_processed])
        problem_aux.keep_classes(list_of_classes_to_keep)
        problem_aux.fix_classes(rooms_of_classes, times_of_classes)
        mip = UCTPModelIntegerProgrammingByParts(problem_aux)
        mip.list_of_classes_must_be_allocated = list(list_of_classes_must_be_allocated)
        mip.list_of_classes_to_be_allocated_as_possible = \
            [list_of_classes_in_sequence_of_processing[class_to_be_processed], ]
        error, rooms_of_classes_aux, times_of_classes_aux = mip.build_model_and_get_parcial_solution()
        if rooms_of_classes_aux:
            rooms_of_classes = rooms_of_classes_aux
            times_of_classes = times_of_classes_aux
        if (len(list_of_classes_must_be_allocated) + 1) == len(rooms_of_classes):
            list_of_classes_must_be_allocated = list(rooms_of_classes.keys())
        class_to_be_processed += 1

    # print("TOTAL DE TURMAS ALOCADAS SEM CONFLITO NO DESTROY AND REBUILD: " + str(len(rooms_of_classes.keys())))
    return rooms_of_classes, times_of_classes


def validate_solution(problem, rooms_of_classes, times_of_classes):
    list_of_classes_must_be_allocated = []
    list_of_classes_must_be_allocated.extend(list(rooms_of_classes.keys()))

    problem_aux = deepcopy(problem)
    list_of_classes_to_keep = list(list_of_classes_must_be_allocated)
    problem_aux.keep_classes(list_of_classes_to_keep)
    problem_aux.fix_classes(rooms_of_classes, times_of_classes)
    mip = UCTPModelIntegerProgrammingByParts(problem_aux)
    mip.list_of_classes_must_be_allocated = list(list_of_classes_must_be_allocated)
    mip.list_of_classes_to_be_allocated_as_possible = []
    error, rooms_of_classes_aux, times_of_classes_aux = mip.build_model_and_get_parcial_solution()
    if error or len(rooms_of_classes_aux) != len(rooms_of_classes):
        return False
    else:
        return True


def read_solution_from_json_file(solution_json_name_file: str) -> Dict:
    x = {}
    try:
        f = open(solution_json_name_file, 'r')
        x = json.load(f)
        f.close()

        rooms_of_classes = {}
        rooms_of_classes_aux = x.get("rooms_of_classes")
        if rooms_of_classes_aux:
            for k, r in rooms_of_classes_aux.items():
                rooms_of_classes[int(k)] = r

        times_of_classes = {}
        times_of_classes_aux = x.get("times_of_classes")
        if times_of_classes_aux:
            for k, t in times_of_classes_aux.items():
                times_of_classes[int(k)] = t

        x[StrConst.ROOMS_OF_CLASSES.value] = rooms_of_classes
        x[StrConst.TIMES_OF_CLASSES.value] = times_of_classes
    except FileNotFoundError:
        print("Erro na abertura do arquivo com a solucao inicial json (\"%s\")." % solution_json_name_file)
    except json.decoder.JSONDecodeError:
        print("Arquivo nao contem uma solucao json.")
    return x


def validate_solution_json(problem, solution_json_file):
    solution_dict = read_solution_from_json_file(solution_json_file)

    print("VERIFICANDO SE JSON EH SOLUCAO VALIDA...")

    return validate_solution(problem, solution_dict[StrConst.ROOMS_OF_CLASSES.value],
                             solution_dict[StrConst.TIMES_OF_CLASSES.value])


def destroy_and_rebuild_group_of_classes(
        problem, dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated,
        rooms_of_classes_param, times_of_classes_param, limit):
    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v2(
    #     rooms_of_classes_param,
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v3(
    #     rooms_of_classes_param,
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)
    print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_of_classes_to_destroy))

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)
    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    # random.shuffle(list_of_classes_to_destroy)
    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)
    # random.shuffle(list_of_classes_in_sequence_of_processing)

    list_of_classes_must_be_allocated = []
    list_of_classes_must_be_allocated.extend(list(rooms_of_classes.keys()))

    problem_aux = deepcopy(problem)
    list_of_classes_to_keep = list(list_of_classes_must_be_allocated)
    list_of_classes_to_keep.extend(list_of_classes_in_sequence_of_processing)
    problem_aux.keep_classes(list_of_classes_to_keep)
    problem_aux.fix_classes(rooms_of_classes, times_of_classes)
    mip = UCTPModelIntegerProgrammingByParts(problem_aux)
    mip.list_of_classes_must_be_allocated = list(list_of_classes_must_be_allocated)
    mip.list_of_classes_to_be_allocated_as_possible = list_of_classes_in_sequence_of_processing
    mip.list_of_classes_with_initial_values = list_of_classes_to_destroy
    mip.times_of_classes = times_of_classes_param
    mip.rooms_of_classes = rooms_of_classes_param
    error, rooms_of_classes_aux, times_of_classes_aux = mip.build_model_and_get_parcial_solution()
    if error:
        return error, rooms_of_classes, times_of_classes
    elif rooms_of_classes_aux:
        rooms_of_classes = rooms_of_classes_aux
        times_of_classes = times_of_classes_aux

    print("TAMANHO DE ROOMS_OF_CLASSES: " + str(len(rooms_of_classes)))
    # print("TOTAL DE TURMAS ALOCADAS SEM CONFLITO NO DESTROY AND REBUILD: " + str(len(rooms_of_classes.keys())))
    return error, rooms_of_classes, times_of_classes


def select_id_classes_with_hard_constraints_type_same(problem):
    list_of_classes_to_keep = []

    for type_iter, list_of_id_constraints in problem.list_of_ids_hard_constraints_by_type.items():
        if type_iter == Const.SAME_START or type_iter == Const.SAME_TIME or type_iter == Const.SAME_DAYS or \
                type_iter == Const.SAME_WEEKS or type_iter == Const.OVERLAP or type_iter == Const.SAME_ROOM:
            """or \
                type == Const.DIFFERENT_TIME or type == Const.DIFFERENT_DAYS or type == Const.DIFFERENT_WEEKS or \
                type == Const.NOT_OVERLAP or type == Const.PRECEDENCE or type == Const.DIFFERENT_ROOM:"""
            for id_constraint in list_of_id_constraints:
                for id_class in problem.constraints[(id_constraint - 1)].classes:
                    if id_class not in list_of_classes_to_keep and \
                            id_class not in problem.fixed_classes:
                        list_of_classes_to_keep.append(id_class)
    return list_of_classes_to_keep


def generate_list_of_id_classes_in_sequence_of_processing(problem: Problem) -> List[int]:
    """ Gera uma lista com a ordem de processamento dos ids das turmas do problema.
    A lista não inclui as turmas fixas.
    :param problem: Instância do problema.
    :return: lista com os ids das turmas na ordem em que serão processados.
    """
    list_of_groups_of_classes_to_be_processed = \
        generate_list_of_groups_of_id_classes_to_be_processed(problem)
    list_of_classes_in_sequence_of_processing = []
    if list_of_groups_of_classes_to_be_processed:
        for group in list_of_groups_of_classes_to_be_processed:
            list_of_classes_in_sequence_of_processing.extend(group)

    num_classes = sum([len(group) for group in list_of_groups_of_classes_to_be_processed])
    # print("NR. OF NOT FIXED CLASSES: %d" % num_classes)
    # print("NR. OF FIXED CLASSES: %d" % len(problem.fixed_classes))
    # num_classes += len(problem.fixed_classes)
    # print("TOTAL OF CLASSES: %d" % num_classes)
    # input("PRESS ENTER...")
    return list_of_classes_in_sequence_of_processing


def sort_classes_by_number_of_id_times(problem: Problem, list_id_classes):
    dict_aux = {}
    for id_class in list_id_classes:
        obj_class = problem.classes[id_class]
        number_of_times = len(obj_class.times)
        if number_of_times not in dict_aux:
            dict_aux[number_of_times] = [obj_class.id, ]
        else:
            dict_aux[number_of_times].append(obj_class.id)

    list_aux = []
    for i in sorted(dict_aux.keys()):
        list_aux.extend(dict_aux[i])
    return list_aux


def sort_classes_by_number_of_rooms(problem: Problem, list_id_classes):
    dict_aux = {}
    for id_class in list_id_classes:
        obj_class = problem.classes[id_class]
        number_of_rooms = len(obj_class.rooms)
        if number_of_rooms not in dict_aux:
            dict_aux[number_of_rooms] = [obj_class.id, ]
        else:
            dict_aux[number_of_rooms].append(obj_class.id)

    list_aux = []
    for i in sorted(dict_aux.keys()):
        list_aux.extend(dict_aux[i])
    return list_aux


def generate_list_of_id_classes_in_sequence_of_processing_v2(problem: Problem) -> List[int]:
    """ Gera uma lista com a ordem de processamento dos ids das turmas do problema.
    A lista não inclui as turmas fixas.
    :param problem: Instância do problema.
    :return: lista com os ids das turmas na ordem em que serão processados.
    """
    list_of_classes_in_sequence_of_processing = []

    list_of_types_in_sequence_of_processing = \
        [Const.SAME_START, Const.SAME_TIME, Const.SAME_DAYS, Const.SAME_WEEKS,
         Const.OVERLAP, Const.SAME_ROOM, Const.SAME_ATTENDEES, Const.PRECEDENCE,
         Const.WORK_DAY, Const.MIN_GAP, Const.DIFFERENT_ROOM, Const.DIFFERENT_TIME,
         Const.DIFFERENT_DAYS, Const.DIFFERENT_WEEKS, Const.NOT_OVERLAP]
    for type_iter in list_of_types_in_sequence_of_processing:
        list_id_hard_constraints = problem.list_of_ids_hard_constraints_by_type.get(type_iter)
        if list_id_hard_constraints:
            for id_constraint in list_id_hard_constraints:
                constraint = problem.constraints[(id_constraint - 1)]
                if type_iter == Const.SAME_ROOM or type_iter == Const.DIFFERENT_ROOM:
                    sort_function = sort_classes_by_number_of_rooms
                else:
                    sort_function = sort_classes_by_number_of_id_times
                list_aux = sort_function(problem, constraint.classes)
                for id_class in list_aux:
                    if id_class not in list_of_classes_in_sequence_of_processing:
                        list_of_classes_in_sequence_of_processing.append(id_class)

    for id_class in problem.classes.keys():
        if id_class not in problem.fixed_classes and \
                id_class not in list_of_classes_in_sequence_of_processing:
            list_of_classes_in_sequence_of_processing.append(id_class)

    return list_of_classes_in_sequence_of_processing


def simulated_annealing(
        problem: Problem, start_time, rooms_of_classes_param, times_of_classes_param, alpha: float,
        max_iterations: int, initial_temp: float, final_temp: float, output_file=None,
        json_file=None):
    list_id_classes_not_allocated = []
    for id_class in problem.classes.keys():
        if id_class not in rooms_of_classes_param:
            list_id_classes_not_allocated.append(id_class)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                          (len(list_id_classes_not_allocated), len(problem.classes.keys())))
        output_file.write(list_id_classes_not_allocated)
    print("TURMAS NAO ALOCADAS:")
    print(list_id_classes_not_allocated)

    print("GERANDO DICIONARIO DE TURMAS COM RECURSOS EM COMUM...")
    dict_of_common_resources = generate_dict_of_common_resources(problem)
    print("GERANDO DICIONARIO DE TURMAS COM RESTRICOES FORTES EM COMUM...")
    dict_of_id_classes_in_common_hard_constraints = \
        generate_dict_of_id_classes_in_common_hard_constraints(problem)
    limit = 50
    # max_limit = 50
    # min_limit = 10

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    old_value_objective_function = len(list_id_classes_not_allocated)
    best_objective_function = old_value_objective_function

    num_iter = 0
    while initial_temp > final_temp:
        while num_iter < max_iterations:
            num_iter += 1
            id_class_selected = random.choice(list_id_classes_not_allocated)
            print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
            error, rooms_of_classes_aux, times_of_classes_aux = \
                destroy_and_rebuild_group_of_classes(
                    problem, dict_of_id_classes_in_common_hard_constraints,
                    dict_of_common_resources, [id_class_selected, ],
                    rooms_of_classes, times_of_classes, limit)

            # rooms_of_classes_aux, times_of_classes_aux = \
            #     destroy_and_rebuild_class_by_class(
            #         problem, dict_of_id_classes_in_common_hard_constraints,
            #         dict_of_common_resources, [id_class_selected, ],
            #         rooms_of_classes, times_of_classes, limit)

            end_time = (time.time() - start_time)

            if error:
                if output_file:
                    print("GRAVANDO ARQUIVO .OUT")
                    output_file.write("ERRO NA OTIMIZACAO: " + str(error))
                print("ERRO NA OTIMIZACAO: " + str(error))
                # if limit >= (min_limit + 10):
                #     print("TAMANHO DO GRUPO DE TURMAS A SER RECONSTRUIDO DIMINUIDO DE %d PARA %d." %
                #           (limit, (limit - 10)))
                #     limit -= 10

            new_value_objective_function = len(problem.classes) - len(rooms_of_classes_aux)
            delta = new_value_objective_function - old_value_objective_function

            if delta < 0:
                print("MELHOROU!!! (%s)" % str(date_time()))
                old_value_objective_function = new_value_objective_function
                rooms_of_classes = deepcopy(rooms_of_classes_aux)
                times_of_classes = deepcopy(times_of_classes_aux)
                list_id_classes_not_allocated = []
                for id_class in problem.classes.keys():
                    if id_class not in rooms_of_classes:
                        list_id_classes_not_allocated.append(id_class)
                if new_value_objective_function < best_objective_function:
                    if json_file:
                        print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
                        f = open(json_file, 'w')
                        json_obj = {"instance": problem.name,
                                    "datetime": date_time(),
                                    "runtime": end_time,
                                    "rooms_of_classes": rooms_of_classes,
                                    "times_of_classes": times_of_classes,
                                    "list_id_classes_not_allocated": list_id_classes_not_allocated}
                        json.dump(json_obj, f)
                        f.close()
                    best_objective_function = new_value_objective_function
                    if output_file:
                        print("GRAVANDO ARQUIVO .OUT")
                        output_file.write(date_time())
                        output_file.write("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                        output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                                          (len(list_id_classes_not_allocated), len(problem.classes.keys())))
                        output_file.write(list_id_classes_not_allocated)
                    print(date_time())
                    print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                    print("TURMAS NAO ALOCADAS:")
                    print(list_id_classes_not_allocated)

                if new_value_objective_function == 0:
                    return rooms_of_classes_aux, times_of_classes_aux
            # elif random.random() < math.exp(-delta / initial_temp):
            #     print("PIOROU A SOLUCAO! (%s)" % str(datetime()))
            #     old_value_objective_function = new_value_objective_function
            #     rooms_of_classes = deepcopy(rooms_of_classes_aux)
            #     times_of_classes = deepcopy(times_of_classes_aux)
            #     list_id_classes_not_allocated = []
            #     for id_class in problem.classes.keys():
            #         if id_class not in rooms_of_classes:
            #             list_id_classes_not_allocated.append(id_class)
            # elif not error and limit <= (max_limit - 10):
            #     print("TAMANHO DO GRUPO DE TURMAS A SER RECONSTRUIDO AUMENTADO DE %d PARA %d." %
            #           (limit, (limit + 10)))
            #     limit += 10

        initial_temp = initial_temp * alpha
        num_iter = 0
        print(">>>>>>>>>>>>>>>>>>>>>> TEMPERATURA: " + str(initial_temp))

    return rooms_of_classes, times_of_classes


def greedy_algorithm_class_by_class(problem: Problem, start_time, output_file=None, json_file=None):
    list_of_classes_in_sequence_of_processing = \
        generate_list_of_id_classes_in_sequence_of_processing(problem)

    list_of_hard_id_constraints_per_class = \
        generate_dict_list_of_id_constraints_per_class(problem.distributions_hard)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))
    print("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
                          str(list_of_classes_in_sequence_of_processing))
    print("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
          str(list_of_classes_in_sequence_of_processing))

    # list_of_classes_in_sequence_of_processing = \
    #     generate_list_of_id_classes_in_sequence_of_processing_v2(problem)

    list_of_id_times_per_room = {}
    times_of_classes = {}
    rooms_of_classes = {}
    for id_class in problem.fixed_classes:
        id_time = list(problem.classes[id_class].times.keys())[0]
        times_of_classes[id_class] = id_time
        id_room = list(problem.classes[id_class].rooms.keys())[0]
        rooms_of_classes[id_class] = id_room
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    class_to_be_processed = 0
    nr_fixed_classes = len(problem.fixed_classes)
    tam = len(problem.classes)
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        id_class_i = list_of_classes_in_sequence_of_processing[class_to_be_processed]
        print("RESOLVENDO C%d (%d / %d)" % (
            id_class_i, (class_to_be_processed + 1 + nr_fixed_classes), tam))
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
                              list_of_classes_in_sequence_of_processing[class_to_be_processed])
        print("INICIANDO PROCESSAMENTO DA TURMA C%d" % list_of_classes_in_sequence_of_processing[class_to_be_processed])

        list_of_id_rooms_class_i = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_class_i)
        list_of_id_times_class_i = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_class_i)

        combination = CombinationClass(
            id_class_i, list_of_id_rooms_class_i,
            list_of_id_times_class_i)

        if not combination.start_combination(
                problem, list_of_id_times_per_room):
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("SALTA...")
            print("SALTA...")
            class_to_be_processed += 1
            continue

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        allocated = True
        while not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class):
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination.increment_combination(
                    problem, list_of_id_times_per_room):
                del times_of_classes[id_class_i]
                del rooms_of_classes[id_class_i]
                allocated = False
                break
            id_time_i = combination.time
            id_room_i = combination.room
            times_of_classes[id_class_i] = id_time_i
            rooms_of_classes[id_class_i] = id_room_i
            if id_room_i not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i] = []
            list_of_id_times_per_room[id_room_i].append(id_time_i)
        if allocated:
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("PROSSEGUE...")
            print("PROSSEGUE...")
        else:
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("SALTA...")
            print("SALTA...")
        class_to_be_processed += 1

    end_time = (time.time() - start_time)
    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
        output_file.write("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
    print(date_time())
    print("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
    print("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
    # input("PRESS ENTER...")
    # pdb.set_trace()

    if json_file:
        print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
        end_time = (time.time() - start_time)
        list_id_classes_not_allocated = []
        for id_class in problem.classes.keys():
            if id_class not in rooms_of_classes:
                list_id_classes_not_allocated.append(id_class)
        f = open(json_file, 'w')
        json_obj = {"instance": problem.name,
                    "datetime": date_time(),
                    "runtime": end_time,
                    "rooms_of_classes": rooms_of_classes,
                    "times_of_classes": times_of_classes,
                    "list_id_classes_not_allocated": list_id_classes_not_allocated}
        json.dump(json_obj, f)
        f.close()

    result = validate_solution(problem, rooms_of_classes, times_of_classes)
    if result:
        print("A SOLUCAO CONSTRUIDA EH PARCIALMENTE FACTIVEL!")
        # input("PRESS ENTER...")

    # if len(rooms_of_classes) == len(problem.classes):
    #     if output_file:
    #         print("GRAVANDO ARQUIVO .OUT")
    #         output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
    #     print("SUCESSO! SOLUCAO ENCONTRADA!")
    #     # input("PRESS ENTER...")
    #     return transfer_solution(problem, rooms_of_classes, times_of_classes)
    #
    # if output_file:
    #     print("GRAVANDO ARQUIVO .OUT")
    #     output_file.write("INICIANDO SIMULATED ANNEALING...")
    # print("INICIANDO SIMULATED ANNEALING...")
    # rooms_of_classes, times_of_classes = \
    #     simulated_annealing_with_greedy_algorithm(
    #         problem, start_time, rooms_of_classes, times_of_classes,
    #         list_of_classes_in_sequence_of_processing,
    #         list_of_hard_id_constraints_per_class,
    #         0.999, 100, 10000, 0.00001, output_file, json_file)

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)
    else:
        return None


def greedy_algorithm_class_by_class_v2(problem: Problem, start_time, output_file=None, json_file=None):
    list_of_classes_in_sequence_of_processing = \
        generate_list_of_id_classes_in_sequence_of_processing(problem)

    list_of_hard_id_constraints_per_class = \
        generate_dict_list_of_id_constraints_per_class(problem.distributions_hard)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))
    print("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
                          str(list_of_classes_in_sequence_of_processing))
    print("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
          str(list_of_classes_in_sequence_of_processing))

    # list_of_classes_in_sequence_of_processing = \
    #     generate_list_of_id_classes_in_sequence_of_processing_v2(problem)

    list_of_id_times_per_room = {}
    times_of_classes = {}
    rooms_of_classes = {}
    for id_class in problem.fixed_classes:
        id_time = list(problem.classes[id_class].times.keys())[0]
        times_of_classes[id_class] = id_time
        id_room = list(problem.classes[id_class].rooms.keys())[0]
        rooms_of_classes[id_class] = id_room
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    class_to_be_processed = 0
    nr_fixed_classes = len(problem.fixed_classes)
    tam = len(problem.classes)
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        id_class_i = list_of_classes_in_sequence_of_processing[class_to_be_processed]
        print("RESOLVENDO C%d (%d / %d)" % (
            id_class_i, (class_to_be_processed + 1 + nr_fixed_classes), tam))
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
                              list_of_classes_in_sequence_of_processing[class_to_be_processed])
        print("INICIANDO PROCESSAMENTO DA TURMA C%d" % list_of_classes_in_sequence_of_processing[class_to_be_processed])

        list_of_id_rooms_class_i = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_class_i)
        list_of_id_times_class_i = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_class_i)

        combination = CombinationClass(
            id_class_i, list_of_id_rooms_class_i,
            list_of_id_times_class_i)

        if not combination.start_combination(
                problem, list_of_id_times_per_room):
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("SALTA...")
            print("SALTA...")
            class_to_be_processed += 1
            continue

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        allocated = True
        while not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class):
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination.increment_combination(
                    problem, list_of_id_times_per_room):
                del times_of_classes[id_class_i]
                del rooms_of_classes[id_class_i]
                allocated = False
                break
            id_time_i = combination.time
            id_room_i = combination.room
            times_of_classes[id_class_i] = id_time_i
            rooms_of_classes[id_class_i] = id_room_i
            if id_room_i not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i] = []
            list_of_id_times_per_room[id_room_i].append(id_time_i)
        if allocated:
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("PROSSEGUE...")
            print("PROSSEGUE...")
        else:
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("SALTA...")
            print("SALTA...")
        class_to_be_processed += 1

    end_time = (time.time() - start_time)
    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
        output_file.write("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
    print(date_time())
    print("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
    print("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
    # input("PRESS ENTER...")
    # pdb.set_trace()

    if json_file:
        print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
        end_time = (time.time() - start_time)
        list_id_classes_not_allocated = []
        for id_class in problem.classes.keys():
            if id_class not in rooms_of_classes:
                list_id_classes_not_allocated.append(id_class)
        f = open(json_file, 'w')
        json_obj = {"instance": problem.name,
                    "datetime": date_time(),
                    "runtime": end_time,
                    "rooms_of_classes": rooms_of_classes,
                    "times_of_classes": times_of_classes,
                    "list_id_classes_not_allocated": list_id_classes_not_allocated}
        json.dump(json_obj, f)
        f.close()

    # result = validate_solution(problem, rooms_of_classes, times_of_classes)
    # if result:
    #     print("A SOLUCAO CONSTRUIDA EH PARCIALMENTE FACTIVEL!")
        # input("PRESS ENTER...")

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("INICIANDO SIMULATED ANNEALING...")
    print("INICIANDO SIMULATED ANNEALING...")
    rooms_of_classes, times_of_classes = \
        simulated_annealing_with_greedy_algorithm(
            problem, start_time, rooms_of_classes, times_of_classes,
            list_of_classes_in_sequence_of_processing,
            list_of_hard_id_constraints_per_class,
            0.999, 100, 10000, 0.00001, output_file, json_file)

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)
    else:
        return None


def greedy_algorithm_class_by_class_v3(tuple_of_params: Tuple[Problem, float, str, str]):
    problem = tuple_of_params[0]
    start_time = tuple_of_params[1]
    output_file = None
    if tuple_of_params[2]:
        output_file = OutputFile(tuple_of_params[2])
    json_file = None
    if tuple_of_params[3]:
        json_file = tuple_of_params[3]
    list_of_classes_in_sequence_of_processing = \
        generate_list_of_id_classes_in_sequence_of_processing(problem)

    list_of_hard_id_constraints_per_class = \
        generate_dict_list_of_id_constraints_per_class(problem.distributions_hard)

    if output_file:
        output_file.write(date_time())
        output_file.write("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))

    if output_file:
        output_file.write("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
                          str(list_of_classes_in_sequence_of_processing))

    list_of_id_times_per_room = {}
    times_of_classes = {}
    rooms_of_classes = {}
    for id_class in problem.fixed_classes:
        id_time = list(problem.classes[id_class].times.keys())[0]
        times_of_classes[id_class] = id_time
        id_room = list(problem.classes[id_class].rooms.keys())[0]
        rooms_of_classes[id_class] = id_room
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    class_to_be_processed = 0
    nr_fixed_classes = len(problem.fixed_classes)
    tam = len(problem.classes)
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        id_class_i = list_of_classes_in_sequence_of_processing[class_to_be_processed]
        if output_file:
            output_file.write("RESOLVENDO C%d (%d / %d)" % (
                id_class_i, (class_to_be_processed + 1 + nr_fixed_classes), tam))
            output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
                              list_of_classes_in_sequence_of_processing[class_to_be_processed])

        list_of_id_rooms_class_i = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_class_i)
        list_of_id_times_class_i = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_class_i)

        combination = CombinationClass(
            id_class_i, list_of_id_rooms_class_i,
            list_of_id_times_class_i)

        if not combination.start_combination(
                problem, list_of_id_times_per_room):
            if output_file:
                output_file.write("SALTA...")
            class_to_be_processed += 1
            continue

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        allocated = True
        while not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class):
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination.increment_combination(
                    problem, list_of_id_times_per_room):
                del times_of_classes[id_class_i]
                del rooms_of_classes[id_class_i]
                allocated = False
                break
            id_time_i = combination.time
            id_room_i = combination.room
            times_of_classes[id_class_i] = id_time_i
            rooms_of_classes[id_class_i] = id_room_i
            if id_room_i not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i] = []
            list_of_id_times_per_room[id_room_i].append(id_time_i)
        if allocated:
            if output_file:
                output_file.write("PROSSEGUE...")
        else:
            if output_file:
                output_file.write("SALTA...")
        class_to_be_processed += 1

    end_time = (time.time() - start_time)
    if output_file:
        output_file.write(date_time())
        output_file.write("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
        output_file.write("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))

    list_id_classes_not_allocated = []
    for id_class in problem.classes.keys():
        if id_class not in rooms_of_classes:
            list_id_classes_not_allocated.append(id_class)

    json_obj = {"instance": problem.name,
                "datetime": date_time(),
                "runtime": end_time,
                "rooms_of_classes": rooms_of_classes,
                "times_of_classes": times_of_classes,
                "list_id_classes_not_allocated": list_id_classes_not_allocated,
                "json_file": str(tuple_of_params[3]),
                "output_file": str(tuple_of_params[2]),
                "list_of_classes_in_sequence_of_processing": list_of_classes_in_sequence_of_processing,
                "list_of_hard_id_constraints_per_class": list_of_hard_id_constraints_per_class}

    if json_file:
        f = open(json_file, 'w')
        json.dump(json_obj, f)
        f.close()

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")

    # return len(list_id_classes_not_allocated)
    return json_obj


def test_multiprocessing(
        pool, problem: Problem, start_time: float,
        output_file: str, json_file: str, nr_of_solutions: int
) -> Solution:
    best_json_solution = {"list_id_classes_not_allocated": problem.classes}
    for json_solution in pool.imap_unordered(
            greedy_algorithm_class_by_class_v3,
            [(problem, start_time, output_file + "_%d.out" % i, json_file + "_%d.json" % i)
             for i in range(1, (nr_of_solutions + 1))]):
        if len(json_solution["list_id_classes_not_allocated"]) < \
                len(best_json_solution["list_id_classes_not_allocated"]):
            best_json_solution = json_solution

    print("TOTAL DE TURMAS DO PROBLEMA: %d" % len(problem.classes))
    print("MELHOR SOLUCAO: %d TURMAS ALOCADAS" %
          (len(problem.classes) - len(best_json_solution["list_id_classes_not_allocated"])))
    print(best_json_solution)
    # pool = Pool()
    if output_file:
        output_file = best_json_solution["output_file"]
    if json_file:
        json_file = best_json_solution["json_file"]
    return fix_and_optimize_with_greedy_algorithm_and_multiprocessing(
        pool, problem, start_time, best_json_solution["rooms_of_classes"],
        best_json_solution["times_of_classes"],
        best_json_solution["list_of_classes_in_sequence_of_processing"],
        best_json_solution["list_of_hard_id_constraints_per_class"], 20, 50, 100, output_file, json_file)


def destroy_and_rebuild_group_of_classes_with_greedy_algorithm(
        problem, dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated,
        rooms_of_classes_param, times_of_classes_param, limit,
        list_of_classes_in_sequence_of_processing_param,
        list_of_hard_id_constraints_per_class_param
):
    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v2(
    #     rooms_of_classes_param,
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    # list_of_classes_to_destroy = select_classes_to_destroy_and_rebuild_v3(
    #     rooms_of_classes_param,
    #     dict_of_list_id_classes_in_common_hard_constraints,
    #     dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    list_aux = select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)
    print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_aux))

    list_of_classes_to_destroy = intersection(list_of_classes_in_sequence_of_processing_param, list_aux)

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    list_of_id_times_per_room = {}
    for id_class in rooms_of_classes.keys():
        id_room = rooms_of_classes[id_class]
        id_time = times_of_classes[id_class]
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)

    class_to_be_processed = 0
    # nr_fixed_classes = len(rooms_of_classes)
    # tam = len(problem.classes)
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        id_class_i = list_of_classes_in_sequence_of_processing[class_to_be_processed]
        # print("RESOLVENDO C%d (%d / %d)" % (
        #     id_class_i, (class_to_be_processed + 1 + nr_fixed_classes), tam))
        # if output_file:
        #     print("GRAVANDO ARQUIVO .OUT")
        #     output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
        #                       list_of_classes_in_sequence_of_processing[class_to_be_processed])
        # print("INICIANDO PROCESSAMENTO DA TURMA C%d" %
        # list_of_classes_in_sequence_of_processing[class_to_be_processed])

        list_of_id_rooms_class_i = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_class_i)
        list_of_id_times_class_i = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_class_i)

        combination = CombinationClass(
            id_class_i, list_of_id_rooms_class_i,
            list_of_id_times_class_i)

        if not combination.start_combination(
                problem, list_of_id_times_per_room):
            # if output_file:
            #     print("GRAVANDO ARQUIVO .OUT")
            #     output_file.write("SALTA...")
            # print("SALTA...")
            # class_to_be_processed += 1
            # continue
            return rooms_of_classes_param, times_of_classes_param

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        # allocated = True
        while not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class_param):
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination.increment_combination(
                    problem, list_of_id_times_per_room):
                del times_of_classes[id_class_i]
                del rooms_of_classes[id_class_i]
                # allocated = False
                break
            id_time_i = combination.time
            id_room_i = combination.room
            times_of_classes[id_class_i] = id_time_i
            rooms_of_classes[id_class_i] = id_room_i
            if id_room_i not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i] = []
            list_of_id_times_per_room[id_room_i].append(id_time_i)
        # if allocated:
            # if output_file:
            #     print("GRAVANDO ARQUIVO .OUT")
            #     output_file.write("PROSSEGUE...")
            # print("PROSSEGUE...")
        # else:
            # if output_file:
            #     print("GRAVANDO ARQUIVO .OUT")
            #     output_file.write("SALTA...")
            # print("SALTA...")
        class_to_be_processed += 1

    print("TAMANHO DE ROOMS_OF_CLASSES: " + str(len(rooms_of_classes)))
    # print("TOTAL DE TURMAS ALOCADAS SEM CONFLITO NO DESTROY AND REBUILD: " +
    # str(len(rooms_of_classes.keys())))
    return rooms_of_classes, times_of_classes


def destroy_and_rebuild_group_of_classes_with_greedy_algorithm_v2(
        problem, dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated,
        rooms_of_classes_param, times_of_classes_param, limit,
        list_of_classes_in_sequence_of_processing_param,
        list_of_hard_id_constraints_per_class_param
):
    list_aux = select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)
    print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_aux))

    list_of_classes_to_destroy = intersection(list_of_classes_in_sequence_of_processing_param, list_aux)

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    list_of_id_times_per_room = {}
    for id_class in rooms_of_classes.keys():
        id_room = rooms_of_classes[id_class]
        id_time = times_of_classes[id_class]
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)

    class_to_be_processed = 0
    count_aux = 0
    max_iter = 100
    # nr_fixed_classes = len(rooms_of_classes)
    # tam = len(problem.classes)
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing) and count_aux < max_iter:
        id_class_i = list_of_classes_in_sequence_of_processing[class_to_be_processed]
        # print("RESOLVENDO C%d (%d / %d)" % (
        #     id_class_i, (class_to_be_processed + 1 + nr_fixed_classes), tam))
        # if output_file:
        #     print("GRAVANDO ARQUIVO .OUT")
        #     output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
        #                       list_of_classes_in_sequence_of_processing[class_to_be_processed])
        # print("INICIANDO PROCESSAMENTO DA TURMA C%d" %
        # list_of_classes_in_sequence_of_processing[class_to_be_processed])

        list_of_id_rooms_class_i = \
            list(problem.classes[id_class_i].rooms.keys())
        random.shuffle(list_of_id_rooms_class_i)
        list_of_id_times_class_i = \
            list(problem.classes[id_class_i].times.keys())
        random.shuffle(list_of_id_times_class_i)

        combination = CombinationClass(
            id_class_i, list_of_id_rooms_class_i,
            list_of_id_times_class_i)

        allocated = True

        if not combination.start_combination(
                problem, list_of_id_times_per_room):
            # if output_file:
            #     print("GRAVANDO ARQUIVO .OUT")
            #     output_file.write("SALTA...")
            # print("SALTA...")
            # class_to_be_processed += 1
            # continue
            if class_to_be_processed == 0:
                return rooms_of_classes_param, times_of_classes_param
            else:
                allocated = False

        if allocated:
            id_time_i = combination.time
            id_room_i = combination.room
            times_of_classes[id_class_i] = id_time_i
            rooms_of_classes[id_class_i] = id_room_i
            if id_room_i not in list_of_id_times_per_room:
                list_of_id_times_per_room[id_room_i] = []
            list_of_id_times_per_room[id_room_i].append(id_time_i)

            while not Algorithm.verify_respect_of_hard_constraints(
                    problem, id_class_i, rooms_of_classes, times_of_classes,
                    list_of_hard_id_constraints_per_class_param):
                list_of_id_times_per_room[id_room_i].remove(id_time_i)
                if not combination.increment_combination(
                        problem, list_of_id_times_per_room):
                    allocated = False
                    break
                id_time_i = combination.time
                id_room_i = combination.room
                times_of_classes[id_class_i] = id_time_i
                rooms_of_classes[id_class_i] = id_room_i
                if id_room_i not in list_of_id_times_per_room:
                    list_of_id_times_per_room[id_room_i] = []
                list_of_id_times_per_room[id_room_i].append(id_time_i)
            # if allocated:
                # if output_file:
                #     print("GRAVANDO ARQUIVO .OUT")
                #     output_file.write("PROSSEGUE...")
                # print("PROSSEGUE...")
            # else:
                # if output_file:
                #     print("GRAVANDO ARQUIVO .OUT")
                #     output_file.write("SALTA...")
                # print("SALTA...")
        if not allocated:
            aux = list_of_classes_in_sequence_of_processing[class_to_be_processed]
            list_of_classes_in_sequence_of_processing[class_to_be_processed] = \
                list_of_classes_in_sequence_of_processing[(class_to_be_processed - 1)]
            list_of_classes_in_sequence_of_processing[(class_to_be_processed - 1)] = aux

            rooms_of_classes = deepcopy(rooms_of_classes_param)
            times_of_classes = deepcopy(times_of_classes_param)

            for id_class in list_of_classes_to_destroy:
                if id_class in rooms_of_classes:
                    del rooms_of_classes[id_class]
                    del times_of_classes[id_class]

            list_of_id_times_per_room = {}
            for id_class in rooms_of_classes.keys():
                id_room = rooms_of_classes[id_class]
                id_time = times_of_classes[id_class]
                if id_room not in list_of_id_times_per_room:
                    list_of_id_times_per_room[id_room] = []
                list_of_id_times_per_room[id_room].append(id_time)
            class_to_be_processed = 0
            count_aux += 1
        else:
            class_to_be_processed += 1

    print("TAMANHO DE ROOMS_OF_CLASSES: " + str(len(rooms_of_classes)))
    # print("TOTAL DE TURMAS ALOCADAS SEM CONFLITO NO DESTROY AND REBUILD: " +
    # str(len(rooms_of_classes.keys())))
    return rooms_of_classes, times_of_classes


def destroy_and_rebuild_group_of_classes_with_greedy_algorithm_v3(
        problem, dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated,
        rooms_of_classes_param, times_of_classes_param, limit,
        list_of_classes_in_sequence_of_processing_param,
        list_of_hard_id_constraints_per_class_param,
        time_limit
):
    # solution = Solution(problem)
    # solution.cores = 8
    # solution.technique = "Greedy Algorithm"
    # solution.author = "Marlucio Pires"
    # solution.institution = "UFOP"
    # solution.country = "Brasil"
    #
    # solution.allocate_fixed_classes()

    list_aux = select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)
    print("LISTA DE TURMAS A SER RECONSTRUIDA: " + str(list_aux))

    list_of_classes_to_destroy = intersection(list_of_classes_in_sequence_of_processing_param, list_aux)

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    list_of_id_times_per_room = {}
    for id_class in rooms_of_classes.keys():
        id_room = rooms_of_classes[id_class]
        id_time = times_of_classes[id_class]
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)

    # if len(list_of_id_classes_in_sequence_of_processing) != \
    #        len(problem.classes) - len(problem.fixed_classes):
    #    print("len(list_of_id_classes_in_sequence_of_processing) = %d" %
    #          len(list_of_id_classes_in_sequence_of_processing))
    #    print("len(problem.classes) = %d" % len(problem.classes))
    #    print("ERRO!")
    #    return solution

    i = 0
    id_class_i = list_of_classes_in_sequence_of_processing[i]

    list_of_id_rooms_per_class = {}
    list_of_id_times_per_class = {}

    list_of_id_rooms_per_class[id_class_i] = \
        list(problem.classes[id_class_i].rooms.keys())
    random.shuffle(list_of_id_rooms_per_class[id_class_i])
    list_of_id_times_per_class[id_class_i] = \
        list(problem.classes[id_class_i].times.keys())
    random.shuffle(list_of_id_times_per_class[id_class_i])

    combination_per_class = [CombinationClass(
        id_class_i, list_of_id_rooms_per_class[id_class_i],
        list_of_id_times_per_class[id_class_i])]

    if not combination_per_class[-1].start_combination(
            problem, list_of_id_times_per_room):
        return rooms_of_classes_param, times_of_classes_param

    must_increment_combination = False
    # count_solutions = count_of_files
    # nr_fixed_classes = problem.number_of_fixed_classes
    # tam = len(list_of_id_classes_in_sequence_of_processing) + \
    #       nr_fixed_classes

    initial_time = time.time()
    while i >= 0:
        if (time.time() - initial_time) >= time_limit:
            break
            # return rooms_of_classes, times_of_classes
        id_class_i = list_of_classes_in_sequence_of_processing[i]
        # print("RESOLVENDO C%d (%d / %d)" % (
        #     id_class_i, (i + 1), tam))
        combination = combination_per_class[-1]
        if must_increment_combination:
            id_time_i = combination.time
            id_room_i = combination.room
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination_per_class[-1].increment_combination(
                    problem, list_of_id_times_per_room):
                if (time.time() - initial_time) >= time_limit:
                    return rooms_of_classes, times_of_classes
                del combination_per_class[-1]
                if times_of_classes.get(id_class_i):
                    del times_of_classes[id_class_i]
                    del rooms_of_classes[id_class_i]
                i -= 1
                must_increment_combination = True
                continue
            else:
                must_increment_combination = False

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        if not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class_param):
            if (time.time() - initial_time) >= time_limit:
                break
                # return rooms_of_classes, times_of_classes
            must_increment_combination = True
            continue

        i += 1
        if i < len(list_of_classes_in_sequence_of_processing):
            id_class_i = list_of_classes_in_sequence_of_processing[i]
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
                    break
                    # return rooms_of_classes, times_of_classes
                del combination_per_class[-1]
                i -= 1
                must_increment_combination = True
        else:
            # count_solutions += 1
            # print("ACHOU SOLUCAO VIAVEL! COUNT: %d" % count_solutions)
            # for id_class_k in list(classes_times.keys())[(len(
            #         problem.fixed_classes)):]:
            #     id_room = classes_rooms[id_class_k]
            #     id_time = classes_times[id_class_k]
            #     solution.classes_solution[id_class_k] = ClassSolution(
            #         id_class_k, id_time, id_room)
            # end_time = (time.time() - start_time)
            # solution.runtime = "%s" % round(end_time, 1)
            # Algorithm.enroll_students(solution)
            # file_name = "output\\" + "{0:02d}".format(count_solutions) + "_saida_" + \
            #             solution.problem.name + ".xml"
            # FileXML.write_file_xml(file_name, solution)
            break

    print("TAMANHO DE ROOMS_OF_CLASSES: " + str(len(rooms_of_classes)))
    return rooms_of_classes, times_of_classes


def simulated_annealing_with_greedy_algorithm(
        problem: Problem, start_time, rooms_of_classes_param, times_of_classes_param,
        list_of_classes_in_sequence_of_processing_param,
        list_of_hard_id_constraints_per_class_param, alpha: float,
        max_iterations: int, initial_temp: float, final_temp: float, output_file=None,
        json_file=None):
    list_id_classes_not_allocated = []
    for id_class in problem.classes.keys():
        if id_class not in rooms_of_classes_param:
            list_id_classes_not_allocated.append(id_class)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                          (len(list_id_classes_not_allocated), len(problem.classes.keys())))
        output_file.write(list_id_classes_not_allocated)
    print("TURMAS NAO ALOCADAS:")
    print(list_id_classes_not_allocated)

    dict_of_common_resources = generate_dict_of_common_resources(problem)
    dict_of_id_classes_in_common_hard_constraints = \
        generate_dict_of_id_classes_in_common_hard_constraints(problem)
    limit = 50

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    old_value_objective_function = len(list_id_classes_not_allocated)
    best_objective_function = old_value_objective_function

    num_iter = 0
    while initial_temp > final_temp:
        while num_iter < max_iterations:
            num_iter += 1
            id_class_selected = random.choice(list_id_classes_not_allocated)
            print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)

            time_limit = 10  # tempo em segundos
            rooms_of_classes_aux, times_of_classes_aux = \
                destroy_and_rebuild_group_of_classes_with_greedy_algorithm_v3(
                    problem, dict_of_id_classes_in_common_hard_constraints,
                    dict_of_common_resources, [id_class_selected, ],
                    rooms_of_classes, times_of_classes, limit,
                    list_of_classes_in_sequence_of_processing_param,
                    list_of_hard_id_constraints_per_class_param, time_limit)

            # rooms_of_classes_aux, times_of_classes_aux = \
            #     destroy_and_rebuild_group_of_classes_with_greedy_algorithm_v2(
            #         problem, dict_of_id_classes_in_common_hard_constraints,
            #         dict_of_common_resources, [id_class_selected, ],
            #         rooms_of_classes, times_of_classes, limit,
            #         list_of_classes_in_sequence_of_processing_param,
            #         list_of_hard_id_constraints_per_class_param)

            # rooms_of_classes_aux, times_of_classes_aux = \
            #     destroy_and_rebuild_class_by_class(
            #         problem, dict_of_id_classes_in_common_hard_constraints,
            #         dict_of_common_resources, [id_class_selected, ],
            #         rooms_of_classes, times_of_classes, limit)

            end_time = (time.time() - start_time)

            # if error:
            #     if output_file:
            #         print("GRAVANDO ARQUIVO .OUT")
            #         output_file.write("ERRO NA OTIMIZACAO: " + str(error))
            #     print("ERRO NA OTIMIZACAO: " + str(error))
            #     if limit >= (min_limit + 10):
            #         print("TAMANHO DO GRUPO DE TURMAS A SER RECONSTRUIDO DIMINUIDO DE %d PARA %d." %
            #               (limit, (limit - 10)))
            #         limit -= 10

            new_value_objective_function = len(problem.classes) - len(rooms_of_classes_aux)
            delta = new_value_objective_function - old_value_objective_function

            if delta < 0:
                print("MELHOROU!!! (%s)" % str(date_time()))
                old_value_objective_function = new_value_objective_function
                rooms_of_classes = deepcopy(rooms_of_classes_aux)
                times_of_classes = deepcopy(times_of_classes_aux)
                list_id_classes_not_allocated = []
                for id_class in problem.classes.keys():
                    if id_class not in rooms_of_classes:
                        list_id_classes_not_allocated.append(id_class)
                if new_value_objective_function < best_objective_function:
                    if json_file:
                        print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
                        f = open(json_file, 'w')
                        json_obj = {"instance": problem.name,
                                    "datetime": date_time(),
                                    "runtime": end_time,
                                    "rooms_of_classes": rooms_of_classes,
                                    "times_of_classes": times_of_classes,
                                    "list_id_classes_not_allocated": list_id_classes_not_allocated}
                        json.dump(json_obj, f)
                        f.close()
                    best_objective_function = new_value_objective_function
                    if output_file:
                        print("GRAVANDO ARQUIVO .OUT")
                        output_file.write(date_time())
                        output_file.write("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                        output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                                          (len(list_id_classes_not_allocated), len(problem.classes.keys())))
                        output_file.write(list_id_classes_not_allocated)
                    print(date_time())
                    print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                    print("TURMAS NAO ALOCADAS:")
                    print(list_id_classes_not_allocated)

                if new_value_objective_function == 0:
                    return rooms_of_classes_aux, times_of_classes_aux
            # elif random.random() < math.exp(-delta / initial_temp):
            #     print("PIOROU A SOLUCAO! (%s)" % str(datetime()))
            #     old_value_objective_function = new_value_objective_function
            #     rooms_of_classes = deepcopy(rooms_of_classes_aux)
            #     times_of_classes = deepcopy(times_of_classes_aux)
            #     list_id_classes_not_allocated = []
            #     for id_class in problem.classes.keys():
            #         if id_class not in rooms_of_classes:
            #             list_id_classes_not_allocated.append(id_class)
            # elif not error and limit <= (max_limit - 10):
            #     print("TAMANHO DO GRUPO DE TURMAS A SER RECONSTRUIDO AUMENTADO DE %d PARA %d." %
            #           (limit, (limit + 10)))
            #     limit += 10

        initial_temp = initial_temp * alpha
        num_iter = 0
        print(">>>>>>>>>>>>>>>>>>>>>> TEMPERATURA: " + str(initial_temp))

    return rooms_of_classes, times_of_classes


def destroy_and_rebuild_group_of_classes_with_greedy_algorithm_and_multiprocessing(
        tuple_of_params: Tuple,
):
    problem = tuple_of_params[0]
    dict_of_list_id_classes_in_common_hard_constraints = tuple_of_params[1]
    dict_of_common_resources = tuple_of_params[2]
    list_id_classes_not_allocated = tuple_of_params[3]
    rooms_of_classes_param = tuple_of_params[4]
    times_of_classes_param = tuple_of_params[5]
    limit = tuple_of_params[6]
    list_of_classes_in_sequence_of_processing_param = tuple_of_params[7]
    list_of_hard_id_constraints_per_class_param = tuple_of_params[8]
    time_limit = tuple_of_params[9]

    list_aux = select_classes_to_destroy_and_rebuild_v4(
        rooms_of_classes_param,
        dict_of_list_id_classes_in_common_hard_constraints,
        dict_of_common_resources, list_id_classes_not_allocated[0], problem.fixed_classes, limit)

    list_of_classes_to_destroy = intersection(list_of_classes_in_sequence_of_processing_param, list_aux)

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    for id_class in list_of_classes_to_destroy:
        if id_class in rooms_of_classes:
            del rooms_of_classes[id_class]
            del times_of_classes[id_class]

    list_of_id_times_per_room = {}
    for id_class in rooms_of_classes.keys():
        id_room = rooms_of_classes[id_class]
        id_time = times_of_classes[id_class]
        if id_room not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room] = []
        list_of_id_times_per_room[id_room].append(id_time)

    list_of_classes_in_sequence_of_processing = list(list_id_classes_not_allocated)
    list_of_classes_in_sequence_of_processing.extend(list_of_classes_to_destroy)

    i = 0
    id_class_i = list_of_classes_in_sequence_of_processing[i]

    list_of_id_rooms_per_class = {}
    list_of_id_times_per_class = {}

    list_of_id_rooms_per_class[id_class_i] = \
        list(problem.classes[id_class_i].rooms.keys())
    random.shuffle(list_of_id_rooms_per_class[id_class_i])
    list_of_id_times_per_class[id_class_i] = \
        list(problem.classes[id_class_i].times.keys())
    random.shuffle(list_of_id_times_per_class[id_class_i])

    combination_per_class = [CombinationClass(
        id_class_i, list_of_id_rooms_per_class[id_class_i],
        list_of_id_times_per_class[id_class_i])]

    if not combination_per_class[-1].start_combination(
            problem, list_of_id_times_per_room):
        return rooms_of_classes_param, times_of_classes_param

    must_increment_combination = False

    initial_time = time.time()
    while i >= 0:
        if (time.time() - initial_time) >= time_limit:
            break
        id_class_i = list_of_classes_in_sequence_of_processing[i]
        combination = combination_per_class[-1]
        if must_increment_combination:
            id_time_i = combination.time
            id_room_i = combination.room
            list_of_id_times_per_room[id_room_i].remove(id_time_i)
            if not combination_per_class[-1].increment_combination(
                    problem, list_of_id_times_per_room):
                if (time.time() - initial_time) >= time_limit:
                    return rooms_of_classes, times_of_classes
                del combination_per_class[-1]
                if times_of_classes.get(id_class_i):
                    del times_of_classes[id_class_i]
                    del rooms_of_classes[id_class_i]
                i -= 1
                must_increment_combination = True
                continue
            else:
                must_increment_combination = False

        id_time_i = combination.time
        id_room_i = combination.room
        times_of_classes[id_class_i] = id_time_i
        rooms_of_classes[id_class_i] = id_room_i
        if id_room_i not in list_of_id_times_per_room:
            list_of_id_times_per_room[id_room_i] = []
        list_of_id_times_per_room[id_room_i].append(id_time_i)

        if not Algorithm.verify_respect_of_hard_constraints(
                problem, id_class_i, rooms_of_classes, times_of_classes,
                list_of_hard_id_constraints_per_class_param):
            if (time.time() - initial_time) >= time_limit:
                break
            must_increment_combination = True
            continue

        i += 1
        if i < len(list_of_classes_in_sequence_of_processing):
            id_class_i = list_of_classes_in_sequence_of_processing[i]
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
                    break
                del combination_per_class[-1]
                i -= 1
                must_increment_combination = True
        else:
            break

    return rooms_of_classes, times_of_classes


def fix_and_optimize_with_greedy_algorithm_and_multiprocessing(
        pool, problem: Problem, start_time, rooms_of_classes_param, times_of_classes_param,
        list_of_classes_in_sequence_of_processing_param,
        list_of_hard_id_constraints_per_class_param, nr_of_threads, min_limit, max_limit,
        output_file=None, json_file=None) -> Solution:
    if output_file:
        output_file = OutputFile(output_file)
    list_id_classes_not_allocated = []
    for id_class in problem.classes.keys():
        if id_class not in rooms_of_classes_param:
            list_id_classes_not_allocated.append(id_class)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("==============================================================")
        output_file.write("INICIANDO FIX AND OPTIMIZE")
        output_file.write("==============================================================")
        output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                          (len(list_id_classes_not_allocated), len(problem.classes.keys())))
        output_file.write(list_id_classes_not_allocated)
    print("TURMAS NAO ALOCADAS:")
    print(list_id_classes_not_allocated)

    dict_of_common_resources = generate_dict_of_common_resources(problem)
    dict_of_id_classes_in_common_hard_constraints = \
        generate_dict_of_id_classes_in_common_hard_constraints(problem)
    limit = min_limit

    rooms_of_classes = deepcopy(rooms_of_classes_param)
    times_of_classes = deepcopy(times_of_classes_param)

    old_value_objective_function = len(list_id_classes_not_allocated)
    best_objective_function = old_value_objective_function

    while True:
        id_class_selected = random.choice(list_id_classes_not_allocated)
        print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)

        time_limit = 10  # tempo em segundos

        rooms_of_classes_aux = deepcopy(rooms_of_classes)
        times_of_classes_aux = deepcopy(times_of_classes)
        # pool = Pool()
        for rooms_of_classes_iter, times_of_classes_iter in pool.imap_unordered(
                destroy_and_rebuild_group_of_classes_with_greedy_algorithm_and_multiprocessing,
                [(problem, dict_of_id_classes_in_common_hard_constraints,
                  dict_of_common_resources, [id_class_selected, ],
                  rooms_of_classes, times_of_classes, limit,
                  list_of_classes_in_sequence_of_processing_param,
                  list_of_hard_id_constraints_per_class_param, time_limit) for i in range(nr_of_threads)]):
            if len(rooms_of_classes_iter) > len(rooms_of_classes_aux):
                rooms_of_classes_aux = deepcopy(rooms_of_classes_iter)
                times_of_classes_aux = deepcopy(times_of_classes_iter)

        end_time = (time.time() - start_time)

        new_value_objective_function = len(problem.classes) - len(rooms_of_classes_aux)
        delta = new_value_objective_function - old_value_objective_function

        if delta < 0:
            limit = min_limit
            print("MELHOROU!!! (%s)" % str(date_time()))
            old_value_objective_function = new_value_objective_function
            rooms_of_classes = deepcopy(rooms_of_classes_aux)
            times_of_classes = deepcopy(times_of_classes_aux)
            list_id_classes_not_allocated = []
            for id_class in problem.classes.keys():
                if id_class not in rooms_of_classes:
                    list_id_classes_not_allocated.append(id_class)
            if new_value_objective_function < best_objective_function:
                if json_file:
                    print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
                    f = open(json_file, 'w')
                    json_obj = {"instance": problem.name,
                                "datetime": date_time(),
                                "runtime": end_time,
                                "rooms_of_classes": rooms_of_classes,
                                "times_of_classes": times_of_classes,
                                "list_id_classes_not_allocated": list_id_classes_not_allocated,
                                "json_file": str(json_file),
                                "output_file": str(output_file)}
                    json.dump(json_obj, f)
                    f.close()
                best_objective_function = new_value_objective_function
                if output_file:
                    print("GRAVANDO ARQUIVO .OUT")
                    output_file.write(date_time())
                    output_file.write("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                    output_file.write("TURMAS NAO ALOCADAS: %d / %d" %
                                      (len(list_id_classes_not_allocated), len(problem.classes.keys())))
                    output_file.write(list_id_classes_not_allocated)
                print(date_time())
                print("TURMA SELECIONADA PARA REBUILD: C%d" % id_class_selected)
                print("TURMAS NAO ALOCADAS:")
                print(list_id_classes_not_allocated)

            if new_value_objective_function == 0:
                # return rooms_of_classes_aux, times_of_classes_aux
                return transfer_solution(problem, rooms_of_classes_aux, times_of_classes_aux)
        else:
            limit += 10
            if limit > max_limit:
                limit = max_limit

    # return rooms_of_classes, times_of_classes


def optimization_class_by_class(problem: Problem, start_time, output_file=None, json_file=None):
    list_of_classes_in_sequence_of_processing = \
        generate_list_of_id_classes_in_sequence_of_processing(problem)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))
    print("LISTA DE TURMAS FIXAS: " + str(problem.fixed_classes))

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
                          str(list_of_classes_in_sequence_of_processing))
    print("\nLISTA DAS DEMAIS TURMAS NA SEQUENCIA DE PROCESSAMENTO: " +
          str(list_of_classes_in_sequence_of_processing))

    # list_of_classes_in_sequence_of_processing = \
    #     generate_list_of_id_classes_in_sequence_of_processing_v2(problem)

    list_of_classes_must_be_allocated = []
    list_of_classes_must_be_allocated.extend(problem.fixed_classes)

    list_of_classes_must_be_allocated.append(list_of_classes_in_sequence_of_processing[0])
    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" % list_of_classes_in_sequence_of_processing[0])
    print("INICIANDO PROCESSAMENTO DA TURMA C%d" % list_of_classes_in_sequence_of_processing[0])

    # print("INICIO DA ALOCACAO INICIAL OBRIGATORIA")
    problem_aux = deepcopy(problem)
    problem_aux.keep_classes(list_of_classes_must_be_allocated)
    mip = UCTPModelIntegerProgrammingByParts(problem_aux)
    mip.list_of_classes_must_be_allocated = list(list_of_classes_must_be_allocated)
    error, rooms_of_classes, times_of_classes = mip.build_model_and_get_parcial_solution()
    # print("FIM DA ALOCACAO INICIAL OBRIGATORIA")
    # input("PRESS ENTER...")
    if len(rooms_of_classes) == len(problem.classes):
        return transfer_solution(problem, rooms_of_classes, times_of_classes)
    elif len(list_of_classes_must_be_allocated) == len(problem.classes):
        # Foi realizada tentativa de alocação de todas as turmas e
        # não se obteve sucesso.
        return None

    class_to_be_processed = 1  # Processa-se a partir da segunda turma.
    while class_to_be_processed < len(list_of_classes_in_sequence_of_processing):
        problem_aux = deepcopy(problem)
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("INICIANDO PROCESSAMENTO DA TURMA C%d" %
                              list_of_classes_in_sequence_of_processing[class_to_be_processed])
        print("INICIANDO PROCESSAMENTO DA TURMA C%d" % list_of_classes_in_sequence_of_processing[class_to_be_processed])
        list_of_classes_to_keep = list(list_of_classes_must_be_allocated)
        list_of_classes_to_keep.append(list_of_classes_in_sequence_of_processing[class_to_be_processed])
        problem_aux.keep_classes(list_of_classes_to_keep)
        problem_aux.fix_classes(rooms_of_classes, times_of_classes)
        mip = UCTPModelIntegerProgrammingByParts(problem_aux)
        mip.list_of_classes_must_be_allocated = list(list_of_classes_must_be_allocated)
        mip.list_of_classes_to_be_allocated_as_possible = \
            [list_of_classes_in_sequence_of_processing[class_to_be_processed], ]
        error, rooms_of_classes_aux, times_of_classes_aux = mip.build_model_and_get_parcial_solution()
        if rooms_of_classes_aux:
            rooms_of_classes = rooms_of_classes_aux
            times_of_classes = times_of_classes_aux
        if len(rooms_of_classes) == len(problem.classes):
            if output_file:
                print("GRAVANDO ARQUIVO .OUT")
                output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
            print("SUCESSO! SOLUCAO ENCONTRADA!")
            return transfer_solution(problem, rooms_of_classes, times_of_classes)
        else:
            if (len(list_of_classes_must_be_allocated) + 1) == len(rooms_of_classes):
                if output_file:
                    print("GRAVANDO ARQUIVO .OUT")
                    output_file.write("PROSSEGUE...")
                print("PROSSEGUE...")
                list_of_classes_must_be_allocated = list(rooms_of_classes.keys())
            else:
                if output_file:
                    print("GRAVANDO ARQUIVO .OUT")
                    output_file.write("SALTA...")
                print("SALTA...")
            class_to_be_processed += 1

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
    print(date_time())
    print("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))

    if json_file:
        print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
        end_time = (time.time() - start_time)
        list_id_classes_not_allocated = []
        for id_class in problem.classes.keys():
            if id_class not in rooms_of_classes:
                list_id_classes_not_allocated.append(id_class)
        f = open(json_file, 'w')
        json_obj = {"instance": problem.name,
                    "datetime": date_time(),
                    "runtime": end_time,
                    "rooms_of_classes": rooms_of_classes,
                    "times_of_classes": times_of_classes,
                    "list_id_classes_not_allocated": list_id_classes_not_allocated}
        json.dump(json_obj, f)
        f.close()

    # return None
    # input("PRESS ENTER...")
    # print(dict_of_id_classes_in_common_hard_constraints)
    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("INICIANDO SIMULATED ANNEALING...")
    print("INICIANDO SIMULATED ANNEALING...")
    rooms_of_classes, times_of_classes = \
        simulated_annealing(problem, start_time, rooms_of_classes, times_of_classes,
                            0.999, 100, 10000, 0.00001, output_file, json_file)

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)
    else:
        return None


def optimization_class_by_class_with_initial_solution(
        problem: Problem, output_file=None, json_file=None,
        initial_solution_file=None):
    if not initial_solution_file:
        return None
    else:
        f = open(initial_solution_file, 'r')
        x = json.load(f)
        f.close()

    rooms_of_classes = {}
    rooms_of_classes_aux = x.get("rooms_of_classes")
    for k, r in rooms_of_classes_aux.items():
        rooms_of_classes[int(k)] = r

    times_of_classes = {}
    times_of_classes_aux = x.get("times_of_classes")
    for k, t in times_of_classes_aux.items():
        times_of_classes[int(k)] = t

    start_time = time.time() - x.get("runtime")

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write(date_time())
        output_file.write("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))
    print(date_time())
    print("*** TOTAL DE TURMAS ALOCADAS SEM CONFLITO: " + str(len(rooms_of_classes.keys())))

    # return None
    # input("PRESS ENTER...")
    # print(dict_of_id_classes_in_common_hard_constraints)
    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)

    if output_file:
        print("GRAVANDO ARQUIVO .OUT")
        output_file.write("INICIANDO SIMULATED ANNEALING...")
    print("INICIANDO SIMULATED ANNEALING...")
    rooms_of_classes, times_of_classes = \
        simulated_annealing(problem, start_time, rooms_of_classes, times_of_classes,
                            0.999, 100, 10000, 0.00001, output_file, json_file)

    if len(rooms_of_classes) == len(problem.classes):
        if output_file:
            print("GRAVANDO ARQUIVO .OUT")
            output_file.write("SUCESSO! SOLUCAO ENCONTRADA!")
        print("SUCESSO! SOLUCAO ENCONTRADA!")
        # input("PRESS ENTER...")
        return transfer_solution(problem, rooms_of_classes, times_of_classes)
    else:
        return None


def temporary_function(problem: Problem, json_solution) -> Solution:
    solution = Algorithm.build_greedy_initial_solution(problem)
    Algorithm.enroll_students(solution)
    solution.cores = 8
    solution.technique = "Greedy Algorithm"
    solution.author = "Marlucio Pires"
    solution.institution = "UFOP"
    solution.country = "Brasil"
    count_aux = 0
    print("VERIFICANDO ALOCACAO DE TURMAS...")
    times_of_classes = json_solution.get(StrConst.TIMES_OF_CLASSES.value)
    rooms_of_classes = json_solution.get(StrConst.ROOMS_OF_CLASSES.value)
    for id_class, id_time in times_of_classes.items():
        count_aux += 1
        id_room = rooms_of_classes[id_class]
        solution.classes_solution[id_class].id_time = id_time
        solution.classes_solution[id_class].id_room = id_room
    print("NR. TURMAS ALOCADAS COM USO DO MIP = %d" % count_aux)
    print("NR. DE TURMAS DO PROBLEMA = %d" % len(problem.classes))

    print("SOLUCAO VALIDA? R: " +
          str(Algorithm.validate_respect_of_hard_constraints_in_solution(
              problem, rooms_of_classes, times_of_classes)))

    return solution


def optimization_with_gurobi(
        problem: Problem, start_time: float
) -> Solution:
    mip_uctp = UCTPModelIntegerProgramming(problem)

    # mip_uctp.hard_constraints_to_add[Const.SAME_START] = False
    # mip_uctp.hard_constraints_to_add[Const.SAME_TIME] = False
    # mip_uctp.hard_constraints_to_add[Const.DIFFERENT_TIME] = False
    # mip_uctp.hard_constraints_to_add[Const.SAME_DAYS] = False
    # mip_uctp.hard_constraints_to_add[Const.DIFFERENT_DAYS] = False
    # mip_uctp.hard_constraints_to_add[Const.SAME_WEEKS] = False
    # mip_uctp.hard_constraints_to_add[Const.DIFFERENT_WEEKS] = False
    # mip_uctp.hard_constraints_to_add[Const.OVERLAP] = False
    # mip_uctp.hard_constraints_to_add[Const.NOT_OVERLAP] = False
    # mip_uctp.hard_constraints_to_add[Const.PRECEDENCE] = False
    # mip_uctp.hard_constraints_to_add[Const.SAME_ROOM] = False
    # mip_uctp.hard_constraints_to_add[Const.DIFFERENT_ROOM] = False
    # mip_uctp.hard_constraints_to_add[Const.SAME_ATTENDEES] = False
    # mip_uctp.hard_constraints_to_add[Const.WORK_DAY] = False
    # mip_uctp.hard_constraints_to_add[Const.MIN_GAP] = False
    # mip_uctp.hard_constraints_to_add[Const.MAX_DAYS] = False
    # mip_uctp.hard_constraints_to_add[Const.MAX_DAY_LOAD] = False
    # mip_uctp.hard_constraints_to_add[Const.MAX_BREAKS] = False
    # mip_uctp.hard_constraints_to_add[Const.MAX_BLOCK] = False

    # mip_uctp.soft_constraints_to_add[Const.SAME_START] = False
    # mip_uctp.soft_constraints_to_add[Const.SAME_TIME] = False
    # mip_uctp.soft_constraints_to_add[Const.DIFFERENT_TIME] = False
    # mip_uctp.soft_constraints_to_add[Const.SAME_DAYS] = False
    # mip_uctp.soft_constraints_to_add[Const.DIFFERENT_DAYS] = False
    # mip_uctp.soft_constraints_to_add[Const.SAME_WEEKS] = False
    # mip_uctp.soft_constraints_to_add[Const.DIFFERENT_WEEKS] = False
    # mip_uctp.soft_constraints_to_add[Const.OVERLAP] = False
    # mip_uctp.soft_constraints_to_add[Const.NOT_OVERLAP] = False
    # mip_uctp.soft_constraints_to_add[Const.PRECEDENCE] = False
    # mip_uctp.soft_constraints_to_add[Const.SAME_ROOM] = False
    # mip_uctp.soft_constraints_to_add[Const.DIFFERENT_ROOM] = False
    # mip_uctp.soft_constraints_to_add[Const.SAME_ATTENDEES] = False
    # mip_uctp.soft_constraints_to_add[Const.WORK_DAY] = False
    # mip_uctp.soft_constraints_to_add[Const.MIN_GAP] = False
    # mip_uctp.soft_constraints_to_add[Const.MAX_DAYS] = False
    # mip_uctp.soft_constraints_to_add[Const.MAX_DAY_LOAD] = False
    # mip_uctp.soft_constraints_to_add[Const.MAX_BREAKS] = False
    # mip_uctp.soft_constraints_to_add[Const.MAX_BLOCK] = False

    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_START] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_TIME] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.DIFFERENT_TIME] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_DAYS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.DIFFERENT_DAYS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_WEEKS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.DIFFERENT_WEEKS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.OVERLAP] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.NOT_OVERLAP] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.PRECEDENCE] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_ROOM] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.DIFFERENT_ROOM] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.SAME_ATTENDEES] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.WORK_DAY] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.MIN_GAP] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.MAX_DAYS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.MAX_DAY_LOAD] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.MAX_BREAKS] = True
    # mip_uctp.hard_constraints_to_add_cuts[Const.MAX_BLOCK] = True

    name_file = "final_results\\middle\\saida_pu-proj-fal19.json"
    xml_file = "output\\saida_pu-proj-fal19.xml"
    json_file = "output\\saida_pu-proj-fal19.json"
    if name_file:
        mip_uctp.param_initial_solution = read_solution_from_json_file(name_file)
        if mip_uctp.param_initial_solution:
            # print(mip_uctp.param_initial_solution)
            solution = temporary_function(problem, mip_uctp.param_initial_solution)
            if solution:
                solution.runtime = "%s" % round(mip_uctp.param_initial_solution[StrConst.RUNTIME.value], 1)
                solution_xml_file = xml_file
                name_json_file = json_file
                if solution_xml_file:
                    print("GRAVANDO SOLUCAO...")
                    FileXML.write_file_xml(solution_xml_file, solution)
                    write_file_json(name_json_file, solution, solution.runtime)
                    FileXML.validate_file_xml(solution_xml_file, "competition-format.dtd")
                else:
                    solution_string_xml = solution.string_to_xml()
                    print(solution_string_xml)

            end_time = (time.time() - start_time)
            print("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
            sys.exit(0)

    mip_uctp.param_add_hard_constraints = True
    # mip_uctp.param_add_hard_constraints = False

    # mip_uctp.param_use_cliques = True
    mip_uctp.param_use_cliques = False

    # mip_uctp.param_add_soft_constraints = True
    mip_uctp.param_add_soft_constraints = False

    # mip_uctp.param_add_constraints_for_students_enrollment = True
    mip_uctp.param_add_constraints_for_students_enrollment = False

    # mip_uctp.param_lazy_constraints = True

    # mip_uctp.param_time_limit = 100

    # mip_uctp.param_max_solutions = 1

    # mip_uctp.param_threads = 1

    # mip_uctp.param_relax = True

    solution = mip_uctp.build_model_and_get_solution()

    end_time = (time.time() - start_time)
    if solution:
        solution.runtime = "%s" % round(end_time, 1)
    print("--- SOLUCAO: %s seconds ---" % round(end_time, 3))
    
    return solution


def count_dependencies_classes_in_hard_constraints(problem: Problem):
    dict_aux = generate_dict_of_id_classes_in_common_hard_constraints(problem)
    print(dict_aux)
    count_set = set()
    for v in dict_aux.values():
        count_set.add(len(v))
    print("CONTAGEM: %s" % str(count_set))


def processate_line_command_params(argv):
    line_command_params = deepcopy(argv)
    params_dict = {}
    nr_params = len(line_command_params)
    # max_time = -1
    if nr_params == 0:
        print("\n\tErro: Sintaxe incorreta!")
        print("\n\tSintaxe: python main.py [m=1|2 [t=VALOR EM SEGUNDOS]] " +
              "[s=solucao_inicial.json] instancia.xml [saida.xml]")
        print("\n\tParametros:")
        print("\t\tO parametro m eh opcional: 1 (valor default) resolve por " +
              "MIP e 2 por tentativas aleatorias.")
        print("\t\tO parametro t eh opcional e indica o tempo maximo em " +
              "segundos que se deseja executar o programa, caso o modo de " +
              "execucao escolhido seja por tentativas aleatorias (m=2).")
        print("\t\tO parametro s eh opcional e deve conter a localizacao e " +
              "nome do arquivo .json com a solucao inicial, caso o modo de " +
              "execucao escolhido seja por MIP (m=1).")
        print("\t\tO arquivo \"instancia.xml\" eh a instancia de entrada do " +
              "problema.")
        print("\t\tO arquivo \"saida.xml\" (opcional) indica onde sera " +
              "gravada a solucao. Se nao fornecido, a solucao eh exibida na " +
              "tela.")
        sys.exit(0)
    else:
        pos = 0
        while pos < len(line_command_params):
            p = line_command_params[pos]
            if p.find("t=") != -1 or p.find("T=") != -1:
                max_time = float(p.split('=')[1])
                if max_time <= 0:
                    max_time = -1
                params_dict[StrConst.MAX_TIME] = max_time
                del line_command_params[pos]
            elif p == "m=1" or p == "M=1":
                params_dict[StrConst.EXECUTION_MODE] = Const.MIP
                del line_command_params[pos]
            elif p == "m=2" or p == "M=2":
                params_dict[StrConst.EXECUTION_MODE] = Const.NOT_MIP
                del line_command_params[pos]
            elif p.find("s=") != -1 or p.find("S=") != -1:
                params_dict[StrConst.INITITAL_SOLUTION] = p.split('=')[1]
                del line_command_params[pos]
            else:
                pos += 1
        if not params_dict.get(StrConst.EXECUTION_MODE):
            params_dict[StrConst.EXECUTION_MODE] = Const.MIP
        if len(line_command_params):
            params_dict[StrConst.INSTANCE_XML_FILE] = line_command_params[0]
            if len(line_command_params) > 1:
                params_dict[StrConst.SOLUTION_XML_FILE] = line_command_params[1]
                params_dict[StrConst.OUTPUT_FILE] = line_command_params[1].split('.')[0] + ".out"
                params_dict[StrConst.JSON_FILE] = line_command_params[1].split('.')[0] + ".json"
    return params_dict


def main(pool):
    """ Função principal da aplicação.
    """
    sys.setrecursionlimit(100000)
    # print("LIMITE MAX. DE RECURSAO: " + str(sys.getrecursionlimit()))

    start_time = time.time()
    params_dict = processate_line_command_params(sys.argv[1:])
    # mip = True
    # max_time = -1

    instance_xml_file = params_dict.get(StrConst.INSTANCE_XML_FILE)
    if not instance_xml_file:
        print("ERRO: Indique o arquivo .xml com a instancia de entrada!")
        sys.exit(0)

    file_xml = FileXML(instance_xml_file)

    problem = file_xml.get_obj_problem
    print("MAX. PENALTIES = %d" % problem.max_penalties)

    # print("COMBINACOES DE CURSOS:")
    # dict_id_courses_id_combinations = {}
    # count_aux = 1
    # for id_course, list_of_combinations in problem.classes_combinations_per_course.items():
    #     nr_combinations = len(list_of_combinations)
    #     print("ID DO CURSO: %d, LISTA DE COMBINACOES (TAM: %d): %s" %
    #           (id_course, nr_combinations, str(list_of_combinations)))
    #     dict_id_courses_id_combinations[id_course] = \
    #         [id_combination for id_combination in range(count_aux, (nr_combinations + count_aux))]
    #     count_aux += nr_combinations
    #     print("ID DO CURSO: %d, LISTA DE IDS DE COMBINACOES (TAM: %d): %s" %
    #           (id_course,
    #            len(dict_id_courses_id_combinations[id_course]),
    #            str(dict_id_courses_id_combinations[id_course])))
    #
    #
    # input("PRESS ENTER...")
    # problem.generate_ids_for_course_combinations()
    # print(problem.generate_combinations_of_id_classes_by_id_student(3))
    # input("PRESS ENTER...")

    # for id, student in problem.students.items():
    #     print("ID DO ESTUDANTE: %d, CURSOS: %s" % (id, str(student.courses)))

    # for id_class, obj_class in problem.classes.items():
    #     print("ID DA TURMA: %d, VAGAS: %d" %(id_class, obj_class.limit))
    # input("PRESS ENTER...")

    # initial_time_execution = str(datetime.now())
    # arq = open("output\\" + problem.name + ".txt", 'w')
    # arq.write("Execução iniciada em " + initial_time_execution)
    # arq.close()

    print("NR. FIXED CLASSES = " + str(len(problem.fixed_classes)))

    # problem.make_dict_conflict_ids()
    # problem.generate_matrix_classes_per_combination()
    # problem.generate_matrix_combinations_per_student()
    # if mip:
    #     problem.generate_constraints_conflict_matrix()

    # print(Constraint.max_block_hard(
    #     [2240, 2204, 556, 576, 558, 555, 2273, 2203, 557, 2276], 40, 9, problem,
    #     {2240:2559, 2204:2644, 556:330, 576:674, 558:326, 555:326, 2273:2580,
    #      2203:1532, 557:326, 2276:2639}))

    # print("CRIACAO DE CLIQUES SAME ATTENDEES...")
    # problem.create_cliques()
    # print("FIM DA CRIACAO DE CLIQUES SAME ATTENDEES")

    end_time = (time.time() - start_time)
    print("--- GERACAO DAS MATRIZES: %s seconds ---" % round(end_time, 3))

    # start_time = time.time()
    # problem.generate_all_neighborhood_coefficient()
    # print(problem.dict_neighborhood_coefficient_id_to_id)
    # end_time = (time.time() - start_time)
    # print("--- GERACAO DAS MATRIZES: %s seconds ---" % round(end_time, 3))
    # sys.exit(0)
    
    # input("PRESS ENTER...")

    """ ========================================================== 
                    ÁREA RESERVADA PARA TESTES
    ============================================================== """

    # print(problem.generate_ids_per_slot())
    # dict_list_of_id_classes_per_room = problem.generate_dict_list_of_id_classes_per_room()
    # print(dict_list_of_id_classes_per_room)
    # pdb.set_trace()
    # input("PRESSIONE ENTER...")
    # list_of_ids_classes = [1, 2]
    # id_room = 6
    # dict_ids_per_slot_in_a_room = problem.generate_ids_per_slot_in_a_room(list_of_ids_classes, id_room)
    # print([tuple for tuple in dict_ids_per_slot_in_a_room[1, 1, 102]])
    # pdb.set_trace()
    # input("PRESSIONE ENTER...")

    """id_class = 4
    print(("SALAS DA TURMA C%d: " % id_class) + str(list(problem.classes[id_class].rooms.keys())))
    print(("HORARIOS DA TURMA C%d: " % id_class) + str(list(problem.classes[id_class].times.keys())))
    print("HORARIOS DISPONIVEIS POR SALA:")
    for id_room in problem.classes[id_class].rooms.keys():
        print(("SALA R%d: " % id_room) + str(problem.possible_times_per_room_and_class(id_class, id_room)))

    pdb.set_trace()

    input("PRESS ENTER...")"""

    """ ========================================================== 
                    FIM DA ÁREA RESERVADA PARA TESTES
        ============================================================== """

    # solution = None
    output_file = None
    json_file = None
    if params_dict.get(StrConst.EXECUTION_MODE) == Const.MIP:
        # if params_dict.get(StrConst.OUTPUT_FILE):
        #     output_file = OutputFile(params_dict.get(StrConst.OUTPUT_FILE))
        # if params_dict.get(StrConst.JSON_FILE):
        #     json_file = params_dict.get(StrConst.JSON_FILE)
        # initial_solution_file = params_dict.get(StrConst.INITITAL_SOLUTION)

        # if initial_solution_file:
        #     is_valid_initial_solution = validate_solution_json(problem, initial_solution_file)
        #     print("RESULTADO DE VALIDACAO DA SOLUCAO: " + str(is_valid_initial_solution))

        # solution = optimization_class_by_class_with_initial_solution(
        #     problem, start_time, output_file, json_file, initial_solution_file)

        # solution = optimization_class_by_class(problem, start_time, output_file, json_file)

        # solution = optimization_by_parts(problem)
        # solution = optimization_with_gurobi_adaptive(problem, start_time)

        # pdb.set_trace()
        # relax = True
        # add_soft_constraints = False
        # add_hard_constraints = False
        solution = optimization_with_gurobi(problem, start_time)

        # solution = optimization_with_gurobi(problem, start_time)

        # if solution:
        #     end_time = (time.time() - start_time)
        #     solution.runtime = "%s" % round(end_time, 1)
    else:
        # if params_dict.get(StrConst.OUTPUT_FILE):
        #     output_file = OutputFile(params_dict.get(StrConst.OUTPUT_FILE))
        # if params_dict.get(StrConst.JSON_FILE):
        #     json_file = params_dict.get(StrConst.JSON_FILE)
        # solution = greedy_algorithm_class_by_class_v2(problem, start_time, output_file, json_file)

        # solution = build_valid_solutions(problem, start_time, max_time)
        # solution = build_valid_solutions_techniques_mixing(problem, start_time, max_time)

        # print("ENTROU")
        """======================================================
                    AREA DE TESTE DO MULTIPROCESSING
        ========================================================="""
        params_dict[StrConst.OUTPUT_FILE] = params_dict[StrConst.SOLUTION_XML_FILE].split('.')[0]
        params_dict[StrConst.JSON_FILE] = params_dict[StrConst.SOLUTION_XML_FILE].split('.')[0]
        solution = test_multiprocessing(
            pool, problem, start_time, params_dict[StrConst.OUTPUT_FILE], params_dict[StrConst.JSON_FILE], 1000)
        # print("NUMERO DE TURMAS DO PROBLEMA: %d" % len(problem.classes))
        # print("NUMERO DE TURMAS NAO ALOCADAS NO ALGORITMO GULOSO: %d" % greedy_algorithm_class_by_class_v3(
        #     (problem, start_time, params_dict[StrConst.OUTPUT_FILE], params_dict[StrConst.JSON_FILE])))

        # solution = None
        """======================================================
                FIM DA AREA DE TESTE DO MULTIPROCESSING
        ========================================================="""

    if solution:
        end_time = (time.time() - start_time)
        solution.runtime = "%s" % round(end_time, 1)
        solution_xml_file = params_dict.get(StrConst.SOLUTION_XML_FILE)
        name_json_file = params_dict.get(StrConst.SOLUTION_XML_FILE).split(".")[0] + ".json"
        if solution_xml_file:
            print("GRAVANDO SOLUCAO...")
            FileXML.write_file_xml(solution_xml_file, solution)
            write_file_json(name_json_file, solution, end_time)
            FileXML.validate_file_xml(solution_xml_file, "competition-format.dtd")
        else:
            solution_string_xml = solution.string_to_xml()
            print(solution_string_xml)

    end_time = (time.time() - start_time)
    print("--- TEMPO TOTAL DE EXECUCAO: %s seconds ---" % round(end_time, 3))
    # pdb.set_trace()

    # output_file.write_forced("")


def write_file_json(name_json_file: str, solution: Solution, end_time) -> None:
    print("GRAVANDO SOLUCAO NO ARQUIVO .JSON")
    list_id_classes_not_allocated = []
    rooms_of_classes = {}
    times_of_classes = {}
    students_of_classes = {}
    for id_class in solution.problem.classes.keys():
        class_solution_i = solution.classes_solution.get(id_class)
        if class_solution_i:
            times_of_classes[id_class] = class_solution_i.id_time
            rooms_of_classes[id_class] = class_solution_i.id_room
            students_of_classes[id_class] = class_solution_i.students
        else:
            list_id_classes_not_allocated.append(id_class)
    f = open(name_json_file, 'w')
    json_obj = {"instance": solution.problem.name,
                "datetime": date_time(),
                "runtime": end_time,
                "rooms_of_classes": rooms_of_classes,
                "times_of_classes": times_of_classes,
                "list_id_classes_not_allocated": list_id_classes_not_allocated,
                "students_of_classes": students_of_classes}
    json.dump(json_obj, f)
    f.close()


if __name__ == "__main__":
    pool = Pool()
    main(pool)
    sys.exit(0)
