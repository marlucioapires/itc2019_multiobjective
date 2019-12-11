# -*- coding: utf-8 -*-

from enum import IntEnum, Enum


class Const(IntEnum):
    COMBINATION_INFEASIBLE = -1
    COMBINATION_OVERFLOWED = -2

    MIP = -3
    NOT_MIP = -4

    HARD_CONFLICTS = 0
    SOFT_CONFLICTS = 1

    SAME_START = 1
    SAME_TIME = 2
    DIFFERENT_TIME = 3
    SAME_DAYS = 4
    DIFFERENT_DAYS = 5
    SAME_WEEKS = 6
    DIFFERENT_WEEKS = 7
    OVERLAP = 8
    NOT_OVERLAP = 9
    PRECEDENCE = 10
    SAME_ROOM = 11
    DIFFERENT_ROOM = 12
    SAME_ATTENDEES = 13
    WORK_DAY = 14
    MIN_GAP = 15
    MAX_DAYS = 16
    MAX_DAY_LOAD = 17
    MAX_BREAKS = 18
    MAX_BLOCK = 19

    CT_PAIR = 20
    CTR_PAIR = 21
    CR_PAIR = 22
    CT_GROUP = 23
    CTR_GROUP = 24

    def __str__(self):
        return str(self.value)


class StrConst(Enum):
    EXECUTION_MODE = "execution_mode"
    MAX_TIME = "max_time"
    INITITAL_SOLUTION = "initial_solution"
    INSTANCE_XML_FILE = "instance_xml_file"
    SOLUTION_XML_FILE = "solution_xml_file"
    OUTPUT_FILE = "output_file"
    JSON_FILE = "json_file"

    INSTANCE = "instance"
    DATETIME = "datetime"
    RUNTIME = "runtime"
    ROOMS_OF_CLASSES = "rooms_of_classes"
    TIMES_OF_CLASSES = "times_of_classes"
    LIST_ID_CLASSES_NOT_ALLOCATED = "list_id_classes_not_allocated"
    STUDENTS_OF_CLASSES = "students_of_classes"

    FO_1 = "objective_funtion_1"
    FO_2 = "objective_funtion_2"

    SAME_START = "SameStart"
    SAME_TIME = "SameTime"
    DIFFERENT_TIME = "DifferentTime"
    SAME_DAYS = "SameDays"
    DIFFERENT_DAYS = "DifferentDays"
    SAME_WEEKS = "SameWeeks"
    DIFFERENT_WEEKS = "DifferentWeeks"
    OVERLAP = "Overlap"
    NOT_OVERLAP = "NotOverlap"
    PRECEDENCE = "Precedence"
    SAME_ROOM = "SameRoom"
    DIFFERENT_ROOM = "DifferentRoom"
    SAME_ATTENDEES = "SameAttendees"
    WORK_DAY = "WorkDay"
    MIN_GAP = "MinGap"
    MAX_DAYS = "MaxDays"
    MAX_DAY_LOAD = "MaxDayLoad"
    MAX_BREAKS = "MaxBreaks"
    MAX_BLOCK = "MaxBlock"

    def __str__(self):
        return str(self.value)
