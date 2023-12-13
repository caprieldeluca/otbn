# -*- coding: utf-8 -*-
"""
************************************************************************
    Name                : remove_spykes.py
    Date                : October 2023
    Copyright           : (C) 2023 by Gabriel De Luca
    Email               : caprieldeluca@gmail.com
************************************************************************
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
************************************************************************
"""

import math
import numpy as np


def _get_angle_at_point(
                    prev_point,
                    curr_point,
                    next_point):
    """Compute the angle at current point given previous and next ones."""

    # Create two vectors, from current to previous and next points
    v1 = np.array([
            prev_point.x() - curr_point.x(),
            prev_point.y() - curr_point.y()])

    v2 = np.array([
            next_point.x() - curr_point.x(),
            next_point.y() - curr_point.y()])

    # Create unit vectors
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)

    # Compute the angle
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    return angle


def run(geom, threshold):
    """Delete vertices if angle is less than threshold degrees."""

    # Count of deleted vertices
    n = 0

    for i, _ in enumerate(geom.vertices()):
        iprev, inext = geom.adjacentVertices(i)
        prev_point = geom.vertexAt(iprev)
        curr_point = geom.vertexAt(i)
        next_point = geom.vertexAt(inext)

        angle = _get_angle_at_point(
                                prev_point,
                                curr_point,
                                next_point)

        angle_degrees = math.degrees(angle)

        if angle_degrees < threshold:
            geom.deleteVertex(i)
            n += 1

    return geom, n
