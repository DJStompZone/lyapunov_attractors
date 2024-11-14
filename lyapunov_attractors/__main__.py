from pathlib import Path

import argparse

from lyapunov_attractors import (
    ChaoticSystemFinder,
    ChaoticSysFinderConfig,
    save_config,
    load_config
)

def main(config_path: Path, animate: bool):
    """
    Main function to load configuration, initialize the chaotic system finder, and start the search process.
    Args:
        config_path (Path): Path to the configuration file.
        animate (bool): Flag to indicate whether to animate the found systems.
    The function performs the following steps:
    1. Loads the configuration from the specified path or creates a default configuration if the file does not exist.
    2. Initializes the ChaoticSystemFinder with the loaded configuration.
    3. Processes the search attempts in 20 batches.
    4. Optionally animates each found system if the animate flag is set to True.
    """
    if config_path.exists():
        print(f"Loading configuration from {config_path}")
        config = load_config(config_path)
    else:
        print(f"No configuration file found at {config_path}. Using default configuration.")
        config = ChaoticSysFinderConfig()
        # Cache config to disk
        save_config(config, config_path)
        print(f"Default configuration saved to {config_path}")
    finder = ChaoticSystemFinder(config)

    # Process attempts in 20 batches
    attempts = config.max_attempts
    per_batch = attempts // 20
    print(f"Starting chaotic system search with 20 batches of {per_batch} attempts...")

    for batch_num in range(20):
        print(f"[ Batch {batch_num + 1} / 20 ]")
        finder.search(num_attempts=per_batch)
    
        # Animate each found system (if we feel like it)
        if animate:
            for idx, system in enumerate(finder.best_systems, 1):
                print(f"Animating system {idx} with Lyapunov exponent {system.lyapunov:.3f}")
                finder.visualizer.animate_system(system, filename=f"attractor_animation_{system.timestamp}.mp4")

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the Chaotic System Finder (and Animator).
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    Command-line arguments:
        -c, --config (Path): Path to the configuration file (default: chaotic_solver_config.json).
        -a, --animate (bool): Enable animation for each found chaotic system.
    """
    parser = argparse.ArgumentParser(description="Chaotic System Finder (and Animator)")
    
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path("chaotic_solver_config.json"),
        help="Path to the configuration file (default: chaotic_solver_config.json)"
    )
    
    parser.add_argument(
        "-a", "--animate",
        action="store_true",
        help="Enable animation for each found chaotic system"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(config_path=args.config, animate=args.animate)
