import os
from datetime import datetime
from typing import List
from pathlib import Path

from colorama import Fore, Back, Style

from lyapunov_attractors.attractor_system import AttractorSystem
from lyapunov_attractors.storage_manager import StorageManager
from lyapunov_attractors.lyapunov_calculator import LyapunovCalculator
from lyapunov_attractors.trajectory_simulator import TrajectorySimulator
from lyapunov_attractors.visualizer import Visualizer
from lyapunov_attractors.models import ChaoticSysFinderConfig, LyapConfig


class ChaoticSystemFinder:
    """
    A class to find and store chaotic systems based on their Lyapunov exponents.

    Attributes:
        config (ChaoticSysFinderConfig): Configuration for the chaotic system finder.
        storage_manager (StorageManager): Manages storage of the best attractor systems.
        lyap_calculator (LyapunovCalculator): Calculates the Lyapunov exponent.
        simulator (TrajectorySimulator): Simulates the trajectory of systems.
        visualizer (Visualizer): Visualizes the attractor systems.
        best_systems (List[AttractorSystem]): List of the best attractor systems found.

    Methods:
        is_system_worthy(lyapunov: float) -> bool:
            Determines if a system is worthy of being stored based on its Lyapunov exponent.

        add_system(coefficients: List[float], lyapunov: float, points: List[List[float]]):
            Adds a new system to the list of best systems if it meets the criteria.

        search(num_attempts: int = None):
            Searches for chaotic systems by simulating trajectories and evaluating their Lyapunov exponents.
    """

    def __init__(self, config: ChaoticSysFinderConfig | None = None):
        self.config = config or ChaoticSysFinderConfig()
        self.lyap_config: LyapConfig = self.config.lyap_config
        self.storage_manager = StorageManager(self.config.output_path)
        self.lyap_calculator = LyapunovCalculator(self.config.lyap_config)
        self.simulator = TrajectorySimulator(config, self.lyap_calculator)
        self.visualizer = Visualizer(Path("./best_attractors"))
        self.best_systems: List[
            AttractorSystem] = self.storage_manager.load_systems()

    def is_system_worthy(self, lyapunov: float) -> bool:
        """
        Determines if a system is worthy based on its Lyapunov exponent. (And warrior spirit)

        Args:
            lyapunov (float): The Lyapunov exponent of the system.

        Returns:
            bool: True if the system is worthy, False otherwise.
        """
        if lyapunov < self.lyap_config.lyapunov_threshold:
            return False
        if len(self.best_systems) < self.config.max_systems:
            return True
        return lyapunov > min(system.lyapunov for system in self.best_systems)

    def add_system(self, coefficients: List[float], lyapunov: float,
                   points: List[List[float]]):
        """
        Adds a new attractor system to the list of best systems if it meets the criteria.

        Args:
            coefficients (List[float]): The coefficients of the system.
            lyapunov (float): The Lyapunov exponent of the system.
            points (List[List[float]]): The points representing the system's trajectory.

        Returns:
            None
        """
        if not self.is_system_worthy(lyapunov):
            return

        new_system = AttractorSystem(
            dimensions=self.config.dimensions,
            param_count=self.config.param_count,
            iterations=self.config.iterations,
            coefficients=coefficients,
            lyapunov=lyapunov,
            points=points,
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"))

        self.best_systems.append(new_system)
        self.best_systems.sort(key=lambda x: x.lyapunov, reverse=True)

        if len(self.best_systems) > self.config.max_systems:
            self.best_systems.pop()

        self.storage_manager.save_systems(self.best_systems)
        self.visualizer.plot_system(new_system)

    def search(self, num_attempts: int = None):
        """
        Searches for chaotic systems with a Lyapunov exponent greater than or equal to the minimum specified in the configuration.

        Args:
            num_attempts (int, optional): The number of attempts to search for chaotic systems. If not provided, the default value from the configuration is used.

        Prints:
            Progress of the search attempts and details of any found systems with a Lyapunov exponent meeting the criteria.
        """
        if num_attempts is None:
            num_attempts = self.config.max_attempts

        print(
            f"Searching for chaotic systems with Lyapunov exponent >= {self.lyap_config.lyapunov_threshold}"
        )
        print(f"Currently stored systems: {len(self.best_systems)}")

        for attempt in range(num_attempts):
            print(f"\r{Fore.MAGENTA}{Back.YELLOW}" +
                  f"Attempt {attempt + 1}/{num_attempts}" +
                  f"{Fore.RESET}{Back.RESET}",
                  end="")

            lyapunov, coefficients, points = self.simulator.simulate()

            if lyapunov > self.lyap_config.lyapunov_threshold:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(
                    f"{Fore.LIGHTYELLOW_EX}" +
                    f"Found system with Lyapunov exponent: {lyapunov:.3f}" +
                    f"{Fore.RESET} ({self.config.dimensions}D, {self.config.param_count} params)"
                )
                self.add_system(coefficients, lyapunov, points)

                print("Current best systems:")
                for idx, system in enumerate(self.best_systems, 1):
                    print(
                        f"{idx}. " +
                        f"{Fore.LIGHTYELLOW_EX}Lyapunov: {system.lyapunov:.3f}{Fore.RESET} "
                        +
                        f"(found: {Fore.CYAN}{system.timestamp}{Fore.RESET})\n"
                        +
                        f'{Fore.RED}C   {system.coefficients[0:system.param_count]}{Fore.RESET}\n'
                        + f'{Fore.BLUE}Vx  {system.points[0]}{Fore.RESET}\n')
