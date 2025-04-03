import csv
import sys


def readMachineFromFile(filename):
    finiteState = None
    states = []
    machine = {}
    with open(filename, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        finiteMarkers = next(reader)[1:]
        states = next(reader)[1:]
        finiteState = states[finiteMarkers.index("F")]
        for row in reader:
            symbol = row[0]
            for i in range(1, len(row)):
                state = states[i - 1]
                if state not in machine:
                    machine[state] = {
                        "is_finite": state == finiteState,
                        "transitions": {}
                    }
                machine[state]["transitions"][symbol] = list(filter(lambda x: x != '', row[i].split(",")))

    return states[0], finiteState, machine


def fillEpsilon(machine):
    epsilon = {}

    for state in machine:
        transitions = []
        if "ε" in machine[state]["transitions"]:
            transitions = machine[state]["transitions"]["ε"]
        visited = set()
        stack = [state]

        while stack:
            vertex = stack.pop()

            if vertex not in visited:
                visited.add(vertex)

                if "ε" not in machine[vertex]["transitions"]:
                    continue
                for neighbor in machine[vertex]["transitions"]["ε"]:
                    if neighbor:
                        stack.append(neighbor)

        epsilon[state] = list(visited)

    return epsilon


def getDependencies(states, epsilon):
    dependencies = set()

    for state in states:
        dependencies.add(state)
        for transition in epsilon[state]:
            dependencies.add(transition)

    return list(dependencies)


def findKeyWithValue(dictionary, newValue):
    for key, value in dictionary.items():
        if tuple(sorted(value)) == tuple(sorted(newValue)):
            return key

    return None


def createNew(initialState, finiteState, epsilon, machine):
    count = 0
    stateDependencies = {"s0": [initialState]}
    states = ["s0"]
    newMachine = {}

    for state in states:
        newMachine[state] = {
            "is_finite": finiteState in getDependencies(stateDependencies[state], epsilon),
            "transitions": {}
        }

        for symbol in filter(lambda x: x != "ε", machine[initialState]["transitions"]):
            transitions = []
            for dependency in getDependencies(stateDependencies[state], epsilon):
                transitions.extend(machine[dependency]["transitions"][symbol])
            transitions = list(set(transitions))
            key = ''
            if len(transitions) != 0:
                key = findKeyWithValue(stateDependencies, transitions)
            if key is None:
                count += 1
                key = f"s{count}"
                states.append(key)
                stateDependencies[key] = transitions
            newMachine[state]["transitions"][symbol] = key

    return newMachine

def processMachine(input, output):
    initialState, finiteState, machine = readMachineFromFile(input)
    epsilon = fillEpsilon(machine)
    newMachine = createNew(initialState, finiteState, epsilon, machine)
    write(newMachine, output)

def write(machine, filename):
    symbols = set()
    for state in machine:
        transitions = machine[state]["transitions"]
        for symbol in transitions:
            symbols.add(symbol)

    finiteMarkers = [""]
    for state in machine:
        marker = machine[state]["is_finite"]
        finiteMarkers.append("F" if marker else "")

    states = [""] + [state for state in machine]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(finiteMarkers)
        writer.writerow(states)
        for symbol in symbols:
            row = [symbol]
            for state in states[1:]:
                row.append(machine[state]["transitions"][symbol])
            writer.writerow(row)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input-file> <output-file>")
        return 1

    input = sys.argv[1]
    output = sys.argv[2]

    try:
        processMachine(input, output)
    except RuntimeError as e:
        print(e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
