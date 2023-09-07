"""
Process a board in order to create an inventory
All KiCAD coordinate and positions are converter here
No KiCAD is exposed outside of this file
"""
from pathlib import Path
from math import radians, cos, sin
from logging import getLogger

from .utils import Coordinate
from .units import nm, degree
from .pcb_inventory import Inventory

logger = getLogger(__name__)

def append_path():
   import platform
   import sys

   if platform.system() == "Windows":
      try:
         import winreg

         # We need to add KiCad to the path
         location = winreg.HKEY_LOCAL_MACHINE
         key = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KiCad 7.0"
         value = 'InstallLocation'

         kicad_keytype = winreg.OpenKeyEx(location, key)
         path_to_kicad = Path(winreg.QueryValueEx(kicad_keytype, value)[0]).absolute()

         # Create the path to append to sys
         for path in [
            'bin/DLLs', 'bin/Lib', 'bin/Lib/site-packages', 'bin']:
            full_path = path_to_kicad / path

            # Import all from sys.path as Path object for proper compare
            sys_paths = [Path(p).absolute() for p in sys.path]

            if full_path not in sys_paths:
               sys.path.append(str(full_path))

         # OS path needs updating too to locate the _pcbnew.dll
         import os
         os.environ['PATH'] = str(path_to_kicad / "bin") + os.pathsep + os.environ['PATH']
         print("PYTHJPATH", sys.path)
         print("PATH", os.environ['PATH'])
         import pcbnew
      except Exception as exception:
         logger.fatal("Cannot locate KiCad on the system")
         logger.info("Got: {}", exception)
         print(exception)
   else:
      # Python case
      from .constants import THIS_PATH
      import os
      
      kicad = THIS_PATH / "pcbnew"
      os.environ["LD_LIBRARY_PATH"] = str(kicad) + os.pathsep + os.environ.get("LD_LIBRARY_PATH","")
      sys.path.append(str(kicad))

try:
   append_path()
   from pcbnew import LoadBoard, BOARD, PCB_VIA_T, VIATYPE_THROUGH, \
      PAD_ATTRIB_PTH, PAD_ATTRIB_NPTH, PAD_DRILL_SHAPE_CIRCLE, PAD_DRILL_SHAPE_OBLONG
except:
   raise RuntimeError("Failed to import pcbnew")


def tocoord(x, y=None):
   """ @return A traditional coordinate given in Units """
   if y is None:
      return Coordinate(nm(x[0]), nm(-x[1]))
   return Coordinate(nm(x), nm(0-y))
   

class BoardProcessor:
   def __init__(self, pcb_file_path):
      board = LoadBoard(pcb_file_path)

      # Work out the offset
      offset = board.GetDesignSettings().GetAuxOrigin()

      self.inventory = Inventory(tocoord(offset))
      
      # Work out the offset
      self.offset = board.GetDesignSettings().GetAuxOrigin()

      # Start with the pads
      self.process_pads(board.GetPads())
      self.process_vias([t for t in board.GetTracks() if t.Type() == PCB_VIA_T])

   def process_pads(self, pads):
      for pad in pads:
         # Check for pads where drilling or routing is required
         pad_attr = pad.GetAttribute()

         if pad_attr in [PAD_ATTRIB_PTH, PAD_ATTRIB_NPTH]:
            pos = pad.GetPosition()
            coord = tocoord(pos[0], pos[1])
            angle = degree(pad.GetOrientationDegrees())
            size_x = nm(pad.GetDrillSizeX())
            size_y = nm(pad.GetDrillSizeY())
            pth = (pad_attr == PAD_ATTRIB_PTH)

            # Drill or route?
            self.inventory.add_hole(
               coord, size_x, size_y=size_y, angle=angle, pth=pth)

   def process_vias(self, vias):
      for via in vias:
         hole_sz = via.GetDrillValue()

         # Must have a hole!
         if hole_sz == 0:
            continue

         if via.GetViaType() != VIATYPE_THROUGH:
            # We don't support burried vias
            continue

         # Check the via is through - discard other holes
         x, y = via.GetStart()

         self.inventory.add_hole( tocoord(x, y), nm(hole_sz))
