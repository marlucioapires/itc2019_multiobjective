# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
from constants import Const, StrConst


# Merges two subarrays of arr[].
# First subarray is arr[l..m]
# Second subarray is arr[m+1..r]
def merge(arr: List[Dict], l: int, m: int, r: int):
    n1 = m - l + 1
    n2 = r - m

    # create temp arrays
    array_left = []
    array_right = []

    # Copy data to temp arrays L[] and R[]
    for i in range(0, n1):
        array_left.append(arr[l + i])

    for j in range(0, n2):
        array_right.append(arr[m + 1 + j])

        # Merge the temp arrays back into arr[l..r]
    i = 0  # Initial index of first subarray
    j = 0  # Initial index of second subarray
    k = l  # Initial index of merged subarray

    while i < n1 and j < n2:
        if array_left[i][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] < \
                array_right[j][StrConst.FO_1.value][Const.HARD_CONFLICTS.value]:
            arr[k] = array_left[i]
            i += 1
        elif array_left[i][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] == \
                array_right[j][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] and \
                array_left[i][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value] < \
                array_right[j][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value]:
            arr[k] = array_left[i]
            i += 1
        elif array_left[i][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] == \
                array_right[j][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] and \
                array_left[i][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value] == \
                array_right[j][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value] and \
                array_left[i][StrConst.FO_2.value][Const.HARD_CONFLICTS.value] < \
                array_right[j][StrConst.FO_2.value][Const.HARD_CONFLICTS.value]:
            arr[k] = array_left[i]
            i += 1
        elif array_left[i][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] == \
                array_right[j][StrConst.FO_1.value][Const.HARD_CONFLICTS.value] and \
                array_left[i][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value] == \
                array_right[j][StrConst.FO_1.value][Const.SOFT_CONFLICTS.value] and \
                array_left[i][StrConst.FO_2.value][Const.HARD_CONFLICTS.value] == \
                array_right[j][StrConst.FO_2.value][Const.HARD_CONFLICTS.value] and \
                array_left[i][StrConst.FO_2.value][Const.SOFT_CONFLICTS.value] < \
                array_right[j][StrConst.FO_2.value][Const.SOFT_CONFLICTS.value]:
            arr[k] = array_left[i]
            i += 1
        else:
            arr[k] = array_right[j]
            j += 1
        k += 1

    # Copy the remaining elements of L[], if there
    # are any
    while i < n1:
        arr[k] = array_left[i]
        i += 1
        k += 1

    # Copy the remaining elements of R[], if there
    # are any
    while j < n2:
        arr[k] = array_right[j]
        j += 1
        k += 1


# l is for left index and r is right index of the
# sub-array of arr to be sorted
def merge_sort(arr: List[Dict], l: int, r: int):
    if l < r:
        # Same as (l+r)/2, but avoids overflow for
        # large l and h
        m = (l + (r - 1)) // 2

        # Sort first and second halves
        merge_sort(arr, l, m)
        merge_sort(arr, m + 1, r)
        merge(arr, l, m, r)


def sort_solutions(list_of_solutions: List[Dict]):
    merge_sort(list_of_solutions, 0, len(list_of_solutions) - 1)
