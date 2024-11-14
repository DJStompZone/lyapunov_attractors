import json
from pathlib import Path
from typing import List
from dataclasses import asdict

from lyapunov_attractors.attractor_system import AttractorSystem

class StorageManager:
    """
    StorageManager is responsible for managing the storage of attractor systems.
    It provides methods to load and save attractor systems from/to a JSON file.

    Attributes:
        storage_path (Path): The directory path where the systems file is stored.
        systems_file (Path): The path to the JSON file where attractor systems are saved.

    Methods:
        load_systems() -> List[AttractorSystem]:
            Returns a list of loaded attractor systems. If the file does not exist,
            an empty list is returned. Raises JSONDecodeError if the file contains invalid JSON.

        save_systems(systems: List[AttractorSystem]):
            Saves a list of AttractorSystem objects to a JSON file.
    """
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.systems_file = self.storage_path / "systems.json"

    def load_systems(self) -> List[AttractorSystem]:
        """
        Loads previously saved attractor systems from a JSON file.

        Returns:
            List[AttractorSystem]: A list of loaded attractor systems. If the file does not exist,
                                   an empty list is returned.

        Raises:
            JSONDecodeError: If the file exists but contains invalid JSON.
        """
        best_systems = []
        if self.systems_file.exists():
            with open(self.systems_file, "r", encoding='utf-8') as f:
                systems_data = json.load(f)
                for system_dict in systems_data:
                    best_systems.append(AttractorSystem(**system_dict))
            print(f"Loaded {len(best_systems)} previously saved systems.")
        else:
            print("No saved systems found.")
        return best_systems

    def save_systems(self, systems: List[AttractorSystem]):
        """
        Save a list of AttractorSystem objects to a JSON file.

        Args:
            systems (List[AttractorSystem]): A list of AttractorSystem objects to be saved.

        The systems are serialized to JSON format and written to the file specified by self.systems_file.
        Each AttractorSystem object is converted to a dictionary using the asdict function.
        The JSON file is written with an indentation of 2 spaces for readability.
        """
        with open(self.systems_file, "w", encoding='utf-8') as f:
            json.dump([asdict(system) for system in systems], f, indent=2)
