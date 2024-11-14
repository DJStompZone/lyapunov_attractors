from dataclasses import dataclass
from typing import List

@dataclass
class AttractorSystem:
    """
    A class to represent a dynamical system for generating Lyapunov attractors.

    Attributes:
        dimensions (int): The number of dimensions of the system.
        param_count (int): The number of parameters in the system.
        iterations (int): The number of iterations to run the system.
        coefficients (List[float]): The coefficients used in the system's equations.
        lyapunov (float): The Lyapunov exponent of the system.
        points (List[List[float]]): The points generated by the system.
        timestamp (str): The timestamp when the system was created or last modified.
    """
    dimensions: int
    param_count: int
    iterations: int
    coefficients: List[float]
    lyapunov: float
    points: List[List[float]]
    timestamp: str
