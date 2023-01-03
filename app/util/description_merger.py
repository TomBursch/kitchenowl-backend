from lark import Lark, Transformer, Tree, Token
from lark.visitors import Interpreter
import re

grammar = r'''
start: ","* item (","+ item)*

item: NUMBER? unit?
unit: COUNT | SI_WEIGHT | SI_VOLUME | DESCRIPTION
COUNT.5: "x"i
SI_WEIGHT.5: "mg"i | "g"i | "kg"i
SI_VOLUME.5: "ml"i | "l"i
DESCRIPTION: /[^0-9, ][^,]*/

DECIMAL: INT ("." | ",") INT? | "." INT
FLOAT: INT _EXP | DECIMAL _EXP?
NUMBER.10: FLOAT | INT

%ignore WS
%import common (_EXP, INT, WS)
'''


class TreeItem(Tree):
    # Quick and dirty class to not build an AST
    def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]') -> None:
        self.data = data
        self.children = children
        self.number: Token = None
        self.unit: Tree = None
        for c in children:
            if isinstance(c, Token) and c.type == "NUMBER":
                self.number = c
            else:
                self.unit = c


class T(Transformer):
    def NUMBER(self, number: Token):
        return number.update(value=float(number.replace(",", ".")))

    def item(self, children):
        return TreeItem("item", children)


class Printer(Interpreter):
    def item(self, item: Tree):
        res = ""
        for child in item.children:
            if isinstance(child, Tree):
                if res and child.children[0].type == "DESCRIPTION":
                    res += " "
                res += self.visit(child)
            elif child.type == 'NUMBER':
                res += str(int(child.value)
                           ) if child.value.is_integer() else f"{child.value:.2f}"
        return res

    def unit(self, unit: Tree):
        return unit.children[0]

    def start(self, start: Tree):
        return ", ".join([s for s in self.visit_children(start) if s])


# Objects
parser = Lark(grammar)
transformer = T()


def merge(description: str, added: str) -> str:
    if not description:
        description = "1x"
    if not added:
        added = "1x"
    description = clean(description)
    added = clean(added)
    desTree = transformer.transform(parser.parse(description))
    addTree = transformer.transform(parser.parse(added))
    print(desTree)

    for item in addTree.children:
        unit = item.unit
        res: TreeItem = None
        if not unit:
            res = next(desTree.find_pred(lambda t: t.data ==
                       "item" and (not t.unit or t.unit.children[0].type == "COUNT")), None)
        else:
            res = next(desTree.find_pred(lambda t: t.data ==
                       "item" and t.unit == unit), None)

        if not res:
            desTree.children.append(item)
        else:
            if not res.number:
                res.number = Token("NUMBER", 1)
                res.children.insert(0, res.number)

            res.number.value = res.number.value + \
                (item.number.value if item.number else 1.0)

    return Printer().visit(desTree)


def clean(input: str) -> str:
    input = re.sub(
        '¼|½|¾|⅐|⅑|⅒|⅓|⅔|⅕|⅖|⅗|⅘|⅙|⅚|⅛|⅜|⅝|⅞',
        lambda match: {
            '¼': '0.25',
            '½': '0.5',
            '¾': '0.75',
            '⅐': '0.142857142857',
            '⅑': '0.111111111111',
            '⅒': '0.1',
            '⅓': '0.333333333333',
            '⅔': '0.666666666667',
            '⅕': '0.2',
            '⅖': '0.4',
            '⅗': '0.6',
            '⅘': '0.8',
            '⅙': '0.166666666667',
            '⅚': '0.833333333333',
            '⅛': '0.125',
            '⅜': '0.375',
            '⅝': '0.625',
            '⅞': '0.875',
        }.get(match.group(), match.group),
        input
    )

    # replace 1/2 with .5
    input = re.sub(
        r'(\d+((\.)\d+)?)\/(\d+((\.)\d+)?)',
        lambda match: str(float(match.group(1)) /
                          float(match.group(4))),
        input
    )

    return input
