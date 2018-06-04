#!/usr/bin/env python
from __future__ import (
    absolute_import,
    print_function,
)
import sys
import tempfile
import traceback

import numpy as np

from IPython.core.magic import register_line_cell_magic
from IPython.display import (
    display,
    clear_output,
)
from .sigplot import SigPlot

try:
    from XMinter import (
        xm as _xm,
        res
    )
except ImportError:
    _xm = None
    res = None

try:
    import bluefile
except ImportError:
    bluefile = None


@register_line_cell_magic
def xm(line, cell=None):
    """Handle `xm` command

    Along with the provided XMPY patch, this will enable stdout/stderr from
    XMIDAS commands to be passed back and displayed in the notebook.

    :param line: the arguments passed with the %-magic command
    :type line: str

    :param cell: The entire newline-delimited cell (default: None)
    :type cell: str

    :Example:
    >>> %xm expl sincos
    SINCOSINE - creates sinusoidal data files

    <sin file>    Output file name for real sine wave file (optional)
    <cos file>    Output file name for real cosine wave file (optional)
    <amplitude>       Amplitude of sinusoidal data
    <frequency>       Frequency in Hz of wave
    <starting phase>  Phase of the first point in the file degrees
    <# elements>      Logical size of data file to create
    <start time>      Start time of output data (does not affect output data)
    <time delta>      Time delta between data elements of output data
    <cx exponential file>   Output file name for complex data (optional)
    ...
    """
    if cell is not None:
        lines = cell.split('\n')
    else:
        lines = [line]

    with tempfile.TemporaryFile(mode='w+t') as output:
        for line in lines:
            args = line.split()
            if not args:
                output.write("Available commands: xplot, xraster, ...\n")
            else:
                # TODO: Handle parsing args and switches
                # TODO: Translating all of the XPLOT/XRASTER switches to SigPlot constructor options
                cmd = args[0].strip().lower()
                fname = None
                if len(args) > 1:
                    fname = args[1].strip()

                if cmd in ("xplot", "xraster"):
                    if fname is None:
                        raise ValueError("Must provide file to %s -- e.g., %s foo.tmp" % (cmd, cmd))
                    
                    plot = SigPlot()
                    display(plot)
                    if cmd == "xplot":
                        plot.overlay_href(fname, layer_type="1D")
                    elif cmd == "xraster":
                        plot.overlay_href(fname, layer_type="2D")
                else:
                    try:
                        _xm(line, xmstdout=output, xmstderr=output)
                    except Exception:
                        tb = traceback.format_exc()
                        output.write(str(tb) + '\n')
        output.seek(0)
        sys.stdout.write(output.read())


@register_line_cell_magic
def xplot():
    plot1 = SigPlot()
    plot1.overlay_href("http://sigplot.lgsinnovations.com/dat/penny.prm")
    plot1.plot()


@register_line_cell_magic
def xraster(data, **kwargs):
    """Wrapper around SigPlot for 2-D plotting

    Currently supports plotting Python lists, Python tuples, numpy arrays,
    HTTP/HTTPS-prefixed files, and local files.

    :param data: A heterogeneous list of files and/or data lists
    :type data: List[Union[str, numpy.ndarray, List, Tuple]]

    :param \**kwargs: See below.
    :type \**kwargs: Dict[str]

    :Keyword Arguments:
        * *subsize* (``int``) -- number of elements per "row"

    :Examples:
    >>> xraster("http://sigplot.lgsinnovations.com/dat/penny.prm")

    >>> xraster([[1, 2, 3], [2, 3, 4], [1, 2, 3]])

    >>> xraster([1, 2, 3, 2, 3, 4, 1, 2, 3], subsize=3)

    >>> xraster([1, 2, 3, 2, 3, 4, 1, 2, 3], subsize=5)

    --

    Below is the argument and switch list for the XMIDAS primitive XRASTER

    --

    XRASTER - Midas file raster plotter for X-Windows terminals

    <file>      Filename to be plotted
    <zmin>      Data minimum value
    <zmax>      Data maximum value
    <mode>      Complex/Real mode (MAgnitude,REal,IMaginary,PHase,LOg,L2,D1,D2)
    <frame>     Frame length by index
    <colors>    Number of color levels

    Switches:
      /ALL      Compresses or expands data vertically so that it will all fill
            the window. (identical with LPF=0)
      /AUTO     Auto scaling mode (1=min, 2=max, 3=min&max)
      /AUTOL    Auto scaling exponential average length in lines, if this value
            is the special flag 0 and /AUTO is 1,2 or 3 then the entire
            file is read to determine scaling, BEFORE it is plotted.
      /AUTORR    Auto reread whenever a zoom occurs
      /AXES     Plots axes around the base layer displaying x,y units & file
    name
      /CBAR     Draws the colorbar along the right edge of the plot.  The colors
            are labeled when used with /AXES.
      /CMP      Specifies compression method (1=Average,2=Min,3=Max,
    4=Decimation)
      /CTM=n    Contour Mode (<0=Off 1=Contours 2=Overlay)
      /CTC=n    Contour color in overlay mode (-2=rubber,-1=white,0=black,
    >0=map)
      /CTL=n    Number of contour lines ( <=1 uses the size of the current map)
      /DBRANGE=n Set the dB range used for Auto full and Auto max log plot
    scaling
            default is 50 dB.  To disable, set to 0 (default for 'LO' and 'L2')
      /EXACT    Do not used the souped up algorithm for speeding up LOG
            calculations, (some precision is lost on very small values)
      /INMEM    Loads entire file into memory (for pipes this is always true)
      /LPB=n    Allows you to specify how many lines are read from disk at a
    time.
            Use 0 to read the entire screen in one GRAB.
      /LPF=n    Allows you to specify how many pixel lines are plotted for each
            frame of data, negative numbers indicate compression.
      /MASK=n    Mask containing which actions to report (see MSGMASK)
      /MIMIC=id  Id of XRASTER primitive to mimic (use /MSGID on other XRASTER)
      /NOCROSS  Disables the crosshairs
      /PCUTS    Brings X-Raster up in P Cuts mode
      /SPECS=0  Turns off the cursor specs at bottom of plot
      /STAY     Leaves X-Raster up even if no file specified on the command line
      /XFMT=fmt Display format for X cursor position; fmt can be GEN, SCI,
            VIS, MAN, ENG, HMS, DMS, (fortran format string) or
            [c format string]
      /XLAB=n   X units to use in /AXES, or X cuts; overrides file X units
      /YFMT=fmt Display format for Y cursor position; fmt can be GEN, SCI,
            VIS, MAN, ENG, HMS, DMS, (fortran format string) or
            [c format string]
      /YLAB=n   Y units to use in /AXES, or Y cuts; overrides file Y units
      /ZFMT=fmt Display format for Z value; fmt can be GEN, SCI,
            VIS, MAN, ENG, HMS, DMS, (fortran format string) or
            [c format string]
      /ZLAB=n   Z units to use plotting XY cuts during Scalar:Real, Complex:Mag

    """
    try:
        plot = SigPlot()
        display(plot)
        if isinstance(data, (tuple, list, np.ndarray)):
            data = np.asarray(data)

            if len(data.shape) != 2 and kwargs.get("subsize", None) is None:
                raise ValueError(
                    "Data passed in needs to be a 2-D array or ``subsize`` must be provided"
                )

            subsize = kwargs.get("subsize", None) or data.shape[-1]
            flattened_data = data.flatten().tolist()
            plot.show_array(flattened_data, subsize=subsize, layer_type="2D")
        else:
            plot.show_href(data, layer_type="2D")
    except Exception:
        clear_output()
        raise
        