from abc import ABC, abstractmethod
from typing import Dict, Union

ParamType = Dict[str, Union[int, float, bool]]

class VolumeGenerator(ABC):
    @classmethod
    def build(self, params: ParamType):
        self.params = params
        VolumeGenerator()

    @abstractmethod
    def generate_volume(self) -> list[int]:
        pass
