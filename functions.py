# -*- coding: utf-8 -*-

import time
import math
from typing import Dict, List


def verify_is_time_conflicting_with_list(
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


def intersection_list(lst1, lst2):
    return [value for value in lst1 if value in lst2]


def combinations_of_two_lists(
        list_of_list: List[List[int]], list_of_int: List[int]) -> List[List[int]]:
    list_final = []
    for iter_list in list_of_list:
        for iter_int in list_of_int:
            list_aux = list(iter_list)
            list_aux.append(iter_int)
            list_final.append(list_aux)
    return list_final


# def intersection(lst):
#     tam = len(lst)
#     if tam:
#         result = lst[0]
#         count = 1
#         while count < tam:
#             if not result or not lst[count]:
#                 return []
#             result = [value for value in result if value in lst[count]]
#             count += 1
#         return result
#     return []


def number_of_combinations(n, p):
    return math.factorial(n) / (math.factorial(p) * math.factorial((n - p)))


def date_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def union(list_of_items1: List[object],
          list_of_items2: List[object]) -> List[object]:
    union_list = set(list_of_items1)
    for item_2 in list_of_items2:
        union_list.add(item_2)
    return list(union_list)


def intersection(list_of_items1: List[object],
                 list_of_items2: List[object]) -> List[object]:
    return [item_1 for item_1 in list_of_items1
            if item_1 in list_of_items2]


def intersection_int(list_of_items1: List[int],
                     list_of_items2: List[int]) -> List[int]:
    return [item_1 for item_1 in list_of_items1
            if item_1 in list_of_items2]


def has_intersection(list_of_items1: List[object],
                     list_of_items2: List[object]) -> bool:
    if list_of_items1 and list_of_items2:
        for item_i in list_of_items1:
            if item_i in list_of_items2:
                return True
    return False


def add_recursively(key: int, dictionary, list_of_keys: List[int], processed) -> None:
    if key not in processed:
        processed.add(key)
        list_of_keys.append(key)
        for k in dictionary[key]:
            add_recursively(k, dictionary, list_of_keys, processed)


def add_different_items_list(list1: List[int], list2: List[int]) -> None:
    for j in list2:
        if j not in list1:
            list1.append(j)


def merge_items_list(
        list_of_lists: List[List[int]], list_of_positions: List[int]
) -> bool:
    list_of_positions_aux = sorted(list_of_positions)
    for i in list_of_positions_aux:
        if i < 0 or i >= len(list_of_lists):
            return False
    if len(list_of_positions_aux) <= 1:
        return True
    first_list = list_of_lists[list_of_positions_aux[0]]
    for i in list_of_positions_aux[1:]:
        another_list = list_of_lists[i]
        add_different_items_list(first_list, another_list)
    count = 0
    for i in list_of_positions_aux[1:]:
        del list_of_lists[(i - count)]
        count += 1
    return True


def calculate_intersection_groups_of_hard_constraints(
        problem) -> List[List[int]]:
    intersection_per_dist = {}
    for hard_dist_i in problem.distributions_hard:
        intersection_per_dist[hard_dist_i.id] = []
        for hard_dist_j in problem.distributions_hard:
            if hard_dist_i.id != hard_dist_j.id and \
                    has_intersection(hard_dist_i.classes, hard_dist_j.classes):
                intersection_per_dist[hard_dist_i.id].append(hard_dist_j.id)

    processed = set()
    final_list = []
    for hard_dist_i in problem.distributions_hard:
        list_of_intersection = []
        add_recursively(hard_dist_i.id, intersection_per_dist,
                        list_of_intersection, processed)
        if list_of_intersection:
            final_list.append(list_of_intersection)

    return final_list


def generate_dict_list_of_id_constraints_per_class(
        list_of_constraints
) -> Dict[int, List[int]]:
    dict_list_of_id_constraints_per_class = {}

    for constraint in list_of_constraints:
        list_of_classes = constraint.classes
        id_constraint = constraint.id
        for id_class in list_of_classes:
            if id_class not in dict_list_of_id_constraints_per_class:
                dict_list_of_id_constraints_per_class[id_class] = \
                    [id_constraint, ]
            else:
                dict_list_of_id_constraints_per_class[id_class].append(
                    id_constraint)

    return dict_list_of_id_constraints_per_class


def generate_list_of_groups_of_hard_constraints(
        list_of_constraints):
    dict_list_of_id_constraints_per_class = \
        generate_dict_list_of_id_constraints_per_class(list_of_constraints)

    list_of_hard_constraints_grouped_by_class = \
        list(dict_list_of_id_constraints_per_class.values())

    i = 0
    while i < len(list_of_hard_constraints_grouped_by_class):
        # print("LISTA ANTES DA MESCLAGEM: %s" % str(list_of_hard_constraints_grouped_by_class))
        list_of_positions = [i, ]
        for j, group in enumerate(list_of_hard_constraints_grouped_by_class):
            if i != j:
                if has_intersection(
                        list_of_hard_constraints_grouped_by_class[i], group):
                    list_of_positions.append(j)
                    if j < i:
                        i = j
                    else:
                        i += 1
                    break
        # print("POSICOES A SEREM MESCLADAS: %s" % str(list_of_positions))

        merge_items_list(list_of_hard_constraints_grouped_by_class,
                         list_of_positions)
        # print("LISTA APOS MESCLAGEM: %s" % str(list_of_hard_constraints_grouped_by_class))
        # input("CONTINUE...")
        if len(list_of_positions) == 1:
            i += 1

    return list_of_hard_constraints_grouped_by_class
