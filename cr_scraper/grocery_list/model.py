from collections import defaultdict
from enum import StrEnum, auto

from cr_scraper.grocery_list.exceptions import NegativeQuantityError, TermMismatchError


class GroceryListElement:
    class Unit(StrEnum):
        KG = auto()
        G = auto()
        MG = auto()
        L = auto()
        ML = auto()

        @classmethod
        def _missing_(cls, value):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
            return None

    _UNIT_CONVERSION = {
        Unit.KG: {Unit.G: 1000, Unit.MG: 1000000},
        Unit.G: {Unit.KG: 0.001, Unit.MG: 1000},
        Unit.MG: {Unit.KG: 0.000001, Unit.G: 0.001},
    }

    def __init__(self, name: str, quantity: float, unit: str):
        if quantity < 0:
            raise NegativeQuantityError
        self.name = name
        self.quantity = quantity
        try:
            self.unit = self.Unit(unit)
        except ValueError:
            self.unit

    def __add__(self, other):
        if not isinstance(other, GroceryListElement) or self.name != other.name:
            raise TermMismatchError
        if self.unit == other.unit or self._can_convert(other.unit):
            quantity = self.quantity + other.quantity
            return GroceryListElement(name=self.name, quantity=quantity, unit=self.unit)
        else:
            return [self, other]

    def _can_convert(self, unit: Unit):
        return self.unit in self._UNIT_CONVERSION.get(unit, {})


class GroceryList:
    def __init__(self):
        self.elements: dict[str, list[GroceryListElement]] = defaultdict(list)

    def add_element(self, element: GroceryListElement):
        self.elements[element.name].append(element)
