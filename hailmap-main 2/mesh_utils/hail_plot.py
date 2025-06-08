import matplotlib
matplotlib.use('Agg')  # for headless environments
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from matplotlib import animation
from docx import Document
import os
from process_mesh import load_mesh


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


def save_geotiff(lats, lons, data, path: str):
    """Save data array to GeoTIFF with geographic bounds."""
    transform = from_bounds(float(lons.min()), float(lats.min()),
                            float(lons.max()), float(lats.max()),
                            data.shape[1], data.shape[0])
    with rasterio.open(
        path,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(data, 1)


def make_contour(lats, lons, data, pin: Optional[Tuple[float, float]] = None):
    """Return a Matplotlib figure with contour lines."""
    fig, ax = plt.subplots(figsize=(8, 6))
    cs = ax.contour(lons, lats, data, colors='k')
    ax.clabel(cs, inline=1, fontsize=8)
    if pin:
        ax.plot(pin[1], pin[0], 'ro', markersize=8)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    return fig


def save_animation(files: List[str], path: str, pin: Optional[Tuple[float, float]] = None):
    """Create an animation from a list of MRMS files."""
    frames = []
    for f in files:
        lats, lons, data = load_mesh(f)
        fig = make_figure(lats, lons, data, pin=pin)
        frames.append([plt.imshow(data, animated=True)])
        plt.close(fig)
    fig, ax = plt.subplots()
    ani = animation.ArtistAnimation(fig, frames, interval=500, blit=True)
    ani.save(path)
    plt.close(fig)


def save_docx(fig, path: str):
    """Save figure to DOCX report."""
    tmp_png = path + '.png'
    save_figure(fig, tmp_png)
    doc = Document()
    doc.add_picture(tmp_png)
    doc.save(path)
    os.remove(tmp_png)
