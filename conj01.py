# coding: utf-8
import sys

sys.path.append('../simple_sat_master/src/')

from simple_sat_master.src import sat

from solvers import iterative_sat as solver
from time import time

def sudoku_cnf_from_starting_grid(grid):
    conj = []
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                conj.append({('x' + str(i + 1) + str(j + 1) + str(grid[i][j]), True)})
    return conj


def test_grid():
    grid = [[0, 0, 0, 0, 5, 4, 0, 0, 8]
        , [0, 6, 0, 0, 0, 0, 0, 1, 7]
        , [0, 0, 0, 9, 0, 0, 0, 0, 0]
        , [6, 0, 5, 0, 0, 7, 0, 0, 0]
        , [0, 0, 0, 0, 0, 0, 1, 0, 0]
        , [0, 0, 0, 0, 9, 0, 0, 7, 3]
        , [4, 0, 0, 0, 0, 9, 0, 0, 0]
        , [0, 8, 0, 3, 0, 0, 0, 2, 0]
        , [7, 1, 0, 0, 8, 0, 0, 3, 5]
            ]
    return grid


def test_sudoku_cnf_from_starting_grid():
    print(sudoku_cnf_from_starting_grid(grid))


# test_sudoku_cnf_from_starting_grid()


def sudoku_cnf_from_general_rules():
    """
    """
    conj = []
    r = range(1, 10)
    for i in r:
        for j in r:
            disj = set()
            # x111 v x112 v ... v x119
            for k in r:
                literal = ('x' + str(i) + str(j) + str(k), True)
                disj.add(literal)
            conj.append(disj)

            # -x111 v -x112 usw
            for k in r:
                for l in r:
                    if k < l:
                        disj = set()
                        literal = ('x' + str(i) + str(j) + str(k), False)
                        disj.add(literal)
                        literal = ('x' + str(i) + str(j) + str(l), False)
                        disj.add(literal)
                        conj.append(disj)

    # jede Zahl kommt pro Zeile vor:
    # x111 v x121 v x131 ... v x191
    for i in r:  # Zeile i
        for k in r:  # Wert k
            disj = set()
            for j in r:
                literal = ('x' + str(i) + str(j) + str(k), True)
                disj.add(literal)
            conj.append(disj)

    # jede Zahl kommt pro Zeile höchstens einmal vor:
    # -x111 v -x121, -x111 v -x131, -x121 v -x131, usw. ... , -x181 v -x191
    for i in r:  # Zeile i
        for k in r:  # Wert k
            for j1 in r:
                for j2 in r:
                    if j1 < j2:
                        disj = set()
                        literal = ('x' + str(i) + str(j1) + str(k), False)
                        disj.add(literal)
                        literal = ('x' + str(i) + str(j2) + str(k), False)
                        disj.add(literal)
                        conj.append(disj)

    # jede Zahl kommt pro Spalte vor:
    for j in r:  # Spalte j
        for k in r:  # Wert k
            disj = set()
            for i in r:
                literal = ('x' + str(i) + str(j) + str(k), True)
                disj.add(literal)
            conj.append(disj)

    # jede Zahl kommt pro Spalte höchstens einmal vor:
    for j in r:  # Spalte j
        for k in r:  # Wert k
            for i1 in r:
                for i2 in r:
                    if i1 < i2:
                        disj = set()
                        literal = ('x' + str(i1) + str(j) + str(k), False)
                        disj.add(literal)
                        literal = ('x' + str(i2) + str(j) + str(k), False)
                        disj.add(literal)
                        conj.append(disj)

    # jede Zahl kommt in kleinem Quadrat vor
    for i1 in (1, 4, 7):
        for j1 in (1, 4, 7):
            for k in r:
                disj = set()
                for i2 in range(0, 3):
                    for j2 in range(0, 3):
                        literal = ('x' + str(i1 + i2) + str(j1 + j2) + str(k), True)
                        disj.add(literal)
                conj.append(disj)

    # jede Zahl kommt in kleinem Quadrat höchstens einmal vor:
    for i1 in (1, 4, 7):
        for j1 in (1, 4, 7):
            for k in r:
                for i21 in range(0, 3):
                    for j21 in range(0, 3):
                        for i22 in range(0, 3):
                            for j22 in range(0, 3):
                                if i21 < i22 or j21 < j22:
                                    disj = set()
                                    literal = ('x' + str(i1 + i21) + str(j1 + j21) + str(k), False)
                                    disj.add(literal)
                                    literal = ('x' + str(i1 + i22) + str(j1 + j22) + str(k), False)
                                    disj.add(literal)
                                    conj.append(disj)

    return conj


def test_sudoku_cnf_from_general_rules():
    cnf = sudoku_cnf_from_general_rules()
    print(cnf)
    print('lenght = ' + str(len(cnf)))


# test_sudoku_cnf_from_general_rules()


def parse_cnf(cnf):
    for clause in cnf:
        line = ''
        for literal in clause:
            line += (' ' if literal[1] else ' ~') + literal[0]
        yield (line)


def parse_and_print_cnf(cnf, outputFilename=None):
    """
    :param cnf: list of sets of 2-tuples (var, bool) where var are variable names, bool
        is True or False, describing a propositional logic statement in
        conjunctive normal form (cnf)
    :param outputFilename: where each line consists of disjunctive
        clauses of the form
            [~]var_1 [~]var_2 ... [~]var_n
        eg.
            ~x123 x745 ~733
        and the combination of lines is to be interpreted as conjunctions
        If outputFilename is none then the output is printed onto console.
    :return: True if there were no errors
    """

    if outputFilename:
        write_file = open(outputFilename, 'w')
    else:
        write_file = sys.stdout

    for line in parse_cnf(cnf):
        write_file.write(line + '\n')

    if outputFilename:
        write_file.close()

    return None


def parse_result_into_grid(input_filename):
    with open(input_filename, 'r') as f:
        itemlist = f.read().split()
    result_grid = [[0 for __ in range(9)] for __ in range(9)]
    for item in itemlist:
        result_grid[int(item[1]) - 1][int(item[2]) - 1] = int(item[3])
    return result_grid


def solve_sudoku(grid):
    # Sudoku-CNF gemaess grid aufstellen
    jetzt = time()
    print(time() - jetzt)
    all_cnf = sudoku_cnf_from_starting_grid(grid) + sudoku_cnf_from_general_rules()
    parse_and_print_cnf(all_cnf, "sudoku_all_cnf.txt")
    input_file = open('sudoku_all_cnf.txt', 'r')
    output_file = open('sudoku_result.txt', 'w')
    print(time() - jetzt)
    sat.run_solver(input_file,
                   output_file,
                   solver,
                   True,
                   False,
                   False,
                   '')
    print(time()-jetzt)
    input_file.close()
    output_file.close()
    return parse_result_into_grid("sudoku_result.txt")
    print(time()-jetzt)

# for item in solve_sudoku(test_grid()):
#    print(item)
