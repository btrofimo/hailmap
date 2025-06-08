import matplotlib
matplotlib.use('Agg')  # for headless environments
import matplotlib.pyplot as plt
from typing import Optional, Tuple
import numpy as np


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


def save_overlay(lats, lons, data, path: str):
    """Save transparent image for use as map overlay."""
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(lons, lats, data, cmap='turbo', shading='auto')
    ax.axis('off')
    ax.set_xlim(np.min(lons), np.max(lons))
    ax.set_ylim(np.min(lats), np.max(lats))
    fig.savefig(path, transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
