import math
from typing import List

from lyapunov_attractors.models import LyapConfig

class LyapunovCalculator:
    """
    A class to calculate the Lyapunov exponent for a given set of trajectories.

    Attributes:
        lyap_skip_steps (int): Number of initial steps to skip in the calculation.
        lyap_norm_dist (float): Normalization distance for the separation of trajectories.
        lyap_renorm_steps (int): Number of steps between renormalizations.
        extreme_threshold (float): Threshold for extreme separation values.

    Methods:
        calculate(reference_traj: List[List[float]], perturbed_traj: List[List[float]]) -> float:
            Calculates the Lyapunov exponent based on the reference and perturbed trajectories.
    """
    def __init__(self, lyap_config: LyapConfig):
        """
        Initializes the LyapunovCalculator with the given configuration.

        Args:
            lyap_config (LyapConfig): Configuration object containing parameters for the calculation.
        """
        self.lyap_skip_steps = lyap_config.transient_skip_steps
        self.lyap_norm_dist = lyap_config.initial_distance
        self.lyap_renorm_steps = lyap_config.renorm_steps
        self.extreme_threshold = lyap_config.extreme_threshold

    def calculate(self, reference_traj: List[List[float]], perturbed_traj: List[List[float]]) -> float:
        """
        Calculates the Lyapunov exponent based on the reference and perturbed trajectories.

        Args:
            reference_traj (List[List[float]]): The reference trajectory points.
            perturbed_traj (List[List[float]]): The perturbed trajectory points.

        Returns:
            float: The calculated Lyapunov exponent. Returns negative infinity if no valid points are found.
        """
        lyap_sum = 0.0
        num_points = len(reference_traj)
        valid_points = 0

        # Skip the wibbly bits
        start_idx = min(self.lyap_skip_steps, num_points // 4)

        for i in range(start_idx, num_points):
            ref_point = reference_traj[i]
            pert_point = perturbed_traj[i]

            # Check rms distance
            separation = math.sqrt(
                sum((r - p) ** 2 for r, p in zip(ref_point, pert_point))
            )

            if separation > 0 and separation < self.extreme_threshold:
                lyap_sum += math.log(separation / self.lyap_norm_dist)
                valid_points += 1

        if valid_points == 0:
            return float('-inf')

        # Calculate average over valid points and normalize by timestep
        return lyap_sum / (valid_points * self.lyap_renorm_steps)
