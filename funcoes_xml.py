# -*- coding: utf-8 -*-
from lxml import etree
from problem import Problem, Room, TimeTuple
from problem import Config, Course, Subpart
from problem import Class, DistributionConstraint, Student
from constants import Const


class FileXML:
    def __init__(self, arquivo=None):
        self.arquivo = arquivo
        self.xml_problem = etree.parse(arquivo).getroot() if arquivo else None
        self.optimization = self.xml_problem.find('optimization')

    @property
    def get_obj_problem(self):
        problem = Problem() if self.arquivo else None
        if problem:
            problem.name = self.get_name_problem()
            problem.nr_days = int(self.get_nr_days_problem())
            problem.nr_weeks = int(self.get_nr_weeks_problem())
            problem.slots_per_day = int(self.get_slots_per_day_problem())
            problem.weight_time = int(self.get_time_optimization())
            problem.weight_room = int(self.get_room_optimization())
            problem.weight_distribution = int(self.get_distribution_optimization())
            problem.weight_student = int(self.get_student_optimization())
            sum_max_penalties = 0

            """ids_rooms_list = []
            for room_iter in self.xml_problem.find('rooms').findall('room'):
                ids_rooms_list.append(problem.generate_int_id_room(room_iter.get('id')))"""

            index_list = 0
            room = Room(0, 0)
            problem.add_room(room)
            for room_iter in self.xml_problem.find('rooms').findall('room'):
                problem.generate_int_id_room(room_iter.get('id'))
            for room_iter in self.xml_problem.find('rooms').findall('room'):
                # id_room = problem.generate_int_id_room(room_iter.get('id'))
                id_room = problem.room_dict_str_id_to_int_id.get(room_iter.get('id'))
                capacity = int(room_iter.get('capacity'))
                room = Room(id_room, capacity)
                for travel_iter in room_iter.findall('travel'):
                    id_travel_room = problem.room_dict_str_id_to_int_id.get(travel_iter.get('room'))
                    value_travel = int(travel_iter.get('value'))
                    room.add_travel(id_travel_room, value_travel)

                for unavailable_iter in room_iter.findall('unavailable'):
                    time_tuple_str = (unavailable_iter.get('start'),
                                      unavailable_iter.get('length'),
                                      unavailable_iter.get('days'),
                                      unavailable_iter.get('weeks'))
                    if time_tuple_str not in problem.time_to_id.keys():
                        problem.time_to_id[time_tuple_str] = problem.ids_count
                        problem.id_to_time[problem.ids_count] = time_tuple_str
                        id_unavailable = problem.ids_count
                        problem.ids_count += 1

                        unavailable_start = int(time_tuple_str[0])
                        unavailable_length = int(time_tuple_str[1])
                        unavailable_days = int(time_tuple_str[2], 2)
                        unavailable_weeks = int(time_tuple_str[3], 2)
                        time_tuple = TimeTuple(id_unavailable, unavailable_days,
                                               unavailable_start,
                                               unavailable_length,
                                               unavailable_weeks)

                        problem.add_time_tuple(id_unavailable, time_tuple)
                    else:
                        id_unavailable = problem.time_to_id.get(time_tuple_str)

                    room.add_unavailable(id_unavailable)

                problem.add_room(room)
                index_list += 1

            # nr_classes_fixed = 0

            for course_iter in self.xml_problem.find('courses').findall('course'):
                id_course = problem.generate_int_id_course(course_iter.get('id'))
                course = Course(id_course)
                for config_iter in course_iter.findall('config'):
                    id_config = problem.generate_int_id_config(config_iter.get('id'))
                    config = Config(id_config)

                    ids_classes_list = []
                    for subpart_iter in config_iter.findall('subpart'):
                        for class_iter in subpart_iter.findall('class'):
                            ids_classes_list.append(problem.generate_int_id_class(class_iter.get('id')))

                    index_list = 0
                    for subpart_iter in config_iter.findall('subpart'):
                        id_subpart = problem.generate_int_id_subpart(subpart_iter.get('id'))
                        subpart = Subpart(id_subpart)
                        for class_iter in subpart_iter.findall('class'):
                            id_class = ids_classes_list[index_list]
                            limit = int(class_iter.get('limit'))
                            room = False if class_iter.get('room') else True
                            obj_class = Class(id_class, limit, room)
                            obj_class.parent = class_iter.get('parent')
                            if obj_class.parent:
                                obj_class.parent = problem.class_dict_str_id_to_int_id.get(obj_class.parent)

                            max_penalty_room = 0
                            for room_iter in class_iter.findall('room'):
                                penalty_aux = int(room_iter.get('penalty'))
                                obj_class.add_room(problem.room_dict_str_id_to_int_id.get(room_iter.get('id')),
                                                   penalty_aux)
                                if penalty_aux > max_penalty_room:
                                    max_penalty_room = penalty_aux
                            sum_max_penalties += max_penalty_room * problem.weight_room

                            if not room:
                                obj_class.add_room(0)  # Se a classe não tem room, adiciona-se a room 0 (zero).

                            max_penalty_time = 0
                            for time_iter in class_iter.findall('time'):
                                time_tuple_str = (time_iter.get('start'),
                                                  time_iter.get('length'),
                                                  time_iter.get('days'),
                                                  time_iter.get('weeks'))
                                if time_tuple_str not in problem.time_to_id.keys():
                                    problem.time_to_id[time_tuple_str] = problem.ids_count
                                    problem.id_to_time[problem.ids_count] = time_tuple_str
                                    id_time = problem.ids_count
                                    problem.ids_count += 1

                                    # Adicionando o horário às estruturas do MIP
                                    problem.ids_times.append(id_time)
                                else:
                                    id_time = problem.time_to_id.get(time_tuple_str)

                                penalty_aux = int(time_iter.get('penalty'))
                                if penalty_aux > max_penalty_time:
                                    max_penalty_time = penalty_aux

                                class_start = int(time_tuple_str[0])
                                class_length = int(time_tuple_str[1])
                                class_days = int(time_tuple_str[2], 2)
                                class_weeks = int(time_tuple_str[3], 2)
                                time_tuple = TimeTuple(id_time, class_days,
                                                       class_start,
                                                       class_length,
                                                       class_weeks,
                                                       penalty_aux)
                                obj_class.add_time(id_time, time_tuple, penalty_aux)

                                problem.add_time_tuple(id_time, time_tuple)
                            sum_max_penalties += max_penalty_time * problem.weight_time

                            subpart.add_class(obj_class)
                            problem.add_class(obj_class)
                            index_list += 1
                        config.add_subpart(subpart)
                    course.add_config(config)
                problem.add_course(course)

            iter_dist_count = 0
            for dist_iter in self.xml_problem.find('distributions').findall('distribution'):
                iter_dist_count += 1
                id_dist = iter_dist_count
                type_str = dist_iter.get('type')
                required = True if dist_iter.get('required') else False
                penalty_str = dist_iter.get('penalty')
                penalty = 0
                list_of_params = []
                type_const = 0
                if type_str == "SameStart":
                    type_const = Const.SAME_START
                elif type_str == "SameTime":
                    type_const = Const.SAME_TIME
                elif type_str == "DifferentTime":
                    type_const = Const.DIFFERENT_TIME
                elif type_str == "SameDays":
                    type_const = Const.SAME_DAYS
                elif type_str == "DifferentDays":
                    type_const = Const.DIFFERENT_DAYS
                elif type_str == "SameWeeks":
                    type_const = Const.SAME_WEEKS
                elif type_str == "DifferentWeeks":
                    type_const = Const.DIFFERENT_WEEKS
                elif type_str == "Overlap":
                    type_const = Const.OVERLAP
                elif type_str == "NotOverlap":
                    type_const = Const.NOT_OVERLAP
                elif type_str == "SameRoom":
                    type_const = Const.SAME_ROOM
                elif type_str == "DifferentRoom":
                    type_const = Const.DIFFERENT_ROOM
                elif type_str == "SameAttendees":
                    type_const = Const.SAME_ATTENDEES
                elif type_str == "Precedence":
                    type_const = Const.PRECEDENCE
                elif type_str.find("WorkDay") != -1:
                    s = int(type_str.split('(')[1].split(')')[0])
                    list_of_params.append(s)
                    type_const = Const.WORK_DAY
                elif type_str.find("MinGap") != -1:
                    g = int(type_str.split('(')[1].split(')')[0])
                    list_of_params.append(g)
                    type_const = Const.MIN_GAP
                elif type_str.find("MaxDays") != -1:
                    d = int(type_str.split('(')[1].split(')')[0])
                    list_of_params.append(d)
                    type_const = Const.MAX_DAYS
                elif type_str.find("MaxDayLoad") != -1:
                    s = int(type_str.split('(')[1].split(')')[0])
                    list_of_params.append(s)
                    type_const = Const.MAX_DAY_LOAD
                elif type_str.find("MaxBreaks") != -1:
                    params = type_str.split('(')[1].split(')')[0].split(',')
                    r = int(params[0])
                    s = int(params[1])
                    list_of_params.append(r)
                    list_of_params.append(s)
                    type_const = Const.MAX_BREAKS
                elif type_str.find("MaxBlock") != -1:
                    params = type_str.split('(')[1].split(')')[0].split(',')
                    m = int(params[0])
                    s = int(params[1])
                    list_of_params.append(m)
                    list_of_params.append(s)
                    type_const = Const.MAX_BLOCK
                if penalty_str:
                    penalty = int(penalty_str)

                distribution_constraint = DistributionConstraint(
                    id_dist, type_const, required, penalty, list_of_params)

                number_of_classes = 0
                for c in dist_iter.findall('class'):
                    number_of_classes += 1
                    str_id_class = c.get('id')
                    int_id_class = problem.class_dict_str_id_to_int_id.get(str_id_class)
                    distribution_constraint.classes.append(int_id_class)

                if type_const == Const.SAME_ROOM:
                    for id_c in distribution_constraint.classes:
                        lista = problem.same_room_constraints.get(id_c)
                        if not lista:
                            problem.same_room_constraints[id_c] = [distribution_constraint, ]
                        else:
                            lista.append(distribution_constraint)

                max_penalties_distribution = number_of_classes * (number_of_classes - 1) / 2
                max_penalties_distribution = max_penalties_distribution * penalty
                sum_max_penalties += max_penalties_distribution * problem.weight_distribution
                problem.add_constraint(distribution_constraint)

            for s in self.xml_problem.find('students').findall('student'):
                id_student = problem.generate_int_id_student(s.get('id'))
                student = Student(id_student)
                sum_max_classes = 0
                for c in s.findall('course'):
                    id_course = c.get('id')
                    student.add_course(problem.course_dict_str_id_to_int_id.get(id_course))
                    sum_max_classes += problem.courses.get(
                        problem.course_dict_str_id_to_int_id.get(
                            id_course)).max_class_combination
                max_penalties_student = sum_max_classes * (sum_max_classes - 1) / 2
                sum_max_penalties += max_penalties_student * problem.weight_student
                problem.add_student(student)

            problem.max_penalties = sum_max_penalties
        return problem

    ''' ************************************************************
            Métodos de manipulação da tag problem:
    ************************************************************ '''

    def get_name_problem(self):
        return self.xml_problem.get('name')

    def get_nr_days_problem(self):
        return self.xml_problem.get('nrDays')

    def get_nr_weeks_problem(self):
        return self.xml_problem.get('nrWeeks')

    def get_slots_per_day_problem(self):
        return self.xml_problem.get('slotsPerDay')

    ''' ************************************************************
            Métodos de manipulação da tag optimization:
    ************************************************************ '''

    def get_time_optimization(self):
        return self.optimization.get('time')

    def get_room_optimization(self):
        return self.optimization.get('room')

    def get_distribution_optimization(self):
        return self.optimization.get('distribution')

    def get_student_optimization(self):
        return self.optimization.get('student')

    ''' ************************************************************
            Funções de construção de arquivo XML:
    ************************************************************ '''

    @staticmethod
    def write_file_xml(name_file, solution):
        arq = open(name_file, 'w')
        arq.write(solution.string_to_xml())
        arq.close()

    @staticmethod
    def validate_file_xml(file_xml, file_dtd):
        xml = etree.parse(file_xml)
        FileXML.validate_object_xml(xml, file_dtd)

    @staticmethod
    def validate_string_xml(string_xml, file_dtd):
        xml = etree.fromstring(string_xml)
        FileXML.validate_object_xml(xml, file_dtd)

    @staticmethod
    def validate_object_xml(xml, file_dtd):
        dtd = etree.DTD(open(file_dtd))
        if dtd.validate(xml):
            return True
        return False
