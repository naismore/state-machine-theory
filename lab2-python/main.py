import csv
import sys


def readMoore(filename):
    states = []
    inputSymbols = []
    transitions = {}
    outputs = {}
    initialState = None

    with open(filename, 'r', newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        outputsRow = list(reversed(next(reader)[1:]))
        states = next(reader)[1:]
        initialState = states[0]
        for state in states:
            outputs[state] = outputsRow.pop()
        for row in reader:
            symbol = row[0]
            inputSymbols.append(symbol)
            for index in range(len(row) - 1):
                transitions.setdefault(states[index], {})[symbol] = row[index + 1]

    return states, inputSymbols, transitions, outputs, initialState


def readMealy(filename):
    states = []
    inputSymbols = []
    transitions = {}
    outputs = {}
    initialState = None

    with open(filename, 'r', newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        states = next(reader)[1:]
        initialState = states[0]
        for row in reader:
            symbol = row[0]
            inputSymbols.append(symbol)
            for index in range(len(row) - 1):
                if "/" in row[index + 1]:
                    state, output = row[index + 1].split('/')
                    transitions.setdefault(states[index], {})[symbol] = state
                    outputs.setdefault(states[index], {})[symbol] = output
                else:
                    transitions.setdefault(states[index], {})[symbol] = ""
                    outputs.setdefault(states[index], {})[symbol] = ""
    return states, inputSymbols, transitions, outputs, initialState


def writeMealy(filename, states, inputSymbols, transitions, outputs, initialState):
    states = [initialState] + list(filter(lambda x: x != initialState, states))
    with open(filename, 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([""] + states)
        for symbol in inputSymbols:
            row = [symbol]
            for state in states:
                transition = transitions[state][symbol]
                output = outputs[state][symbol]
                if transition and output:
                    row.append(f"{transition}/{output}")
                else:
                    row.append("")
            writer.writerow(row)


def writeMoore(filename, states, inputSymbols, transitions, outputs, initialState):
    states = [initialState] + list(filter(lambda x: x != initialState, states))
    with open(filename, 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        outputsRow = [""]
        for state in states:
            outputsRow.append(outputs[state])
        writer.writerow(outputsRow)
        writer.writerow([""] + states)
        for symbol in inputSymbols:
            row = [symbol]
            for state in states:
                row.append(transitions[state][symbol])
            writer.writerow(row)


def removeUnreachableStates(states, inputSymbols, transitions, outputs, initialState):
    reachableStates = set()
    toVisit = [initialState]

    while toVisit:
        state = toVisit.pop()
        if state in reachableStates:
            continue
        reachableStates.add(state)

        for symbol in transitions[state]:
            transition = transitions[state][symbol]
            if transition:
                toVisit.append(transition)

    return list(filter(lambda x: x in reachableStates, states)), inputSymbols, transitions, outputs, initialState


def minimizeMealy(states, inputSymbols, transitions, outputs, initialState):
    outputGroups = {}
    for state in states:
        output = ""
        for symbol in inputSymbols:
            output += outputs[state][symbol]
        outputGroups.setdefault(output, set()).add(state)

    partitions = list(outputGroups.values())

    def refine(partitions):
        newPartitions = []
        for group in partitions:
            subgroup = {}
            for state in group:
                key = ""
                for symbol in inputSymbols:
                    key += str(next((i for i, s in enumerate(partitions) if transitions[state][symbol] in s)))
                subgroup.setdefault(key, set()).add(state)
            newPartitions.extend(subgroup.values())
        return newPartitions

    while True:
        newPartitions = refine(partitions)
        if newPartitions == partitions:
            break
        partitions = newPartitions

    stateMap = {}
    minimizedStates = []
    minimizedTransitions = {}
    minimizedOutputs = {}

    for i, group in enumerate(partitions):
        newState = f"S{i}"
        for state in group:
            stateMap[state] = newState
        minimizedStates.append(newState)

    for group in partitions:
        representative = next(iter(group))
        newState = stateMap[representative]
        minimizedTransitions[newState] = {
            symbol: stateMap[transitions[representative][symbol]]
            for symbol in inputSymbols
        }
        minimizedOutputs[newState] = {
            symbol: outputs[representative][symbol]
            for symbol in inputSymbols
        }

    minimizedInitialState = stateMap[initialState]

    return minimizedStates, inputSymbols, minimizedTransitions, minimizedOutputs, minimizedInitialState


def minimizeMoore(states, inputSymbols, transitions, outputs, initialState):
    outputGroups = {}
    for state in states:
        output = outputs[state]
        outputGroups.setdefault(output, set()).add(state)

    partitions = list(outputGroups.values())

    def refine(partitions):
        newPartitions = []
        for group in partitions:
            subgroup = {}
            for state in group:
                key = ""
                for symbol in inputSymbols:
                    for i, s in enumerate(partitions):
                        if transitions[state][symbol] in s:
                            key += symbol + str(i)
                subgroup.setdefault(key, set()).add(state)
            newPartitions.extend(subgroup.values())
        return newPartitions

    while True:
        newPartitions = refine(partitions)
        if newPartitions == partitions:
            break
        partitions = newPartitions

    stateMap = {}
    minimizedStates = []
    minimizedTransitions = {}
    minimizedOutputs = {}

    for i, group in enumerate(partitions):
        newState = f"S{i}"
        for state in group:
            stateMap[state] = newState
        minimizedStates.append(newState)
        representative = next(iter(group))
        minimizedOutputs[newState] = outputs[representative]

    for group in partitions:
        representative = next(iter(group))
        newState = stateMap[representative]
        minimizedTransitions[newState] = {
            symbol: stateMap[transitions[representative][symbol]] if transitions[representative][symbol] else ""
            for symbol in inputSymbols
        }
    minimizedInitialState = stateMap[initialState]

    return minimizedStates, inputSymbols, minimizedTransitions, minimizedOutputs, minimizedInitialState


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <machine-type> <input-file> <output-file>")
        return 1

    machineType = sys.argv[1]
    inputFileName = sys.argv[2]
    outputFileName = sys.argv[3]

    try:
        if machineType == "mealy":
            values = readMealy(inputFileName)
            values = removeUnreachableStates(*values)
            values = minimizeMealy(*values)
            writeMealy(outputFileName, *values)
        elif machineType == "moore":
            values = readMoore(inputFileName)
            values = removeUnreachableStates(*values)
            values = minimizeMoore(*values)
            writeMoore(outputFileName, *values)
        else:
            print(f"Unknown machine type: {machineType}")
            return 1
    except RuntimeError as e:
        print(e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
