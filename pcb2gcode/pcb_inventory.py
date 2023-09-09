# -*- coding: utf-8 -*-

#
# This file is part of the pcb2gcode distribution (https://github.com/adarwoo/pcb2gcode).
# Copyright (c) 2023 Guillaume ARRECKX (software@arreckx.com).
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Creates an abstract inventory for the PCB.
"""
from typing import Dict
from collections import OrderedDict
from math import radians, cos, sin, sqrt

from .units import um, degree, Length
from .coordinate import Coordinate
from .operations import Operations


class Feature:
    """ Abstract base class feature of the inventory """
    @classmethod
    @property
    def type(cls):
        return cls


class Hole(Feature):
    """
    Representation of a Hole information collected from KiCAD
    All dimensions shall be given as Length objects
    """
    def __init__(self, diameter, coord):
        self.coord = coord
        self.diameter = diameter

        # To be added by the machining
        self.tool_id = 0

    def __repr__(self) -> str:
        return str(self)

    def __str__(self):
        return f"{self.diameter} ({self.coord.x}, {self.coord.y})"


class Oblong(Hole):
    """ Representation of a oblong hole """
    def __init__(self, slitwidth, start, end):
        super().__init__(slitwidth, start)
        self.end = end

        # The distance is used to determine if 2 holes are required / and / or routing is required
        self.distance = \
            sqrt((self.coord.x-self.end.x)(um)**2 + (self.coord.y-self.end.y)(um)**2) * um

    def __str__(self):
        return "O" + super().__str__()


class Route(Feature):
    pass


class Inventory:
    """
    Create an inventory of Features which will require some machine.
    The inventory is created from the PCB data and does not factor how it will be machined
    """
    def __init__(self, offset):
        self.pth: Dict[Length, Feature] = OrderedDict()
        self.npth: Dict[Length, Feature] = OrderedDict()
        self.offset = offset

    def _add_hole(self, hole: Hole, pth):
        if pth:
            self.pth.setdefault(hole.diameter, []).append(hole)
        else:
            self.npth.setdefault(hole.diameter, []).append(hole)
            
    def get_features(self, ops: Operations):
        """ @returns All feature of the pcb for the given operations """
        retval = {}
        
        if ops & Operations.PTH:
            retval.update(self.pth)
            
        if ops & Operations.NPTH:
            retval.update(self.npth)

        return retval

    def add_hole(self, coord, size_x, **kwargs):
        """
        Add a hole to the inventory

        @param pos_x, pos_y Position of the hole in KiCad coordinate values
        @param size_x, size_y Size of the hole. Oblong hole have different sizes
        @param orient Orientation of the hole
        @param kwargs:
            size_y: Oblong hole
            angle: Same, orientation as an Angle
            pth: If false, hole is npth (default is pth)
        """
        size_y = kwargs.get("size_y", None)
        angle = kwargs.get("angle", 0*degree)
        pth = kwargs.get("pth", True)
        
        if size_y is None or size_x == size_y:
            hole = Hole(size_x, coord)
            self._add_hole(hole, pth)
        else:
            # Determine the orientation
            # WARNING : As KiCad uses screen coordinates, angles are inverted
            hole_width = min(size_x, size_y)
            radius = (max(size_x, size_y) - hole_width) / 2
            angle = radians((90 if size_x < size_y else 0) - angle(degree))
            dx = radius * cos(angle)
            dy = radius * sin(angle)
            start = Coordinate(coord.x + dx, coord.y + dy)
            end = Coordinate(coord.x - dx, coord.y - dy)

            # Append an oblong hole
            self._add_hole(Oblong(hole_width, start, end), pth)
