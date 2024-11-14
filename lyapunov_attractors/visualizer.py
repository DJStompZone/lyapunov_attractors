from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lyapunov_attractors.attractor_system import AttractorSystem


class Visualizer:
    """
    Visualizer class for plotting and animating attractor systems.

    Attributes:
        storage_path (Path): The path where plots and animations will be saved.

    Methods:
        __init__(storage_path: Path):
            Initializes the Visualizer with a specified storage path.

        plot_system(system: AttractorSystem):
            Saves the plot as a PNG file in the specified storage path.
            If the system has fewer than 3 dimensions, it prints a message indicating that plotting is only implemented for 3D systems.

        animate_system(system: AttractorSystem, filename: str = "attractor_animation.mp4", fps: int = 30):
            Creates and saves an animation of the system's trajectory.
            If the system has fewer than 3 dimensions, it prints a message indicating that animation is only implemented for 3D systems.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def plot_system(self, system: AttractorSystem):
        """
        Plots the attractor system in 3D if the system has 3 or more dimensions.

        Parameters:
        system (AttractorSystem): The attractor system to be plotted. It should have a 'points' attribute
                                  which is a list or array of points in the system, a 'dimensions' attribute
                                  indicating the number of dimensions, a 'lyapunov' attribute representing
                                  the Lyapunov exponent, and a 'timestamp' attribute for the filename.

        Returns:
        None

        Saves the plot as a PNG file in the specified storage path if the system has 3 or more dimensions.
        If the system has fewer than 3 dimensions, it prints a message indicating that plotting is only
        implemented for 3D systems.
        """
        points_array = np.array(system.points)

        titleName = (
            f'{system.dimensions}D: {system.coefficients[0:system.dimensions]}'
            + f'\nInitPos: {system.points[0]}' +
            f'\nLyapunov: {system.lyapunov:.3f}' +
            f'\nTime: {datetime.strptime(system.timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")}'
        )

        if system.dimensions >= 3:
            fig = plt.figure(figsize=(10, 8))
            ax3d = fig.add_subplot(111, projection='3d')
            scatter = ax3d.scatter(points_array[:, 0],
                                   points_array[:, 1],
                                   points_array[:, 2],
                                   c=np.arange(len(points_array)),
                                   cmap='viridis',
                                   alpha=0.6)

            ax3d.set_xlabel(
                f'X \n[{min(points_array[:, 0]):.2f}, {max(points_array[:, 0]):.2f}]'
            )
            ax3d.set_ylabel(
                f'Y \n[{min(points_array[:, 1]):.2f}, {max(points_array[:, 1]):.2f}]'
            )
            ax3d.set_zlabel(
                f'Z \n[{min(points_array[:, 2]):.2f}, {max(points_array[:, 2]):.2f}]'
            )
            ax3d.set_title(titleName)

            plt.colorbar(scatter,
                         label='Time Evolution',
                         orientation='horizontal')

            plt.tight_layout()
            plot_path = self.storage_path / f"attractor_{system.timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
        elif system.dimensions == 2:
            fig, ax = plt.subplots(figsize=(10, 10))
            scatter = ax.scatter(points_array[:, 0],
                                 points_array[:, 1],
                                 c=np.arange(len(points_array)),
                                 cmap='viridis',
                                 alpha=0.6)

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title(titleName)

            plt.colorbar(scatter,
                         label='Time Evolution',
                         orientation='horizontal')

            plt.tight_layout()
            plot_path = self.storage_path / f"attractor_{system.timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("Plotting is only implemented for above 2D systems.")

    def animate_system(self,
                       system: AttractorSystem,
                       filename: str = "attractor_animation.mp4",
                       fps: int = 30):
        """Create and save an animation of the system's trajectory."""
        points_array = np.array(system.points)
        sample_rate = 10  # Controls frame quantity
        points_array = points_array[::sample_rate]

        if system.dimensions >= 3:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(
                f'3D Chaotic Attractor\nLyapunov Exponent: {system.lyapunov:.3f}'
            )

            # store trajectory
            line, = ax.plot([], [], [], lw=0.5)

            # Get a good seat
            ax.view_init(elev=30, azim=45)

            def update(num):
                line.set_data(points_array[:num, 0], points_array[:num, 1])
                line.set_3d_properties(points_array[:num, 2])
                return line,

            ani = FuncAnimation(fig,
                                update,
                                frames=len(points_array),
                                blit=True,
                                interval=20)

            anim_path = self.storage_path / filename
            ani.save(anim_path, writer='ffmpeg', fps=fps)

            plt.show()
        else:
            print("Animation is only implemented for 3D systems.")
