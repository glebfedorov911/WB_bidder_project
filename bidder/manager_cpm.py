from abc import ABC, abstractmethod
import os

from .settings import *
from .utils import BaseRegistry, BaseFabric


class ManagerCPM(ABC):
    
    @abstractmethod
    def increase_cpm(self) -> int:
        ...

class BaseManagerCPM(ManagerCPM):


    def __init__(
        self, 
        cpm: int, 
        step: int,
        current_position: int,
        wish_position: int
    ):
        self.cpm = cpm
        self.step = step
        self.current_position = current_position
        self.wish_position = wish_position

    def _get_positive_or_negative_step_increase_of_position_dif(self, step):
        return -step if self.wish_position > self.current_position else step

class DefaultManagerCPM(BaseManagerCPM):

    
    def __init__(
        self, 
        cpm: int, 
        step: int,
        current_position: int,
        wish_position: int
    ):
        super().__init__(cpm, step, current_position, wish_position)

    def increase_cpm(self):
        return self.cpm + self._get_positive_or_negative_step_increase_of_position_dif(self.step)

class MomentumManagerCPM(BaseManagerCPM):
    DEFAULT_DIF_PLACES = settings.cpm_var.default_dif_between_position_momentum_mode
    MINIMUM_STEP = settings.cpm_var.step_cpm
    
    def __init__(
        self, 
        cpm: int, 
        step: int,
        current_position: int,
        wish_position: int
    ):
        super().__init__(cpm, step, current_position, wish_position)


    def increase_cpm(self):
        use_minimum_step = self._check_dif_between_positions()
        self.step = self.MINIMUM_STEP if use_minimum_step else self.step

        return self.cpm + self._get_positive_or_negative_step_increase_of_position_dif(self.step)

    def _check_dif_between_positions(self):
        return abs(self.wish_position - self.current_position) < self.DEFAULT_DIF_PLACES

class ManagerCPMRegistry(BaseRegistry): 
    _registry = {}

class ManagerCPMFabric(BaseFabric): ...

ManagerCPMRegistry.register_obj('default', DefaultManagerCPM)
ManagerCPMRegistry.register_obj('momentum', MomentumManagerCPM)