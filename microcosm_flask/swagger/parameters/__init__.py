from functools import lru_cache
from pkg_resources import iter_entry_points
from typing import (
    Any,
    List,
    Mapping,
    Type,
)

from marshmallow.fields import Field

from microcosm_flask.swagger.parameters.base import ParameterBuilder
from microcosm_flask.swagger.parameters.default import DefaultParameterBuilder


ENTRY_POINT = "microcosm_flask.swagger.parameters"


class Parameters:
    """
    Plugin-aware swagger parameter builder.

    Discovers builder subclasses via the `microcosm_flask.swagger.parameters` entry point
    and delegates to the first compatible implementation.

    """
    def __init__(self, strict_enums: bool = True):
        self.strict_enums = strict_enums

    def build(self, field: Field) -> Mapping[str, Any]:
        """
        Build a swagger parameter from a marshmallow field.

        """
        builder_types = self.builder_types() + [
            # put default last
            self.default_builder_type()
        ]

        builders: List[ParameterBuilder] = [
            builder_type(
                build_parameter=self.build,  # type: ignore
                strict_enums=self.strict_enums,
            )
            for builder_type in builder_types
        ]

        builder = next(
            builder
            for builder in builders
            if builder.supports_field(field)
        )

        return builder.build(field)

    @classmethod
    # NB: entry point lookups can be slow; memoize
    @lru_cache()
    def builder_types(cls) -> List[Type[ParameterBuilder]]:
        """
        Define the available builder types.

        """
        return [
            entry_point.load()
            for entry_point in iter_entry_points(ENTRY_POINT)
        ]

    @classmethod
    def default_builder_type(cls) -> Type[ParameterBuilder]:
        """
        Define the default builder type.

        """
        return DefaultParameterBuilder
