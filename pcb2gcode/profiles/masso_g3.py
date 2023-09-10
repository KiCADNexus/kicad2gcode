from time import strftime

from pcb2gcode.cutting_tools import CutDir
from pcb2gcode.units import Length, FeedRate, Rpm, mm, mm_min, rpm


def header(filename):
    """
    Called to create the header of the gcode file
    @param filename Name of the PCB file
    """
    yield f"""
        (Created by pcb2gcode from '{filename}' - {strftime("%Y-%m-%d %H:%M:%S")})
        (Reset all back to safe defaults)
        G17 G54 G40 G49 G80 G90
        G21
    """

def footer():
    yield f"""(end of file)
    """


def route_hole(
    size: Length, x: Length, y: Length, d: Length, cutdir: CutDir,
    feedrate: FeedRate, z_feedrate: FeedRate, z_safe: Length, z_bottom: Length):
    """
    Called to generate the GCode for cutting a hole with a router bit
    Note: When you route the hole in a clockwise direction (viewed from above)
     with an upcut bit, it tends to pull the chips up and out of the hole.
    This results in a cleaner top surface at the expense of the bottom - which
    should not happen if the backboard does its job
    Note: Z0 is set to the machine bed, that is the bottom of the backing board
           Doing so, allow zero setup of the Z0, and the board thickness information
           is not required

    Variables are:
        size:       Diameter of the hole as a length. Convert appropriatly
        x, y:       Center location of the hole as lengths
        d:          Diameter of the cutter
        cutdir:     Up of down or updown cutter type
        feedrate:   Lateral displacement feedrate
        z_feedrate: Z feedrate
        z_safe:     Z to retract to
        z_bottom:   Depth to go to

    Yields:
        The g-code text
    """
    id = (size - d) / 2

    # Go straight down in the center
    yield f"""G0 {x(mm)} {y(mm)}
    G1 Z{z_bottom(mm)} F{z_feedrate(mm_min)}
    G1 Y{(y+id)(mm)}
    """

    if cutdir in [CutDir.UP, CutDir.UPDOWN]:
        yield f"""G2 X{(x+id)(mm)} Y{y(mm)} I0 J-{id(mm)}
        G2 X{x(mm)} Y{(y-id)(mm)} I-{id(mm)} J0
        G2 X{(x+id)(mm)} Y{y(mm)} I0 J+{id(mm)}
        G2 X{x(mm)} Y{(y+id)(mm)} I+{id(mm)} J0
        """
    else:
        yield "G3"


def drill_hole(
    x: Length, y: Length,
    z_feedrate: FeedRate,
    z_safe:Length, z_bottom:Length,
    index, last_index):

    if index == 0:
        yield f"""G81 X{x(mm)} Y{y(mm)} Z{z_bottom(mm)} R{z_safe(mm)} F{z_feedrate(mm_min)}
        """
    else:
        yield f"""X{x(mm)} Y{y(mm)}
        """

    if last_index == index:
        yield """G80
        """


def change_tool(tool: int, speed: Rpm, type, diameter, atc):
    """
    GCode for tool change.
      Variables are:
        tool:     holds the tool number
        rpm:      Required spindle speed
        type:     Type of tool
        diameter: Diameter of the tool
        atc:      True if tool change is automatic

    """
    msg = f"\nLoad {type} Dia={diameter}" if atc else ""

    yield f"""T{tool}
        M06{msg}
        S{speed()}
    """
