import re
import sys

def readFileToString(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            fileContent = file.read()
            firstLine = fileContent.split("\n")[0].strip('|')
            return fileContent, firstLine
    except IOError as e:
        raise RuntimeError(f"Unable to open file: {filename}") from e

def processGrammar(inputFilename, outputFilename):
    content, first_line = readFileToString(inputFilename)
    parser = getParser(content)
    grammar, initialState = parser(content)
    generateCsvFile(grammar, outputFilename, initialState)


def parseRightLinearGrammar(content):
    grammarPattern = re.compile(
        r"^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$",
        re.MULTILINE
    )
    transitionPattern = re.compile(r"^\s*([\wε]*)\s*(?:<(\w*)>)?\s*$")

    grammar = {}
    initialState = None

    for match in grammarPattern.finditer(content):
        state = match.group(1)
        initialState = initialState or state
        transitions = match.group(2).split("|")

        grammar["H"] = {"is_finite": "F", "transitions": {}}

        for transition in transitions:
            transMatch = transitionPattern.search(transition)
            symbol = transMatch.group(1)
            nextState = transMatch.group(2) or "H"

            if state not in grammar:
                grammar[state] = {
                    "is_finite": "",
                    "transitions": {symbol: [nextState]}
                }
            else:
                if symbol not in grammar[state]["transitions"]:
                    grammar[state]["transitions"][symbol] = [nextState]
                else:
                    grammar[state]["transitions"][symbol].append(nextState)

    return grammar, initialState


def parseLeftLinearGrammar(content):
    grammarPattern = re.compile(
        r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$",
        re.MULTILINE
    )
    transitionPattern = re.compile(r"^\s*(?:<(\w*)>)?\s*([\wε]*)\s*$")

    grammar = {}
    finiteState = None

    for match in grammarPattern.finditer(content):
        state = match.group(1)
        finiteState = finiteState or state
        transitions = match.group(2).split("|")

        if state not in grammar:
            grammar[state] = {
                "is_finite": "F" if state == finiteState else "",
                "transitions": {}
            }

        for transition in transitions:
            transMatch = transitionPattern.search(transition)
            symbol = transMatch.group(2)
            nextState = transMatch.group(1) or "H"

            if nextState not in grammar:
                grammar[nextState] = {
                    "is_finite": "F" if nextState == finiteState else "",
                    "transitions": {symbol: [state]}
                }
            else:
                if symbol not in grammar[nextState]["transitions"]:
                    grammar[nextState]["transitions"][symbol] = [state]
                else:
                    grammar[nextState]["transitions"][symbol].append(state)

    return grammar, "H"


def generateCsvFile(grammar, outputFileName, initialState="H"):
    states = [initialState] + [state for state in grammar if state != initialState]
    symbols = sorted({symbol for state in grammar for symbol in grammar[state]['transitions']})

    csvHeader1 = [''] + ['F' if grammar[state]['is_finite'] == 'F' else '' for state in states]
    csvHeader2 = [''] + [f'q{i}' for i in range(len(states))]
    stateIndexMap = {state: f'q{i}' for i, state in enumerate(states)}

    rows = []
    for symbol in symbols:
        row = [''] * (len(states) + 1)
        row[0] = symbol
        for state in states:
            state_index = states.index(state) + 1
            transitions = grammar[state]['transitions'].get(symbol, [])
            row[state_index] = ",".join(stateIndexMap[nextState] for nextState in transitions)
        rows.append(row)

    with open(outputFileName, "w", encoding="utf-8") as outputFile:
        outputFile.write(';'.join(csvHeader1) + "\n")
        outputFile.write(';'.join(csvHeader2) + "\n")
        for row in rows:
            outputFile.write(';'.join(row) + "\n")


def getParser(text):
    pattern = re.compile(
        r"^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$",
        re.MULTILINE
    )
    if len(re.findall(pattern, text)) == text.count('->'):
        return parseRightLinearGrammar
    pattern = re.compile(
        r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$",
        re.MULTILINE
    )
    if len(re.findall(pattern, text)) == text.count('->'):
        return parseLeftLinearGrammar
    return parseLeftLinearGrammar


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input-file> <output-file>")
        return 1

    input = sys.argv[1]
    output = sys.argv[2]

    try:
        processGrammar(input, output)
    except RuntimeError as e:
        print(e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
