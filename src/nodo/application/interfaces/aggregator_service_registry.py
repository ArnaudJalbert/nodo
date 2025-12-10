"""Aggregator service registry interface."""

from abc import ABC, abstractmethod

from nodo.application.interfaces.aggregator_service import IAggregatorService


class IAggregatorServiceRegistry(ABC):
    """Interface for accessing aggregator services.

    This abstract base class defines the contract for retrieving
    aggregator services by name and listing available aggregators.
    """

    @abstractmethod
    def get_service(self, aggregator_name: str) -> IAggregatorService | None:
        """Get an aggregator service by name.

        Args:
            aggregator_name: The name of the aggregator.

        Returns:
            The aggregator service if found, None otherwise.
        """

    @abstractmethod
    def get_all_names(self) -> list[str]:
        """Get all available aggregator names.

        Returns:
            List of all available aggregator names.
        """
