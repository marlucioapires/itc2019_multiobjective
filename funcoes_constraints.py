# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
# from problem import Problem


class Constraint:
    @staticmethod
    def same_start(class1_start: int, class2_start: int):
        return class1_start == class2_start

    @staticmethod
    def same_time(class1_start: int, class1_end: int,
                  class2_start: int, class2_end: int):
        return (class1_start <= class2_start and
                class2_end <= class1_end) or \
               (class2_start <= class1_start and
                class1_end <= class2_end)

    @staticmethod
    def different_time(class1_start: int, class1_end: int,
                       class2_start: int, class2_end: int):
        return (class1_end <= class2_start) or \
               (class2_end <= class1_start)

    @staticmethod
    def same_days(class1_days: int, class2_days: int):
        binary_or = class1_days | class2_days
        return (binary_or == class1_days) or \
               (binary_or == class2_days)

    @staticmethod
    def different_days(class1_days: int, class2_days: int):
        return (class1_days & class2_days) == 0

    @staticmethod
    def same_weeks(class1_weeks: int, class2_weeks: int):
        binary_or = class1_weeks | class2_weeks
        return (binary_or == class1_weeks) or \
               (binary_or == class2_weeks)

    @staticmethod
    def different_weeks(class1_weeks: int, class2_weeks: int):
        return (class1_weeks & class2_weeks) == 0

    @staticmethod
    def overlap(class1_start: int, class1_end: int,
                class2_start: int, class2_end: int,
                class1_days: int, class2_days: int,
                class1_weeks: int, class2_weeks: int):
        return ((class2_start < class1_end) and
                (class1_start < class2_end)) and \
               ((class1_days & class2_days) != 0) and \
               ((class1_weeks & class2_weeks) != 0)

    @staticmethod
    def not_overlap(class1_start: int, class1_end: int,
                    class2_start: int, class2_end: int,
                    class1_days: int, class2_days: int,
                    class1_weeks: int, class2_weeks: int):
        return ((class1_end <= class2_start) or
                (class2_end <= class1_start)) or \
               ((class1_days & class2_days) == 0) or \
               ((class1_weeks & class2_weeks) == 0)

    @staticmethod
    def same_room(class1_room: int, class2_room: int):
        return class1_room == class2_room

    @staticmethod
    def different_room(class1_room: int, class2_room: int):
        return class1_room != class2_room

    @staticmethod
    def same_attendees(
            class1_start: int, class1_end: int, class2_start: int,
            class2_end: int, class1_days: int, class2_days: int,
            class1_weeks: int, class2_weeks: int, room_travel_value: int):
        return (class1_end + room_travel_value <= class2_start) or \
               (class2_end + room_travel_value <= class1_start) or \
               ((class1_days & class2_days) == 0) or \
               ((class1_weeks & class2_weeks) == 0)

    @staticmethod
    def precedence(class1_end: int, class2_start: int,
                   class1_days: int, class2_days: int,
                   class1_weeks: int, class2_weeks: int, nr_weeks: int):
        first_class1_weeks = \
            Constraint.first_bit_1(
                ("{0:0" + str(nr_weeks) + "b}").format(class1_weeks))
        first_class2_weeks = \
            Constraint.first_bit_1(
                ("{0:0" + str(nr_weeks) + "b}").format(class2_weeks))
        first_class1_days = \
            Constraint.first_bit_1("{0:07b}".format(class1_days))
        first_class2_days = \
            Constraint.first_bit_1("{0:07b}".format(class2_days))
        return (first_class1_weeks < first_class2_weeks) or \
               ((first_class1_weeks == first_class2_weeks) and
                ((first_class1_days < first_class2_days) or
                 ((first_class1_days == first_class2_days) and
                  (class1_end <= class2_start))))

    @staticmethod
    def work_day(class1_start: int, class1_end: int,
                 class2_start: int, class2_end: int,
                 class1_days: int, class2_days: int,
                 class1_weeks: int, class2_weeks: int, s: int):
        return ((class1_days & class2_days) == 0) or \
               ((class1_weeks & class2_weeks) == 0) or \
               (max(class1_end, class2_end) -
                min(class1_start, class2_start) <= s)

    @staticmethod
    def min_gap(class1_start: int, class1_end: int,
                class2_start: int, class2_end: int,
                class1_days: int, class2_days: int,
                class1_weeks: int, class2_weeks: int, g: int):
        return ((class1_days & class2_days) == 0) or \
               ((class1_weeks & class2_weeks) == 0) or \
               (class1_end + g <= class2_start) or \
               (class2_end + g <= class1_start)

    @staticmethod
    def max_days_soft(list_of_class_ids: List[int], problem,
                      times_classes: Dict[int, int]):
        or_binary = 0
        for id_class in list_of_class_ids:
            id_time = times_classes[id_class]
            time_tuple = problem.classes[id_class].times[id_time]
            class_days = time_tuple.days
            or_binary = or_binary | class_days
        str_binary = '{0:07b}'.format(or_binary)
        return str_binary.count('1')

    @staticmethod
    def max_days_hard(
            list_of_class_ids: List[int], d: int,
            problem, times_classes: Dict[int, int]):
        return Constraint.max_days_soft(
            list_of_class_ids, problem, times_classes) <= d

    @staticmethod
    def max_day_load_soft(
            list_of_class_ids: List[int], s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        sum_w_d = 0
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                day_load = 0
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_i_length = time_tuple.length
                    c_i_days = time_tuple.days
                    c_i_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_i_days & binary_2_d != 0) and
                            (c_i_weeks & binary_2_w != 0)):
                        day_load += c_i_length

                sum_w_d += max(day_load - s, 0)

        return sum_w_d

    @staticmethod
    def max_day_load_hard(
            list_of_class_ids: List[int], s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                day_load = 0
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_i_length = time_tuple.length
                    c_i_days = time_tuple.days
                    c_i_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_i_days & binary_2_d != 0) and
                            (c_i_weeks & binary_2_w != 0)):
                        day_load += c_i_length

                if day_load > s:
                    return False

        return True

    @staticmethod
    def max_breaks_soft(
            list_of_class_ids: List[int], r: int, s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        sum_w_d = 0
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                blocks = []
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_start = time_tuple.start
                    c_end = time_tuple.end
                    c_days = time_tuple.days
                    c_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_days & binary_2_d != 0) and
                            (c_weeks & binary_2_w != 0)):
                        blocks.append((c_start, c_end))

                if len(blocks) > 1:
                    Constraint.merge_sort(blocks, 0, (len(blocks) - 1))

                    list_of_merged_blocks = [blocks[0]]
                    for block in blocks[1:]:
                        is_merge, merged_block = \
                            Constraint.merge_blocks(
                                s, list_of_merged_blocks[-1][0],
                                list_of_merged_blocks[-1][1],
                                block[0], block[1])
                        if is_merge:
                            list_of_merged_blocks[-1] = merged_block
                        else:
                            list_of_merged_blocks.append(block)

                    sum_w_d += max((len(list_of_merged_blocks) - (r + 1)), 0)

        return sum_w_d

    @staticmethod
    def max_breaks_hard(
            list_of_class_ids: List[int], r: int, s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                blocks = []
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_start = time_tuple.start
                    c_end = time_tuple.end
                    c_days = time_tuple.days
                    c_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_days & binary_2_d != 0) and
                            (c_weeks & binary_2_w != 0)):
                        blocks.append((c_start, c_end))

                if len(blocks) > 1:
                    Constraint.merge_sort(blocks, 0, (len(blocks) - 1))

                    list_of_merged_blocks = [blocks[0]]
                    for block in blocks[1:]:
                        is_merge, merged_block = \
                            Constraint.merge_blocks(
                                s, list_of_merged_blocks[-1][0],
                                list_of_merged_blocks[-1][1],
                                block[0], block[1])
                        if is_merge:
                            list_of_merged_blocks[-1] = merged_block
                        else:
                            list_of_merged_blocks.append(block)

                    if len(list_of_merged_blocks) > (r + 1):
                        return False

        return True

    @staticmethod
    def max_block_soft(
            list_of_class_ids: List[int], m: int, s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        sum_w_d = 0
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                blocks = []
                count_classes = 0
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_start = time_tuple.start
                    c_end = time_tuple.end
                    c_days = time_tuple.days
                    c_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_days & binary_2_d != 0) and
                            (c_weeks & binary_2_w != 0)):
                        count_classes += 1
                        blocks.append((c_start, c_end))

                if count_classes <= 1:
                    continue

                Constraint.merge_sort(blocks, 0, (len(blocks) - 1))

                list_of_merged_blocks = [blocks[0], ]
                for block in blocks[1:]:
                    is_merge, merged_block = \
                        Constraint.merge_blocks(
                            s, list_of_merged_blocks[-1][0],
                            list_of_merged_blocks[-1][1],
                            block[0], block[1])
                    if is_merge:
                        list_of_merged_blocks[-1] = merged_block
                    else:
                        list_of_merged_blocks.append(block)

                for block in list_of_merged_blocks:
                    b_end = block[1]
                    b_start = block[0]
                    sum_w_d += max(((b_end - b_start) - m), 0)

        return sum_w_d

    @staticmethod
    def max_block_hard(
            list_of_class_ids: List[int], m: int, s: int,
            problem, times_classes: Dict[int, int]):
        nr_weeks = problem.nr_weeks
        nr_days = problem.nr_days
        for w in range(nr_weeks):
            str_2_w = ('{0:0' + str(nr_weeks) + 'b}').format(0)
            str_2_w = str_2_w[:w] + '1' + str_2_w[(w + 1):]

            for d in range(nr_days):
                str_2_d = ('{0:0' + str(nr_days) + 'b}').format(0)
                str_2_d = str_2_d[:d] + '1' + str_2_d[(d + 1):]

                blocks = []
                count_classes = 0
                for c in list_of_class_ids:
                    id_time = times_classes[c]
                    time_tuple = problem.classes[c].times[id_time]
                    c_start = time_tuple.start
                    c_end = time_tuple.end
                    c_days = time_tuple.days
                    c_weeks = time_tuple.weeks
                    binary_2_d = int(str_2_d, 2)
                    binary_2_w = int(str_2_w, 2)

                    if ((c_days & binary_2_d != 0) and
                            (c_weeks & binary_2_w != 0)):
                        count_classes += 1
                        blocks.append((c_start, c_end))

                if count_classes <= 1:
                    continue

                Constraint.merge_sort(blocks, 0, (len(blocks) - 1))

                list_of_merged_blocks = [blocks[0], ]
                for block in blocks[1:]:
                    is_merge, merged_block = \
                        Constraint.merge_blocks(
                            s, list_of_merged_blocks[-1][0],
                            list_of_merged_blocks[-1][1],
                            block[0], block[1])
                    if is_merge:
                        list_of_merged_blocks[-1] = merged_block
                        b_end = list_of_merged_blocks[-1][1]
                        b_start = list_of_merged_blocks[-1][0]
                        if (b_end - b_start) > m:
                            return False
                    else:
                        list_of_merged_blocks.append(block)

        return True

    @staticmethod
    def merge_blocks(s: int, ba_start: int,
                     ba_end: int, bb_start: int,
                     bb_end: int):
        b_start = 0
        b_end = 0
        if (ba_end + s > bb_start) and (bb_end + s > ba_start):
            b_start = min(ba_start, bb_start)
            b_end = max(ba_end, bb_end)
            return True, (b_start, b_end)
        return False, (b_start, b_end)

    @staticmethod
    def first(string: str, char: str):
        """ first(x) returns the index of the first char in the string x.
        """
        index = string.find(char)
        return index if index >= 0 else len(string)

    @staticmethod
    def first_bit_1(string: str):
        """ first_bit_1(x) returns the index of the first char '1' in the
        string x.
        """
        return Constraint.first(string, '1')

    @staticmethod
    # Merges two subarrays of arr[].
    # First subarray is arr[l..m]
    # Second subarray is arr[m+1..r]
    def merge(arr: List[Tuple[int, int]], l: int, m: int, r: int):
        n1 = m - l + 1
        n2 = r - m

        # create temp arrays
        array_left = [(0, 0)] * n1
        array_right = [(0, 0)] * n2

        # Copy data to temp arrays L[] and R[]
        for i in range(0, n1):
            array_left[i] = arr[l + i]

        for j in range(0, n2):
            array_right[j] = arr[m + 1 + j]

            # Merge the temp arrays back into arr[l..r]
        i = 0  # Initial index of first subarray
        j = 0  # Initial index of second subarray
        k = l  # Initial index of merged subarray

        while i < n1 and j < n2:
            if array_left[i][0] <= array_right[j][0]:
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

    @staticmethod
    # l is for left index and r is right index of the
    # sub-array of arr to be sorted
    def merge_sort(arr: List[Tuple[int, int]], l: int, r: int):
        if l < r:
            # Same as (l+r)/2, but avoids overflow for
            # large l and h
            m = (l + (r - 1)) // 2

            # Sort first and second halves
            Constraint.merge_sort(arr, l, m)
            Constraint.merge_sort(arr, m + 1, r)
            Constraint.merge(arr, l, m, r)
