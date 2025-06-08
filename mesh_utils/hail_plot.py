import matplotlib
matplotlib.use('Agg')  # for headless environments
import matplotlib.pyplot as plt
from typing import Optional, Tuple


def make_figure(lats, lons, data, pin: Optional[Tuple[float, float]] = None):
    """Return a Matplotlib figure showing the hail swath."""
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(lons, lats, data, cmap='turbo', shading='auto')
    fig.colorbar(mesh, ax=ax, label='MESH (inches)')
    if pin:
        ax.plot(pin[1], pin[0], 'ro', markersize=8)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    return fig


def save_figure(fig, path: str):
    fig.savefig(path, bbox_inches='tight')
