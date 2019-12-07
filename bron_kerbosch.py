from typing import List, Tuple
# import sys
from copy import deepcopy
from networkx import Graph


def difference(list_of_items1: List[object],
               list_of_items2: List[object]) -> List[object]:
    return list(set(list_of_items1) - set(list_of_items2))


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


def bron_kerbosch_iterative(vertices, min_weight, graph, list_of_maximal_cliques):
    pilha = [([], vertices, []), ]
    # nr_vertices = len(vertices)
    while pilha:
        c, p, s = pilha.pop()
        if not union(p, s):
            if len(c) >= min_weight:
                list_of_maximal_cliques.append(c)
        if p:
            v = p[0]
            # print("\nAnalisando vertice nr. %d / %d" % (len(p), nr_vertices))
            neighbors_of_v = [n for n in graph.neighbors(v)]
            p_aux = deepcopy(p)
            p_aux.remove(v)
            s_aux = deepcopy(s)
            s_aux.append(v)
            pilha.append((deepcopy(c), p_aux, s_aux))
            pilha.append((union(c, [v, ]), intersection(p, neighbors_of_v),
                          intersection(s, neighbors_of_v)))


def bron_kerbosch_recursive(c, p, s, min_weight, graph, list_of_maximal_cliques):
    if not union(p, s):
        if len(c) >= min_weight:
            list_of_maximal_cliques.append(c)
    while p:
        v = p[0]
        neighbors_of_v = [n for n in graph.neighbors(v)]
        bron_kerbosch_recursive(
            union(c, [v, ]), intersection(p, neighbors_of_v),
            intersection(s, neighbors_of_v), min_weight, graph,
            list_of_maximal_cliques)
        p.remove(v)
        s.append(v)


def bron_kerbosch(c, p, s, min_weight, graph):
    if not union(p, s):
        if len(c) >= min_weight:
            return c
    while p:
        v = p[0]
        neighbors_of_v = [n for n in graph.neighbors(v)]
        result = bron_kerbosch(
            union(c, [v, ]), intersection(p, neighbors_of_v),
            intersection(s, neighbors_of_v), min_weight, graph)
        if result:
            return result
        p.remove(v)
        s.append(v)
    return None


def bron_kerbosch_separation_algorithm(c, p, s, min_weight_t, graph, list_of_maximal_cliques):
    if not union(p, s):
        if len(c) >= min_weight_t:
            list_of_maximal_cliques.append(c)
    if (len(c) + len(p)) >= min_weight_t:
        if len(p):
            u = p[0]
            neighbors_of_u = [n for n in graph.neighbors(u)]
            p_less_neighbors_of_u = difference(p, neighbors_of_u)
            for v in p_less_neighbors_of_u:
                neighbors_of_v = [n for n in graph.neighbors(v)]
                bron_kerbosch_separation_algorithm(
                    union(c, [v, ]), intersection(p, neighbors_of_v),
                    intersection(s, neighbors_of_v), min_weight_t, graph,
                    list_of_maximal_cliques)
                p.remove(v)
                s.append(v)


def enumerate_cliques_from_graph(graph_conflict_same_attendees: Graph) -> List[List[Tuple]]:
    vertices = list(graph_conflict_same_attendees.nodes)
    done = False
    list_of_cliques = []
    while not done:
        c = []
        p = vertices
        s = []
        clique = bron_kerbosch(c, p, s, 2, graph_conflict_same_attendees)
        if clique:
            remove_clique_edges(graph_conflict_same_attendees, clique)
            list_of_cliques.append(clique)
        else:
            done = True
    return list_of_cliques


def remove_clique_edges(graph, clique):
    for i, v1 in enumerate(clique):
        for v2 in clique[(i + 1):]:
            graph.remove_edge(v1, v2)


def modified_degree(graph, v):
    md = graph.degree(v)
    for n in graph.neighbors(v):
        md += graph.degree(n)
    return md


def swap(list1, pos1, pos2):
    aux = list1[pos1]
    list1[pos1] = list1[pos2]
    list1[pos2] = aux


def partition(list_v, list_md, low, high):
    pivot = list_md[high]
    i = low - 1
    for j in range(low, high):
        if list_md[j] >= pivot:
            i += 1
            swap(list_v, i, j)
            swap(list_md, i, j)
    swap(list_v, (i + 1), high)
    swap(list_md, (i + 1), high)
    return i + 1


def quicksort(list_v, list_md, low, high):
    if low < high:
        pos_pivot = partition(list_v, list_md, low, high)
        quicksort(list_v, list_md, low, (pos_pivot - 1))
        quicksort(list_v, list_md, (pos_pivot + 1), high)


def sort(list_v, list_md):
    high = len(list_v)
    # sys.setrecursionlimit(100000)
    if high == len(list_md):
        quicksort(list_v, list_md, 0, (high - 1))


def calculate_modified_degree(graph):
    return [modified_degree(graph, v) for v in list(graph.nodes)]
