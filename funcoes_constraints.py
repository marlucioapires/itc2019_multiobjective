# -*- coding: utf-8 -*-


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
