from abc import ABC, abstractmethod

from .utils import BaseRegistry, BaseFabric


class CalculatorCPM(ABC):

    @abstractmethod
    def calculate_start_cpm(self) -> int:
        ...

class DefaultCalculatorCPM(CalculatorCPM):

    def __init__(self, min_cpm: int, max_cpm: int):
        self.min_cpm = min_cpm
        self.max_cpm = max_cpm

    def calculate_start_cpm(self) -> int:
        part_max_cpm = self.max_cpm // 3

        return part_max_cpm if self._check_valid_cpm(part_max_cpm=part_max_cpm) else self.min_cpm

    def _check_valid_cpm(self, part_max_cpm: int) -> bool:
        return part_max_cpm > self.min_cpm

class CalculatorCPMRegisty(BaseRegistry):
    _registry = {}

class CalculatorCPMFabric(BaseFabric): ...

CalculatorCPMRegisty.register_obj("default", DefaultCalculatorCPM)