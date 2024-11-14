import random
import math
import itertools
from typing import List, Tuple

from lyapunov_attractors.models import ChaoticSysFinderConfig, DensityConstraints, LyapConfig

class TrajectorySimulator:
    """
    A class to simulate trajectories for Lyapunov attractors.

    Attributes:
        dimensions (int): Number of dimensions for the simulation.
        iterations (int): Number of iterations to run the simulation.
        PARAM_MAX (float): Maximum value for polynomial coefficients.
        DENSITY_MIN (float): Minimum density constraint.
        DENSITY_MAX (float): Maximum density constraint.
        convergence_threshold (float): Threshold for convergence.
        extreme_threshold (float): Threshold for extreme values.
        lyap_norm_dist (float): Normalization distance for Lyapunov separation.
        lyap_renorm_steps (int): Steps interval for renormalizing the separation.

    Methods:
        create_random_points() -> Tuple[List[float], List[float]]:
            Creates a random point and a perturbed point with initial separation.

        generate_polynomial_coefficients() -> List[float]:
            Generates random polynomial coefficients for the simulation.

        compute_polynomial_terms(point: List[float], dim_coeffs: List[float]) -> float:
            Computes the polynomial terms for a given point and dimension coefficients.

        normalize_point(point: List[float]) -> List[float]:
            Normalizes a point to ensure it does not exceed the maximum density.

        check_convergence(point: List[float]) -> bool:
            Checks if a point has converged based on the magnitude.

        simulate() -> Tuple[float, List[float], List[List[float]]]:
            Runs the trajectory simulation and returns the Lyapunov exponent, coefficients, and reference trajectory.

        calculate_new_point(point: List[float], coefficients: List[float]) -> List[float]:
            Calculates a new point based on the current point and polynomial coefficients.
    """
    def __init__(self, config: ChaoticSysFinderConfig):
        self.config = config
        self.density_constraints: DensityConstraints = config.density_constraints
        self.lyap_config: LyapConfig = config.lyap_config
        self.dimensions = config.dimensions
        self.iterations = config.iterations
        self.param_max = config.max_systems
        self.min_density = self.density_constraints.MIN
        self.max_density = self.density_constraints.MAX
        self.convergence_threshold = self.lyap_config.convergence_threshold
        self.extreme_threshold = self.lyap_config.extreme_threshold
        self.lyap_norm_dist = self.lyap_config.initial_distance
        self.lyap_renorm_steps = self.lyap_config.renorm_steps

    def create_random_points(self) -> Tuple[List[float], List[float]]:
        """
        Generate a random point and a perturbed point with a specified initial separation.

        This method creates a random point within the defined density range and then
        generates a second point that is perturbed from the first point by a fixed
        distance in a random direction.

        Returns:
            Tuple[List[float], List[float]]: A tuple containing the original random point
            and the perturbed point.
        """
        point = [
            random.uniform(self.min_density / 2, self.max_density / 2)
            for _ in range(self.dimensions)
        ]

        # Create perturbed point with exact initial separation
        random_direction = [random.uniform(-1, 1) for _ in range(self.dimensions)]
        magnitude = math.sqrt(sum(x * x for x in random_direction))
        perturbed = [
            p + (d * self.lyap_norm_dist / magnitude)
            for p, d in zip(point, random_direction)
        ]

        return point, perturbed

    def generate_polynomial_coefficients(self) -> List[float]:
        """
        Generates a list of polynomial coefficients for a given number of dimensions.

        The number of coefficients per dimension is calculated as:
        1 + dimensions + (dimensions * (dimensions + 1)) // 2

        The total number of parameters is then:
        coeffs_per_dim * dimensions

        Each coefficient is a random float uniformly distributed between 
        -PARAM_MAX / 2 and PARAM_MAX / 2.

        Returns:
            List[float]: A list of randomly generated polynomial coefficients.
        """
        coeffs_per_dim = 1 + self.dimensions + (self.dimensions * (self.dimensions + 1)) // 2
        total_params = coeffs_per_dim * self.dimensions
        return [
            random.uniform(-self.param_max / 2, self.param_max / 2)
            for _ in range(total_params)
        ]

    def compute_polynomial_terms(self, point: List[float], dim_coeffs: List[float]) -> float:
        """
        Computes the polynomial terms for a given point using the provided dimension coefficients.

        This function calculates a polynomial value based on the given point and dimension coefficients.
        It includes constant, linear, and quadratic terms.

        Args:
            point (List[float]): A list of float values representing the coordinates of the point.
            dim_coeffs (List[float]): A list of float values representing the coefficients for the polynomial terms.

        Returns:
            float: The computed polynomial value. If an OverflowError occurs, returns float('inf').

        Raises:
            OverflowError: If the computation results in a value too large to be represented.
        """
        try:
            current_idx = 0
            result = 0.0

            # Constant term
            result += dim_coeffs[current_idx] * 0.1
            current_idx += 1

            # Linear terms
            for i in range(self.dimensions):
                if current_idx < len(dim_coeffs):
                    result += dim_coeffs[current_idx] * point[i] * 0.5
                    current_idx += 1

            # Quadratic terms
            for i, j in itertools.combinations_with_replacement(range(self.dimensions), 2):
                if current_idx < len(dim_coeffs):
                    result += dim_coeffs[current_idx] * point[i] * point[j] * 0.25
                    current_idx += 1

            return result
        except OverflowError:
            return float('inf') # Oopsiepoopsie, terms 2 stronk

    def normalize_point(self, point: List[float]) -> List[float]:
        """
        Normalize a point to ensure its magnitude does not exceed a specified maximum density.

        Args:
            point (List[float]): A list of float values representing the coordinates of the point.

        Returns:
            List[float]: A list of float values representing the normalized coordinates of the point.
        """
        magnitude = math.sqrt(sum(x * x for x in point))
        if magnitude > self.max_density:
            return [x * self.max_density / magnitude for x in point]
        return point

    def check_convergence(self, point: List[float]) -> bool:
        """
        Check if a given point has converged or diverged based on its magnitude.

        Args:
            point (List[float]): A list of float values representing the coordinates of the point.

        Returns:
            bool: True if the magnitude of the point is greater than the extreme threshold 
                  or less than the convergence threshold, indicating divergence or convergence, 
                  respectively. False otherwise.
        """
        magnitude = math.sqrt(sum(x * x for x in point))
        return magnitude > self.extreme_threshold or magnitude < self.convergence_threshold

    def simulate(self) -> Tuple[float, List[float], List[List[float]]]:
        """
        Simulates the trajectory of a point and its perturbed counterpart over a number of iterations.

        Returns:
            Tuple[float, List[float], List[List[float]]]: A tuple containing:
                - A float representing the Lyapunov exponent (returns -inf if convergence is detected).
                - A list of polynomial coefficients used in the simulation.
                - A list of lists representing the reference trajectory points.
        """
        point, perturbed = self.create_random_points()
        coefficients = self.generate_polynomial_coefficients()
        reference_traj = []
        perturbed_traj = []

        for iteration in range(self.iterations):
            # Update reference trajectory
            new_point = self.calculate_new_point(point, coefficients)
            if self.check_convergence(new_point):
                return float('-inf'), coefficients, reference_traj
            point = new_point
            reference_traj.append(point)

            # Update perturbed trajectory
            new_perturbed = self.calculate_new_point(perturbed, coefficients)
            if self.check_convergence(new_perturbed):
                return float('-inf'), coefficients, reference_traj

            # Periodically renormalize the separation
            if iteration % self.lyap_renorm_steps == 0 and iteration > 0:
                # Calculate current separation vector
                separation = [p - r for p, r in zip(new_perturbed, new_point)]
                separation_dist = math.sqrt(sum(x * x for x in separation))

                if separation_dist > 0:
                    # Renormalize to initial separation distance
                    scale = self.lyap_norm_dist / separation_dist
                    new_perturbed = [
                        r + s * scale for r, s in zip(new_point, separation)
                    ]

            perturbed = new_perturbed
            perturbed_traj.append(perturbed)

        return float('-inf'), coefficients, reference_traj

    def calculate_new_point(self, point: List[float], coefficients: List[float]) -> List[float]:
        """
        Calculate a new point in the trajectory based on the given point and coefficients.

        Args:
            point (List[float]): The current point in the trajectory, represented as a list of floats.
            coefficients (List[float]): The coefficients used to compute the new point, represented as a list of floats.

        Returns:
            List[float]: The new point in the trajectory, normalized and represented as a list of floats.
        """
        new_point = []
        coeffs_per_dim = len(coefficients) // self.dimensions

        for dim in range(self.dimensions):
            start_idx = dim * coeffs_per_dim
            dim_coeffs = coefficients[start_idx:start_idx + coeffs_per_dim]
            new_coord = self.compute_polynomial_terms(point, dim_coeffs)
            new_point.append(new_coord)

        return self.normalize_point(new_point)
