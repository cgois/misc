import re
import argparse

SECTIONS = r"(Names:|Names|Equations:|Equations|Inequalities:|Inequalities|\n)"
KEYWORDS = ["Names", "Equations", "Inequalities"]


def parse_expression(expression, basis, separator):

    coefficients = []
    coefficients.append(re.findall(rf"(?<={separator})[-+\d\s]*", expression)[0])
    for x in basis:
        try:
            coefficients.append(re.findall(rf"^(?={x})|[-+][\d\s]*?(?={x})", expression)[0])
        except IndexError: # If term isn't in expression.
            coefficients.append("0")

    coefficients = [x.replace(' ', '') for x in coefficients]
    coefficients = map(lambda x: '1' if (x == '+' or x == '') else x, coefficients)
    coefficients = map(lambda x: '-1' if x == '-' else x, coefficients)
    coefficients = list(map(int, coefficients))
    coefficients[0] = -coefficients[0]

    if "<=" in expression:
        coefficients = map(lambda x: -x, coefficients)

    return list(coefficients)


def panda2lrs(fname):

    with open(fname, 'r') as file:
        raw = re.split(SECTIONS, file.read())
    expressions = list(filter(None, filter((lambda x: x != "\n"), raw)))

    # Find starting indexes for each section.
    indexes = {}
    for kword in KEYWORDS:
        try:
            indexes[kword] = expressions.index(kword)
        except ValueError:
            pass

    # Parse all variables' names.
    try:
        NAMES = expressions[indexes["Names"] + 1].split()
    except KeyError:
        raise KeyError("Missing variables names in input file.")

    # Extract equations' coefficients and turn them into two inequalities.
    equations = []
    if "Equations" in indexes.keys():
        end = indexes["Inequalities"] if "Inequalities" in indexes.keys() else -1

        for expression in expressions[indexes["Equations"] + 1:end]:
            equations.append(parse_expression(expression, NAMES, "="))
            equations.append(list(map(lambda x: -x, equations[-1])))

    # Extract inequalities' coefficients.
    inequalities = []
    if "Inequalities" in indexes.keys():
        inequalities = [parse_expression(expression, NAMES, "<=|>=")
                        for expression in expressions[indexes["Inequalities"] + 1:]]

    lrs = f"H-representation\nbegin\n{len(equations + inequalities)} {len(NAMES) + 1} rational\n"
    lrs += "\n".join([" ".join(map(str, expr)) for expr in equations + inequalities])
    return lrs + "\nend"


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str, help='Input file name')
    parser.add_argument('output', nargs='?', type=str, default=None, help='Output file name')
    args = parser.parse_args()

    if args.output:
        with open(args.output, 'w') as file:
            file.write(panda2lrs(args.fname))
    else:
        print(panda2lrs(args.fname))
