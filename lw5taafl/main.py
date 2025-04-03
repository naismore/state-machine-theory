import csv
import sys


class RegexNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f"RegexNode({self.value})"


class State:
    def __init__(self):
        self.transitions = {}
        self.epsilonTransitions = []

    def addTransition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

    def addEpsilonTransition(self, state):
        self.epsilonTransitions.append(state)


class NFA:
    def __init__(self, startState, acceptState):
        self.startState = startState
        self.acceptState = acceptState


def isLiteral(value):
    return value not in "+*()|"


def parseRegex(expression):
    def parse(tokens):
        def getNext():
            return tokens.pop(0) if tokens else None

        def parsePrimary():
            token = getNext()
            if token == "\\":
                escaped = getNext()
                if isLiteral(escaped):
                    tokens.insert(0, escaped)
                else:
                    return RegexNode(escaped)
            if isLiteral(token):
                return RegexNode(token)
            elif token == "(":
                node = parseExpression()
                if getNext() != ")":
                    raise ValueError("Mismatched parentheses")
                return node
            raise ValueError(f"Unexpected token: {token}")

        def parseFactor():
            node = parsePrimary()
            while tokens and tokens[0] in ("*", "+"):
                op = "multiply" if getNext() == "*" else "add"
                node = RegexNode(op, left=node)
            return node

        def parseTerm():
            node = parseFactor()
            while tokens and tokens[0] and (isLiteral(tokens[0]) or tokens[0] == "("):
                right = parseFactor()
                node = RegexNode("concat", left=node, right=right)
            return node

        def parseExpression():
            node = parseTerm()
            while tokens and tokens[0] == "|":
                getNext()
                right = parseTerm()
                node = RegexNode("or", left=node, right=right)
            return node

        return parseExpression()

    tokens = []
    for char in expression:
        tokens.append(char)

    return parse(tokens)


def printTree(node, level=0):
    if node is not None:
        printTree(node.right, level + 1)
        print(" " * 4 * level + "->", node.value)
        printTree(node.left, level + 1)


def buildNfa(node):
    if node is None:
        return None

    if node.value not in ("concat", "or", "add", "multiply"):
        start = State()
        accept = State()
        start.addTransition(node.value, accept)
        return NFA(start, accept)
    elif node.value == "concat":
        left = buildNfa(node.left)
        right = buildNfa(node.right)
        left.acceptState.addEpsilonTransition(right.startState)
        return NFA(left.startState, right.acceptState)
    elif node.value == "or":
        start = State()
        accept = State()
        left = buildNfa(node.left)
        rightNfa = buildNfa(node.right)
        start.addEpsilonTransition(left.startState)
        start.addEpsilonTransition(right.startState)
        left.acceptState.addEpsilonTransition(accept)
        right.acceptState.addEpsilonTransition(accept)
        return NFA(start, accept)
    elif node.value == "multiply":
        start = State()
        accept = State()
        sub = buildNfa(node.left)
        start.addEpsilonTransition(sub.startState)
        start.addEpsilonTransition(accept)
        sub.acceptState.addEpsilonTransition(sub.startState)
        sub.acceptState.addEpsilonTransition(accept)
        return NFA(start, accept)
    elif node.value == "add":
        start = State()
        accept = State()
        sub = buildNfa(node.left)
        start.addEpsilonTransition(sub.startState)
        sub.acceptState.addEpsilonTransition(sub.startState)
        sub.acceptState.addEpsilonTransition(accept)
        return NFA(start, accept)

    raise ValueError(f"Unexpected node value: {node.value}")


def printNfa(nfa):
    def printState(state, visited, stateIndex):
        if state in visited:
            return
        visited.add(state)
        for symbol, states in state.transitions.items():
            for s in states:
                print(f"    S{stateIndex[state]}-- {symbol} -->S{stateIndex[s]}")
                printState(s, visited, stateIndex)
        for s in state.epsilonTransitions:
            print(f"    S{stateIndex[state]}-- ε -->S{stateIndex[s]}")
            printState(s, visited, stateIndex)

    stateIndex = {}
    index = 0

    def assignIndices(state):
        nonlocal index
        if state not in stateIndex:
            stateIndex[state] = index
            index += 1
            for symbol, states in state.transitions.items():
                for s in states:
                    assignIndices(s)
            for s in state.epsilonTransitions:
                assignIndices(s)

    assignIndices(nfa.startState)

    print("NFA:")
    print("flowchart LR")
    printState(nfa.startState, set(), stateIndex)


def assignIndices(startState):
    stateIndex = {}
    index = 0
    stack = [startState]

    while stack:
        state = stack.pop()
        if state not in stateIndex:
            stateIndex[state] = f"S{index}"
            index += 1
            for symbol, states in state.transitions.items():
                for s in states:
                    if s not in stateIndex:
                        stack.append(s)
            for s in state.epsilonTransitions:
                if s not in stateIndex:
                    stack.append(s)

    return stateIndex


def writeNfa(nfa, output):
    stateIndex = assignIndices(nfa.startState)
    finalState = stateIndex[nfa.acceptState]

    transitions = {stateIndex[s]: {} for s in stateIndex}

    for state, name in stateIndex.items():
        for symbol, states in state.transitions.items():
            transitions[name].setdefault(symbol, set()).update(stateIndex[s] for s in states)
        for s in state.epsilonTransitions:
            transitions[name].setdefault("ε", set()).add(stateIndex[s])

    symbols = set()
    for state in transitions:
        trans = transitions[state]
        for symbol in trans:
            symbols.add(symbol)

    with open(output, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow([""] + ["F" if state == finalState else "" for state in stateIndex.values()])
        writer.writerow([""] + [state for state in stateIndex.values()])

        for symbol in symbols:
            row = [symbol]
            for state in stateIndex.values():
                row.append(",".join(transitions.get(state, {}).get(symbol, {})))
            writer.writerow(row)


def processRegex(regexPattern, output):
    tree = parseRegex(regexPattern)
    nfa = buildNfa(tree)
    writeNfa(nfa, output)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <output-file> <regex pattern>")
        return 1

    output = sys.argv[1]
    regexPattern = sys.argv[2]

    try:
        processRegex(regexPattern, output)
    except RuntimeError as e:
        print(e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
