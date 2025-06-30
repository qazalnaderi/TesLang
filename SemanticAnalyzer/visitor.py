from abc import ABC, abstractmethod


class Visitor(ABC):
    """Abstract base class for visitor pattern"""
    
    @abstractmethod
    def visit(self, node):
        pass
