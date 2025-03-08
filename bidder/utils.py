from .custom_exceptions import CPMException


class BaseRegistry:
    _registry = {}

    @classmethod
    def register_obj(cls, obj_type: str, obj_class):
        obj_type_lower = cls._obj_type_to_lower(obj_type)
        cls._registry[obj_type_lower] = obj_class

    @classmethod
    def _obj_type_to_lower(self, obj_type: str):
        if isinstance(obj_type, str):
            return obj_type.lower()
        return obj_type.value.lower()

    @classmethod
    def get_obj(cls, obj_type: str):
        obj_type_lower = cls._obj_type_to_lower(obj_type)

        if not obj_type_lower in cls._registry:
            raise ValueError(
                (CPMException.NOT_REGISTER_FABRIC, obj_type)
            )
        return cls._registry[obj_type_lower]

class BaseFabric:
    

    @staticmethod
    def create_obj(
        obj_type: str, 
        registry: BaseRegistry, 
        /, 
        **kwargs
    ):
        obj = registry.get_obj(obj_type)
        return obj(**kwargs)
