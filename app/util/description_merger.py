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
    def __init__(self, data: str, children) -> None:
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
                value = round(child.value, 5)
                res += str(int(value)) if value.is_integer() else f"{value}"
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

    for item in addTree.children:
        unit: Tree = item.unit
        targetItem: TreeItem = None
        if not unit or unit.children[0].type == "COUNT":
            # find where no unit or count (x)
            targetItem = next(desTree.find_pred(lambda t: t.data ==
                                                "item" and (not t.unit or t.unit.children[0].type == "COUNT")), None)
        else:
            # find where unit type is equal (SI_WEIGHT == SI_WEIGHT) but not description or description is equal ("halves" == "halves")
            targetItem = next(desTree.find_pred(lambda t: t.data ==
                                                "item" and t.unit and
                                                (t.unit.children[0].type == unit.children[0].type and not t.unit.children[0].type == "DESCRIPTION"
                                                 or t.unit.children[0].lower() == unit.children[0].lower())), None)

        if not targetItem:  # No item with same unit
            desTree.children.append(item)
        else:  # Found item with same unit
            if not targetItem.number:  # Add number if not present
                targetItem.number = Token("NUMBER", 1)
                targetItem.children.insert(0, targetItem.number)

            # Add up numbers
            if unit and unit.children[0].type == "SI_WEIGHT":
                merge_SI_Weight(targetItem, item)
            elif unit and unit.children[0].type == "SI_VOLUME":
                merge_SI_Volume(targetItem, item)
            else:
                targetItem.number.value = targetItem.number.value + \
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


def merge_SI_Volume(base: TreeItem, add: TreeItem) -> None:
    def toMl(x: float, unit: str):
        return {'ml': x, 'l': 1000*x}.get(unit.lower())

    base.number.value = toMl(base.number.value, base.unit.children[0]) + \
        toMl(add.number.value if add.number else 1.0, add.unit.children[0])
    base.unit.children[0] = base.unit.children[0].update(value='ml')

    # Simplify if possible
    if (base.number.value/1000).is_integer():
        base.number.value = base.number.value/1000
        base.unit.children[0] = base.unit.children[0].update(value='L')


def merge_SI_Weight(base: TreeItem, add: TreeItem) -> None:
    def toG(x: float, unit: str):
        return {'mg': x/1000, 'g': x, 'kg': 1000*x}.get(unit.lower())

    base.number.value = toG(base.number.value, base.unit.children[0]) + \
        toG(add.number.value if add.number else 1.0, add.unit.children[0])
    base.unit.children[0] = base.unit.children[0].update(value='g')

    # Simplify when possible
    if base.number.value < 1:
        base.number.value = base.number.value*1000
        base.unit.children[0] = base.unit.children[0].update(value='mg')
    elif (base.number.value/1000).is_integer():
        base.number.value = base.number.value/1000
        base.unit.children[0] = base.unit.children[0].update(value='kg')
