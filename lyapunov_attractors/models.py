from collections import namedtuple
import json

# Settings directly relating to Lyapunov calculation
LyapConfig = namedtuple(
    "LyapConfig",
    [
        "transient_skip_steps",
        "initial_distance",
        "renorm_steps",
        "convergence_threshold",
        "extreme_threshold",
        "lyapunov_threshold",
    ],
    defaults=[100, 1e-8, 10, 1e-10, 1e10, 0.05],
)

# Tbh I expected to add more to this one
# And now I don't feel like refactoring it
DensityConstraints = namedtuple("DensityConstraints", ["MIN", "MAX"], defaults=[-5, 5])

# Primary config container for the project
ChaoticSysFinderConfig = namedtuple(
    "ChaoticSysFinderConfig",
    [
        "dimensions",
        "param_count",
        "iterations",
        "max_systems",
        "coefficient_limit",
        "max_attempts",
        "output_path",
        "density_constraints",
        "lyap_config",
    ],
    defaults=[
        3,
        12,
        2000,
        10,
        2.5,
        9000,
        "./best_attractors",
        DensityConstraints(),
        LyapConfig(),
    ],
)


# Utility functions to save and load configurations
def save_config(config: ChaoticSysFinderConfig, filepath: str):
    """Save the configuration to a JSON file."""
    config_dict = config._asdict()
    # Can't forget the younglings
    config_dict["density_constraints"] = config.density_constraints._asdict()
    config_dict["lyap_config"] = config.lyap_config._asdict()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)


def load_config(filepath: str) -> ChaoticSysFinderConfig:
    """Load configuration from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        config_dict = json.load(f)
    # Instant namedtuples, just add water
    density_constraints = DensityConstraints(**config_dict["density_constraints"])
    lyap_config = LyapConfig(**config_dict["lyap_config"])
    return ChaoticSysFinderConfig(
        dimensions=config_dict["dimensions"],
        param_count=config_dict["param_count"],
        iterations=config_dict["iterations"],
        max_systems=config_dict["max_systems"],
        coefficient_limit=config_dict["coefficient_limit"],
        max_attempts=config_dict["max_attempts"],
        output_path=config_dict["output_path"],
        density_constraints=density_constraints,
        lyap_config=lyap_config,
    )
