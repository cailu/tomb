import os

solutions = []

def get_solutions():
    if solutions:
        return solutions
    filename = os.path.dirname(os.path.abspath(__file__)) + '/solutions.txt'
    with open(filename) as fin:
        sol = []
        for line in fin:
            line = line.strip()
            if len(line) == 0 and sol:
                solutions.append(sol)
                sol = []
            else:
                sol.append(line)
        if sol:
            solutions.append(sol)
    return solutions


if __name__ == '__main__':
    print(get_solutions())
