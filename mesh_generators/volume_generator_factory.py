from abc import ABC, abstractmethod
from typing import Dict, Union
from mesh_generators.volume_generator import VolumeGenerator, ParamType
from mesh_generators.branching_elements_generator import BranchingElementsGenerator
from mesh_generators.porous_material_volume_generator import PorousMaterialVolumeGenerator

class VolumeGeneratorFactory:
    _registry: Dict[str, type[VolumeGenerator]] = {
        "branching_structure": BranchingElementsGenerator,
        "porous_material": PorousMaterialVolumeGenerator
    }

    @classmethod
    def build(cls, model_name: str, params: ParamType) -> VolumeGenerator:
        generator_cls = cls._registry.get(model_name)
        if not generator_cls:
            raise ValueError(f"Unknown model: {model_name}")
        return generator_cls.build(params)
