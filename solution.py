# -*- coding: utf-8 -*-
from problem import Problem
from funcoes_constraints import Constraint
from copy import deepcopy
import random
from conflict_matrix import ConflictMatrixEsparse
from constants import Const
from typing import Dict, List, Tuple


class ClassSolution:
    def __init__(self, id_param: int, id_time: int = None, id_room: int = None) -> None:
        self.id = id_param
        self.id_time = id_time
        self.id_room = id_room
        self.students = []

    def __str__(self) -> str:
        str_return = 'Class id="%d"' % self.id
        str_return += ', id_time="%s"' % str(self.id_time)
        str_return += ', room="%s"' % self.id_room if self.id_room else ''
        str_return += ', Students="%s"' % str(self.students)
        return str_return

    def string_to_xml(self, problem: Problem):
        xml = '\t<class id="%s"' % problem.class_dict_int_id_to_str_id[self.id]
        # if self.id_time:
        #     tupla = problem.id_to_time[self.id_time]
        #     xml += ' days="%s"' % tupla[2]
        #     xml += ' start="%s"' % tupla[0]
        #     xml += ' weeks="%s"' % tupla[3]
        tupla = problem.id_to_time[self.id_time]
        xml += ' days="%s"' % tupla[2]
        xml += ' start="%s"' % tupla[0]
        xml += ' weeks="%s"' % tupla[3]
        xml += ' room="%s"' % problem.room_dict_int_id_to_str_id[self.id_room]\
            if self.id_room != 0 else ''
        if self.students:
            xml += '>'
            for student in self.students:
                # xml += '\n\t\t<student id="%d"/>' % student
                xml += '\n\t\t<student id="%s"/>' % problem.student_dict_int_id_to_str_id[student]
            xml += '\n\t</class>'
        else:
            xml += '/>'
        return xml


class ClassConflict:
    def __init__(self, dict_of_real_indexes=None,
                 indirect_sort_index=None):
        self.conflict_by_id = {}
        self.conflict_reverse = {}
        self.list_of_real_indexes = dict_of_real_indexes
        self.indirect_sort_index = indirect_sort_index

    def add_conflict_without_check(self, id1, id2):
        list_aux = self.conflict_by_id.get(id1)
        if list_aux:
            if id2 not in list_aux:
                list_aux.append(id2)
        else:
            self.conflict_by_id[id1] = [id2, ]

        list_aux = self.conflict_reverse.get(id2)
        if list_aux:
            if id1 not in list_aux:
                list_aux.append(id1)
        else:
            self.conflict_reverse[id2] = [id1, ]

    def add_conflict(self, id1, id2):
        if (self.list_of_real_indexes.get(id1) >
                self.list_of_real_indexes.get(id2)):
            aux = id1
            id1 = id2
            id2 = aux

        list_aux = self.conflict_by_id.get(id2)
        if list_aux:
            if id1 not in list_aux:
                list_aux.append(id1)
        else:
            self.conflict_by_id[id2] = [id1, ]

        list_aux = self.conflict_reverse.get(id1)
        if list_aux:
            if id2 not in list_aux:
                list_aux.append(id2)
        else:
            self.conflict_reverse[id1] = [id2, ]

    def remove_redundant_conflicts(self):
        for id_iter in self.indirect_sort_index:
            if self.conflict_by_id.get(id_iter):
                print("REMOVING KEY: %d" % id_iter)
                self.remove_id(id_iter)

    def remove_id(self, id_param):
        list_of_ids = self.conflict_reverse.get(id_param)
        if list_of_ids:
            for id_iter in list_of_ids:
                list_of_ids2 = self.conflict_by_id.get(id_iter)
                list_of_ids2.remove(id_param)
                if len(list_of_ids2) == 0:
                    del self.conflict_by_id[id_iter]
            del self.conflict_reverse[id_param]


class Solution:
    def __init__(self, problem=None, runtime=None, cores=None, technique=None,
                 author=None, institution=None, country=None):
        self.problem = problem
        self.runtime = runtime
        self.cores = cores
        self.technique = technique
        self.author = author
        self.institution = institution
        self.country = country
        self.classes_solution = {}
        self.classes_per_students = {}

        self.indirect_sort_index = []
        self.real_index_of_classes = {}
        for i in range(len(problem.classes)):
            # self.indirect_sort_index.append((len(problem.classes) - i))
            self.indirect_sort_index.append(i + 1)

        random.shuffle(self.indirect_sort_index)
        # for i in range(len(problem.classes)):
        for i, id_class in enumerate(self.indirect_sort_index):
            self.real_index_of_classes[id_class] = i + 1

        self.classes_not_assigned = []
        self.classes_not_assigned_with_times_rooms_conflict = []

        self.classes_conflict = ClassConflict(self.real_index_of_classes, self.indirect_sort_index)

        # Dict de room (key) e lista de times (values) alocados nela
        # self.times_in_rooms = {}

        # Dict de room (key) e lista de classes (values) alocadas nela
        # self.classes_in_rooms = {}

        # Dict de room (key) e lista de classes solution (values) alocadas nela
        self.classes_solution_in_rooms = {}

        # Dict de class (turma) e as vagas disponíveis (values)
        self.vacancies_of_classes = {}

        self.conflicts_in_rooms = []
        self.conflicts_in_hard_constraints = []

    def clear_allocation_of_classes(self) -> None:
        self.classes_not_assigned = []
        self.classes_not_assigned_with_times_rooms_conflict = []

        self.classes_conflict = ClassConflict(self.real_index_of_classes, self.indirect_sort_index)

        # Dict de room (key) e lista de classes solution (values) alocadas nela
        self.classes_solution_in_rooms = {}
        for id_class in self.problem.fixed_classes:
            id_room = list(self.problem.classes[id_class].rooms.keys())[0]
            if id_room:
                if id_room in self.classes_solution_in_rooms.keys():
                    self.classes_solution_in_rooms[id_room].append(id_class)
                else:
                    self.classes_solution_in_rooms[id_room] = [id_class, ]

        self.conflicts_in_rooms = []
        self.conflicts_in_hard_constraints = []

    def update_class(self, obj_class_solution):
        self.classes_solution[obj_class_solution.id] = obj_class_solution

    def add_class_to_list_of_classes_not_assigned(self, id_class_conflicting1,
                                                  id_class_conflicting2,
                                                  list_of_classes_not_assigned):
        if (self.real_index_of_classes.get(id_class_conflicting1) >
                self.real_index_of_classes.get(id_class_conflicting2)):
            id_class_conflicting2 = id_class_conflicting1
        if id_class_conflicting2 not in list_of_classes_not_assigned:
            list_of_classes_not_assigned.append(id_class_conflicting2)

    def add_class_not_assigned(self, id_class_conflicting1,
                               id_class_conflicting2):
        self.add_class_to_list_of_classes_not_assigned(id_class_conflicting1,
                                                       id_class_conflicting2,
                                                       self.classes_not_assigned)

    def add_classes_not_assigned_with_times_rooms_conflict(self, id_class_conflicting1,
                                                           id_class_conflicting2):
        self.add_class_to_list_of_classes_not_assigned(id_class_conflicting1,
                                                       id_class_conflicting2,
                                                       self.classes_not_assigned_with_times_rooms_conflict)

    def __str__(self):
        str_return = 'Solution:'
        str_return += '\n\tname="%s"' % self.problem.name
        for c in self.classes_solution.values():
            str_return += '\n\t' + str(c)
        return str_return

    def is_time_available(self, id_time, id_room):
        if self.classes_solution_in_rooms.get(id_room):
            for id_class_solution in self.classes_solution_in_rooms.get(id_room):
                id_time_class_solution = self.get_id_time(id_class_solution)
                if self.problem.is_overlap(id_time, id_time_class_solution):
                    return False
        return True

    def conflicting_classes_in_room(self, id_time, id_room):
        list_of_ids_conflicting = []

        classes_solution_allocated_in_room = self.classes_solution_in_rooms.get(id_room)
        if classes_solution_allocated_in_room:
            for id_class_solution in classes_solution_allocated_in_room:
                id_time_class_solution = self.get_id_time(id_class_solution)
                if self.problem.conflict_ids_matrix.has_conflict(id_time, id_time_class_solution):
                    list_of_ids_conflicting.append(id_class_solution)
        return list_of_ids_conflicting

    def random_new_time_for_a_class(self, id_class):
        class_solution = self.classes_solution[id_class]
        id_room = class_solution.id_room
        id_time = class_solution.id_time
        list_of_times = list(self.problem.classes[id_class].times.keys())
        nr_times = len(list_of_times)
        i = 0

        while i < nr_times:
            pos = random.randint(0, (nr_times - 1))
            new_id_time = list_of_times[pos]
            if id_time != new_id_time:
                if not id_room or not self.problem.rooms[id_room].is_time_unavailable(
                        new_id_time, self.problem.conflict_ids_matrix):
                    return new_id_time
            i += 1
        return id_time

    def random_new_room_for_a_class2(self, id_class):
        class_solution = self.classes_solution[id_class]
        id_room = class_solution.id_room
        id_time = class_solution.id_time
        list_of_rooms = list(self.problem.classes[id_class].rooms.keys())
        nr_rooms = len(list_of_rooms)
        i = 0

        while i < nr_rooms:
            pos = random.randint(0, (nr_rooms - 1))
            new_id_room = list_of_rooms[pos]
            if id_room != new_id_room:
                if self.problem.rooms[new_id_room].is_time_unavailable(
                        id_time, self.problem.conflict_ids_matrix):
                    self.classes_solution[id_class].id_room = new_id_room
                    new_id_time = self.random_new_time_for_a_class(id_class)
                    self.classes_solution[id_class].id_room = id_room
                    return new_id_room, new_id_time
                else:
                    return new_id_room, id_time
            i += 1
        return id_room, id_time

    def random_new_room_for_a_class(self, id_class):
        class_solution = self.classes_solution[id_class]
        id_room = class_solution.id_room
        id_time = class_solution.id_time
        list_of_rooms = list(self.problem.classes[id_class].rooms.keys())
        nr_rooms = len(list_of_rooms)
        i = 0

        while i < nr_rooms:
            pos = random.randint(0, (nr_rooms - 1))
            new_id_room = list_of_rooms[pos]
            if id_room != new_id_room:
                if not self.problem.rooms[new_id_room].is_time_unavailable(
                        id_time, self.problem.conflict_ids_matrix):
                    return new_id_room, id_time
            i += 1
        return id_room, id_time

    def rand_time_and_change(self, id_class):
        new_id_time = self.random_new_time_for_a_class(id_class)
        self.classes_solution[id_class].id_time = new_id_time

    def rand_room_and_change(self, id_class):
        new_id_room = 0
        new_id_time = 0
        class_solution = None
        choose_another_room = True

        while choose_another_room:
            choose_another_room = False
            new_id_room, new_id_time = self.random_new_room_for_a_class(id_class)
            class_solution = self.classes_solution[id_class]

            lista = self.problem.same_room_constraints.get(id_class)
            if lista:
                for dist in lista:
                    for id_class_dist in dist.classes:
                        if new_id_room not in self.problem.classes[id_class_dist].rooms.keys():
                            choose_another_room = True
                            break
                        if (id_class_dist != id_class and
                                not self.problem.select_id_time_compatible_with_room(
                                    id_class_dist, new_id_room)):
                            choose_another_room = True
                            break
                    if choose_another_room:
                        break

                if not choose_another_room:
                    for dist in lista:
                        # print("DIST_SAME ROOM CLASSES: " + str(dist.classes))
                        for id_class_dist in dist.classes:
                            if id_class_dist != id_class:
                                new_id_time_class_dist = \
                                    self.problem.select_id_time_compatible_with_room(
                                        id_class_dist, new_id_room)
                                class_solution_dist = \
                                    self.classes_solution[id_class_dist]
                                self.change_room(class_solution_dist,
                                                 new_id_room,
                                                 new_id_time_class_dist)
                    #             print("CLASS C%d: ID_ROOM = %d" %
                    #                   (id_class_dist,
                    #                    self.classes_solution[id_class_dist].id_room))
                    #         else:
                    #             print("CLASS C%d: ID_ROOM = %d" %
                    #                   (id_class_dist,
                    #                    new_id_room))
                    #
                    # input("PRESSIONE ENTER...")

        self.change_room(class_solution, new_id_room, new_id_time)

    def change_room(self, class_solution, new_id_room, new_id_time):
        id_class = class_solution.id
        self.classes_solution_in_rooms[class_solution.id_room].remove(id_class)
        if new_id_room in self.classes_solution_in_rooms.keys():
            self.classes_solution_in_rooms[new_id_room].append(id_class)
        else:
            self.classes_solution_in_rooms[new_id_room] = [id_class, ]
        class_solution.id_time = new_id_time
        class_solution.id_room = new_id_room

    def realocate_classes(self):

        for id_class in self.conflicts_in_rooms:
            obj_class = self.problem.classes[id_class]
            list_of_remanescent_rooms = deepcopy(list(obj_class.rooms.keys()))
            sair = False
            id_time = 0
            id_room = 0
            while list_of_remanescent_rooms and not sair:
                id_room = list_of_remanescent_rooms[0]
                for id_time_iter in list(obj_class.times.keys()):
                    if self.problem.rooms[id_room].is_time_unavailable(
                            id_time_iter, self.problem.conflict_ids_matrix):
                        continue
                    if self.is_time_available(id_time_iter, id_room):
                        id_time = id_time_iter
                        sair = True
                        break

                list_of_remanescent_rooms.remove(id_room)
            if sair:
                class_solution = self.classes_solution[id_class]
                self.change_room(class_solution, id_room, id_time)
        self.calculate_conflicts_in_rooms()
        self.calculate_hard_constraints_penalties()

    def rearrange_classes_conflicting_in_hard_constraints(self, limit_iter: int):
        count = 0
        while len(self.conflicts_in_hard_constraints) > 0 and count < limit_iter:

            nr_conflicts_in_hard_constraints = len(self.conflicts_in_hard_constraints)
            pos = random.randint(0, (nr_conflicts_in_hard_constraints - 1))
            id_class = self.conflicts_in_hard_constraints[pos]

            tipo_troca = random.randint(1, 2)
            old_id_room = self.classes_solution[id_class].id_room
            if not old_id_room:
                    tipo_troca = 1

            class_picked = self.problem.classes[id_class]
            nr_times_class = len(class_picked.times)
            nr_rooms_class = len(class_picked.rooms)
            if tipo_troca == 1 and nr_times_class == 1:
                if nr_rooms_class == 1:
                    continue
                tipo_troca = 2
            elif tipo_troca == 2 and nr_rooms_class == 1:
                if nr_times_class == 1:
                    continue
                tipo_troca = 1
            if tipo_troca == 1:
                self.rand_time_and_change(id_class)
            else:
                self.rand_room_and_change(id_class)

            self.calculate_hard_constraints_penalties()
            # print("VETOR CONFLICT HARD CONSTRAINTS: " + str(self.conflicts_in_hard_constraints))
            # input("PRESSIONE ENTER...")
            count += 1

    def __has_vacancy(self, list_of_id_classes: List[int]) -> bool:
        """ Verifica se há vaga em todas as turmas de uma lista de turmas.

        Verifica se há pelo menos uma vaga para cada uma das turmas de uma
        lista de turmas.
        :param List[int] list_of_id_classes: lista com os id's das turmas a
        serem verificadas se há vagas.
        :return: Valor booleano. True se há vagas e False, no caso de qualquer
        uma das turmas da lista não ter vaga.
        :rtype: bool
        """
        # Itera sobre cada uma das turmas do parâmetro list_of_id_classes para
        # verificar se há vagas.
        for id_class in list_of_id_classes:
            if self.vacancies_of_classes[id_class] <= 0:
                return False  # Retorna False se ao menos uma turma da lista não possui vaga.
        return True

    def pick_course_combination_with_vacancy(self, id_course: int) -> List[int]:
        """ Escolhe uma combinação de turmas de um curso em que haja vagas.

        Escolhe e retorna uma combinação de turmas de um curso, cujo id é
        passado como parâmetro, em que haja vagas. Caso não haja, retorna a
        última combinação de turmas da lista de cobinações do curso.
        :param int id_course: id do curso para o qual se deseja selecionar uma
        combinação de turmas com vagas.
        :return: Lista com os id's das turmas que compõem a combinação
        escolhida.
        :rtype: List[int]
        """
        # Itera sobre as diversas combinações de turmas que compõem um curso.
        for combination_of_classes in \
                self.problem.classes_combinations_per_course[id_course]:
            if self.__has_vacancy(combination_of_classes):
                # Retorna a primeira cobinação de turmas em que encontrar
                # vagas.
                return combination_of_classes
        # Em caso de não haver vagas, retorna a última combinação de turmas
        # da lista de combinações do curso.
        return self.problem.classes_combinations_per_course[id_course][-1]

    def allocate_all_students(self) -> Tuple[Dict[int, Dict[int, List[int]]],
                                             Dict[int, List[int]]]:
        """ Aloca todos os estudantes do problema em turmas.

        Aloca todos os estudantes do problema em uma combinação de turmas
        de cada um dos cursos de suas listas de cursos.
        :return: Dois dicionários, um com a disposição de turmas (values, em
        forma de dicionário) por estudante (keys) e o outro com a disposição de
        estudantes (values, em forma de lista) por turma (keys).
        :rtype: Tuple[Dict[int, Dict[int, List[int]]], Dict[int, List[int]]]
        """
        # Dicionário de turmas por estudante:
        classes_per_student = {}
        # Dicionário de estudantes por turma:
        students_per_class = {}

        # Inicializando a lista vacancies_of_classes (vagas das turmas)
        # com a capacidade (limit) da turma, já que não há nenhum estudante
        # matriculado.
        for c in self.problem.classes.values():
            self.vacancies_of_classes[c.id] = c.limit

        # Itera sobre todos os estudantes do problema para matriculá-los
        # em seus cursos.
        for student in self.problem.students.values():
            # Inicializa a posição do estudante com um dicionário vazio,
            # para começar a matrícula dele.
            classes_per_student[student.id] = {}

            # Itera sobre cada um dos cursos em que o estudante deve ser
            # matriculado.
            for id_course in student.courses:
                # Seleciona uma combinação de turmas para o curso em que haja
                # vagas.
                list_of_classes =\
                    self.pick_course_combination_with_vacancy(id_course)

                # Armazena no dicionário classes_per_student, nas chaves com o
                # id do estudante e com o id do curso, a lista de turmas em que
                # ele foi matriculado.
                classes_per_student[student.id][id_course] = list_of_classes

                # Itera sobre os id's de cada turma em que o estudante foi
                # matriculado.
                for id_class in list_of_classes:
                    # Decrementa uma unidade do número de vagas que a turma
                    # possui.
                    self.vacancies_of_classes[id_class] -= 1

                    # Adiciona no dicionário students_per_class, na chave com o
                    # id da turma, o id do estudante.
                    if students_per_class.get(id_class):
                        students_per_class[id_class].append(student.id)
                    else:
                        students_per_class[id_class] = [student.id, ]
        return classes_per_student, students_per_class

    def allocate_fixed_classes(self) -> None:
        for id_class in self.problem.fixed_classes:
            id_room = list(self.problem.classes[id_class].rooms.keys())[0]
            id_time = list(self.problem.classes[id_class].times.keys())[0]
            self.classes_solution[id_class] = ClassSolution(id_class, id_time, id_room)
            if id_room:
                if id_room in self.classes_solution_in_rooms.keys():
                    self.classes_solution_in_rooms[id_room].append(id_class)
                else:
                    self.classes_solution_in_rooms[id_room] = [id_class, ]

    def calculate_conflicts_in_rooms(self):
        self.conflicts_in_rooms = []
        for id_room in list(self.problem.rooms.keys())[1:]:
            if self.classes_solution_in_rooms.get(id_room):
                for iter_class_sol1, id_class_sol1 in enumerate(self.classes_solution_in_rooms.get(id_room)):
                    for id_class_sol2 in list(self.classes_solution_in_rooms.get(id_room))[(iter_class_sol1 + 1):]:
                        id_time_class1 = self.get_id_time(id_class_sol1)
                        id_time_class2 = self.get_id_time(id_class_sol2)
                        if self.problem.matrix_not_overlap.has_conflict(id_time_class1, id_time_class2):
                            if id_class_sol1 not in self.conflicts_in_rooms:
                                self.conflicts_in_rooms.append(id_class_sol1)
                            if id_class_sol2 not in self.conflicts_in_rooms:
                                self.conflicts_in_rooms.append(id_class_sol2)

    def calculate_objective_function(self):
        z = 0
        time_penalties = 0
        room_penalties = 0

        self.calculate_conflicts_in_rooms()

        # print("TURMAS COM CONFLITO DE OVERLAP NAS SALAS: %d" % len(self.conflicts))

        # print("PENALIDADES HARD CONSTRAINTS VIOLADAS:")
        # aux = self.calculate_hard_constraints_penalties()
        # print("TOTAL DE PENALIDADES HARD CONSTRAINTS VIOLADAS: %d" % aux)

        for c in self.classes_solution.values():
            time_penalties += self.problem.classes[c.id].times[c.id_time].penalty
            if c.id_room:
                room_penalties += self.problem.classes[c.id].rooms[c.id_room]

        z += time_penalties * self.problem.weight_time
        # print("PENALIDADES TIMES: %d" % time_penalties)
        z += room_penalties * self.problem.weight_room
        # print("PENALIDADES ROOMS: %d" % room_penalties)

        aux = self.calculate_soft_constraints_penalties()
        # print("PENALIDADES SOFT CONSTRAINTS: %d" % aux)
        z += aux * self.problem.weight_distribution
        aux = self.calculate_students_penalties()
        # print("PENALIDADES STUDENTS: %d" % aux)
        z += aux * self.problem.weight_student

        return z

    def compute_hard_constraint_time(self, list_of_class_ids: List[int],
                                     matrix: ConflictMatrixEsparse) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if matrix.has_conflict(id_time_class1, id_time_class2):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_constraint_time(self, list_of_class_ids: List[int],
                                     matrix: ConflictMatrixEsparse) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if matrix.has_conflict(id_time_class1, id_time_class2):
                    nr_class += 1
        return nr_class

    def compute_soft_same_room(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                c1_room = self.get_id_room(c1)
                c2_room = self.get_id_room(c2)
                if not Constraint.same_room(c1_room, c2_room):
                    nr_class += 1
        return nr_class

    def compute_hard_same_room(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                c1_room = self.get_id_room(c1)
                c2_room = self.get_id_room(c2)
                if not Constraint.same_room(c1_room, c2_room):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_different_room(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                c1_room = self.get_id_room(c1)
                c2_room = self.get_id_room(c2)
                if not Constraint.different_room(c1_room, c2_room):
                    nr_class += 1
        return nr_class

    def compute_hard_different_room(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                c1_room = self.get_id_room(c1)
                c2_room = self.get_id_room(c2)
                if not Constraint.different_room(c1_room, c2_room):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_same_attendees(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                id_room_class1 = self.get_id_room(c1)
                id_room_class2 = self.get_id_room(c2)
                if self.problem.matrix_same_attendees.has_conflict(
                        (id_time_class1, id_room_class1),
                        (id_time_class2, id_room_class2)):
                    nr_class += 1
        return nr_class

    def compute_student_same_attendees(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                tupla = self.problem.id_to_time[self.get_id_time(c1)]
                c1_start = int(tupla[0])
                c1_length = int(tupla[1])
                c1_end = c1_start + c1_length
                c1_days = int(tupla[2], 2)
                c1_weeks = int(tupla[3], 2)
                id_room_class1 = self.get_id_room(c1)
                tupla = self.problem.id_to_time[self.get_id_time(c2)]
                c2_start = int(tupla[0])
                c2_length = int(tupla[1])
                c2_end = c2_start + c2_length
                c2_days = int(tupla[2], 2)
                c2_weeks = int(tupla[3], 2)
                id_room_class2 = self.get_id_room(c2)
                travel_room = None
                if id_room_class1:
                    travel_room = self.problem.times_travel_rooms.get((id_room_class1, id_room_class2))
                room_travel_value = travel_room if travel_room else 0
                if not Constraint.same_attendees(c1_start, c1_end, c2_start, c2_end,
                                                 c1_days, c2_days, c1_weeks, c2_weeks, room_travel_value):
                    nr_class += 1
        return nr_class

    def compute_hard_same_attendees(self, list_of_class_ids: List[int]) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                id_room_class1 = self.get_id_room(c1)
                id_room_class2 = self.get_id_room(c2)
                if self.problem.matrix_same_attendees.has_conflict(
                        (id_time_class1, id_room_class1),
                        (id_time_class2, id_room_class2)):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_work_day(self, list_of_class_ids: List[int], s: int) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if self.problem.matrix_work_day.has_conflict((id_time_class1, s), id_time_class2):
                    nr_class += 1
        return nr_class

    def compute_hard_work_day(self, list_of_class_ids: List[int], s: int) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if self.problem.matrix_work_day.has_conflict((id_time_class1, s), id_time_class2):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_min_gap(self, list_of_class_ids: List[int], g: int) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if self.problem.matrix_min_gap.has_conflict((id_time_class1, g), id_time_class2):
                    nr_class += 1
        return nr_class

    def compute_hard_min_gap(self, list_of_class_ids: List[int], g: int) -> int:
        nr_class = 0
        for i, c1 in enumerate(list_of_class_ids):
            for c2 in list_of_class_ids[(i + 1):]:
                id_time_class1 = self.get_id_time(c1)
                id_time_class2 = self.get_id_time(c2)
                if self.problem.matrix_min_gap.has_conflict((id_time_class1, g), id_time_class2):
                    if c1 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c1)
                    if c2 not in self.conflicts_in_hard_constraints:
                        self.conflicts_in_hard_constraints.append(c2)
                    nr_class += 1
        return nr_class

    def compute_soft_max_days(self, list_of_class_ids, d):
        list_of_class_days = []
        for c in list_of_class_ids:
            tupla = self.problem.id_to_time[self.classes_solution[c].id_time]
            c_days = int(tupla[2], 2)
            list_of_class_days.append(c_days)
        number_of_non_zero_bits = Constraint.max_days_soft(list_of_class_days, self.problem)
        return max(number_of_non_zero_bits - d, 0)

    def compute_hard_max_days(self, list_of_class_ids, d):
        list_of_class_days = []
        for c in list_of_class_ids:
            tupla = self.problem.id_to_time[self.classes_solution[c].id_time]
            c_days = int(tupla[2], 2)
            list_of_class_days.append(c_days)
        number_of_days_exceeded = self.compute_soft_max_days(list_of_class_ids, d)
        if number_of_days_exceeded > 0:
            for c in list_of_class_ids:
                if c not in self.classes_not_assigned:
                    self.classes_not_assigned.append(c)
        return number_of_days_exceeded

    def compute_soft_max_day_load(self, list_of_class_ids, s):
        return Constraint.max_day_load_soft(list_of_class_ids,
                                            s, self.problem, self)

    def compute_hard_max_day_load(self, list_of_class_ids, s):
        aux_list_of_class_ids = []
        for c in list_of_class_ids:
            aux_list_of_class_ids.append(c)
        number_of_slots_exceeded = Constraint.max_day_load_soft(aux_list_of_class_ids,
                                                                s, self.problem, self)
        if number_of_slots_exceeded > 0:
            for c in aux_list_of_class_ids:
                self.classes_not_assigned.append(c)
        return number_of_slots_exceeded

    def compute_soft_max_breaks(self, list_of_class_ids, r, s):
        aux_list_of_class_ids = []
        for c in list_of_class_ids:
            aux_list_of_class_ids.append(c)
        return Constraint.max_breaks_soft(aux_list_of_class_ids,
                                          r, s, self.problem, self)

    def compute_hard_max_breaks(self, list_of_class_ids, r, s):
        aux_list_of_class_ids = []
        for c in list_of_class_ids:
            aux_list_of_class_ids.append(c)
        number_of_breaks_exceeded = Constraint.max_breaks_soft(aux_list_of_class_ids,
                                                               r, s, self.problem, self)
        if number_of_breaks_exceeded > 0:
            for c in aux_list_of_class_ids:
                self.classes_not_assigned.append(c)
        return number_of_breaks_exceeded

    def calculate_hard_constraints_penalties(self) -> int:
        self.conflicts_in_hard_constraints = []
        sum_penalties = 0
        for dist_hard in self.problem.distributions_hard:
            type = dist_hard.type
            if type == Const.SAME_START:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_same_start)
            elif type == Const.SAME_TIME:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_same_time)
            elif type == Const.DIFFERENT_TIME:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_different_time)
            elif type == Const.SAME_DAYS:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_same_days)
            elif type == Const.DIFFERENT_DAYS:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_different_days)
            elif type == Const.SAME_WEEKS:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_same_weeks)
            elif type == Const.DIFFERENT_WEEKS:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_different_weeks)
            elif type == Const.OVERLAP:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_overlap)
            elif type == Const.NOT_OVERLAP:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_not_overlap)
            elif type == Const.SAME_ROOM:
                sum_penalties += self.compute_hard_same_room(dist_hard.classes)
            elif type == Const.DIFFERENT_ROOM:
                sum_penalties += self.compute_hard_different_room(dist_hard.classes)
            elif type == Const.SAME_ATTENDEES:
                sum_penalties += self.compute_hard_same_attendees(dist_hard.classes)
            elif type == Const.PRECEDENCE:
                sum_penalties += self.compute_hard_constraint_time(
                    dist_hard.classes, self.problem.matrix_precedence)
            elif type == Const.WORK_DAY:
                s = dist_hard.list_of_params[0]
                sum_penalties += self.compute_hard_work_day(dist_hard.classes, s)
            elif type == Const.MIN_GAP:
                g = dist_hard.list_of_params[0]
                sum_penalties += self.compute_hard_min_gap(dist_hard.classes, g)
            elif type == Const.MAX_DAYS:  # type.find("MaxDays") != -1:
                d = int(type.split('(')[1].split(')')[0])
                sum_penalties += self.compute_hard_max_days(dist_hard.classes, d)
            elif type == Const.MAX_DAY_LOAD:  # type.find("MaxDayLoad") != -1:
                s = int(type.split('(')[1].split(')')[0])
                sum_penalties += self.compute_hard_max_day_load(dist_hard.classes, s)
            elif type == Const.MAX_BREAKS:  # type.find("MaxBreaks") != -1:
                params = type.split('(')[1].split(')')[0].split(',')
                r = int(params[0])
                s = int(params[1])
                sum_penalties += self.compute_hard_max_breaks(dist_hard.classes, r, s)
            elif type == Const.MAX_BLOCK:  # type.find("MaxBlock") != -1:
                params = type.split('(')[1].split(')')[0].split(',')
                m = int(params[0])
                s = int(params[1])

        return sum_penalties

    def calculate_soft_constraints_penalties(self) -> int:
        sum_penalties = 0
        for dist_soft in self.problem.distributions_soft:
            type = dist_soft.type
            penalty = dist_soft.penalty
            if type == Const.SAME_START:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_same_start) * penalty
            elif type == Const.SAME_TIME:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_same_time) * penalty
            elif type == Const.DIFFERENT_TIME:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_different_time) * penalty
            elif type == Const.SAME_DAYS:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_same_days) * penalty
            elif type == Const.DIFFERENT_DAYS:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_different_days) * penalty
            elif type == Const.SAME_WEEKS:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_same_weeks) * penalty
            elif type == Const.DIFFERENT_WEEKS:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_different_weeks) * penalty
            elif type == Const.OVERLAP:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_overlap) * penalty
            elif type == Const.NOT_OVERLAP:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_not_overlap) * penalty
            elif type == Const.SAME_ROOM:
                sum_penalties += self.compute_soft_same_room(dist_soft.classes) * penalty
            elif type == Const.DIFFERENT_ROOM:
                sum_penalties += self.compute_soft_different_room(dist_soft.classes) * penalty
            elif type == Const.SAME_ATTENDEES:
                sum_penalties += self.compute_soft_same_attendees(dist_soft.classes) * penalty
                pass
            elif type == Const.PRECEDENCE:
                sum_penalties += self.compute_soft_constraint_time(
                    dist_soft.classes, self.problem.matrix_precedence) * penalty
            elif type == Const.WORK_DAY:
                s = dist_soft.list_of_params[0]
                sum_penalties += self.compute_soft_work_day(dist_soft.classes, s) * penalty
            elif type == Const.MIN_GAP:
                g = dist_soft.list_of_params[0]
                sum_penalties += self.compute_soft_min_gap(dist_soft.classes, g) * penalty
            elif type == Const.MAX_DAYS:  # type.find("MaxDays") != -1:
                d = int(type.split('(')[1].split(')')[0])
                sum_penalties += self.compute_soft_max_days(dist_soft.classes, d) * penalty
            elif type == Const.MAX_DAY_LOAD:  # type.find("MaxDayLoad") != -1:
                s = int(type.split('(')[1].split(')')[0])
                sum_penalties += (self.compute_soft_max_day_load(dist_soft.classes, s)
                                  * penalty) // self.problem.nr_weeks
            elif type == Const.MAX_BREAKS:  # type.find("MaxBreaks") != -1:
                params = type.split('(')[1].split(')')[0].split(',')
                r = int(params[0])
                s = int(params[1])
                sum_penalties += (self.compute_soft_max_breaks(dist_soft.classes, r, s)
                                  * penalty) // self.problem.nr_weeks
            elif type == Const.MAX_BLOCK:  # type.find("MaxBlock") != -1:
                params = type.split('(')[1].split(')')[0].split(',')
                m = int(params[0])
                s = int(params[1])

        return sum_penalties

    def get_id_time(self, id_class: int) -> int:
        if self.classes_solution.get(id_class):
            return self.classes_solution[id_class].id_time
        else:
            return 0

    def get_id_room(self, id_class: int) -> int:
        if self.classes_solution.get(id_class):
            return self.classes_solution[id_class].id_room
        else:
            return 0

    def calculate_students_penalties(self):
        sum_penalties = 0
        for id_student, classes_of_student in self.classes_per_students.items():
            sum_penalties += self.compute_student_same_attendees(classes_of_student)
        return sum_penalties

    def string_to_xml(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>'
        xml += '\n<!DOCTYPE solution PUBLIC'
        xml += '\n\t"-//ITC 2019//DTD Problem Format/EN"'
        xml += '\n\t"http://www.itc2019.org/competition-format.dtd">'
        xml += '\n<solution name="%s"' % self.problem.name
        xml += '\n\truntime="%s" cores="%s"' % (self.runtime, self.cores)
        xml += ' technique="%s"' % self.technique
        xml += '\n\tauthor="%s" institution="%s"' % (self.author,
                                                     self.institution)
        xml += ' country="%s">' % self.country
        for class_solution in self.classes_solution.values():
            xml += '\n' + class_solution.string_to_xml(self.problem)
        xml += '\n</solution>\n'
        return xml
