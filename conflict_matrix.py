# -*- coding: utf-8 -*-


class ConflictMatrixEsparse:
    def __init__(self):
        self.conflict = dict()

    def add_conflict(self, id1, id2):
        if id1 not in self.conflict:
            self.conflict[id1] = set()
        if id2 not in self.conflict:
            self.conflict[id2] = set()
        self.conflict[id1].add(id2)
        self.conflict[id2].add(id1)

    def add_conflict_one_way(self, id1, id2):
        if id1 not in self.conflict:
            self.conflict[id1] = set()
        self.conflict[id1].add(id2)

    def has_conflict(self, id1, id2):
        if id1 not in self.conflict:
            return False
        return id2 in self.conflict[id1]

    def get_conflict_binary_value(self, id1, id2):
        return 1 if self.has_conflict(id1, id2) else 0

    def __str__(self):
        return str(self.conflict)


class ConflictMatrixNotEsparse:
    def __init__(self):
        self.conflict = {}

    def add_conflict(self, id1, id2):
        self.add_conflict_value(id1, id2, 1)

    def add_conflict_value(self, id1, id2, value):
        self.conflict[(id1, id2)] = value
        self.conflict[(id2, id1)] = value

    def add_no_conflict(self, id1, id2):
        self.conflict[(id1, id2)] = 0
        self.conflict[(id2, id1)] = 0

    def has_conflict(self, id1, id2):
        return (id1, id2) in self.conflict

    def __str__(self):
        return str(self.conflict)
