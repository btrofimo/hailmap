#!/usr/bin/env python3
"""Simple command-line interface for MESH-MAP."""
import argparse
from typing import List
import os

from process_mesh import load_mesh
from mesh_utils import (
    make_figure,
    save_figure,
    save_overlay,
    save_geotiff,
    make_contour,
    save_animation,
    save_docx,
)


def cmd_plot(args: argparse.Namespace) -> None:
    lats, lons, data = load_mesh(args.input)
    fig = make_figure(lats, lons, data)
    if args.png:
        save_figure(fig, args.png)
    if args.geotiff:
        save_geotiff(lats, lons, data, args.geotiff)
    if args.docx:
        save_docx(fig, args.docx)


def cmd_contour(args: argparse.Namespace) -> None:
    lats, lons, data = load_mesh(args.input)
    fig = make_contour(lats, lons, data)
    save_figure(fig, args.output)


def cmd_animate(args: argparse.Namespace) -> None:
    save_animation(args.inputs, args.output)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MESH-MAP CLI")
    sub = p.add_subparsers(dest="cmd")

    plot_p = sub.add_parser("plot", help="Plot single file")
    plot_p.add_argument("input")
    plot_p.add_argument("--png")
    plot_p.add_argument("--geotiff")
    plot_p.add_argument("--docx")
    plot_p.set_defaults(func=cmd_plot)

    contour_p = sub.add_parser("contour", help="Generate contour map")
    contour_p.add_argument("input")
    contour_p.add_argument("output")
    contour_p.set_defaults(func=cmd_contour)

    anim_p = sub.add_parser("animate", help="Animate multiple files")
    anim_p.add_argument("output")
    anim_p.add_argument("inputs", nargs="+")
    anim_p.set_defaults(func=cmd_animate)

    return p


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
