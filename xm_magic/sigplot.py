#!/usr/bin/env python
from __future__ import absolute_import
import os
import numpy as np
from ipywidgets import widgets
from traitlets import (
    Unicode,
    List,
    Dict
)
from IPython.display import (
    display,
    clear_output,
)
try:
    import bluefile
except ImportError:
    bluefile = None

from IPython.core.magic import register_line_cell_magic
from IPython.display import (
    display,
    clear_output,
)

class SigPlot(widgets.DOMWidget):
    _view_module_version = Unicode('0.0.1')

    _view_name = Unicode("SigPlotView").tag(sync=True)
    _view_module = Unicode("sigplot_ext").tag(sync=True)

    href_obj = Dict().tag(sync=True)
    array_obj = Dict().tag(sync=True)
    inputs=[]
    dimension=1

    def __init__(self, *args, **kwargs):
        """This is one place where the XPLOT/XRASTER switches
        should be applied.
        """
        self.inputs=[]
        for arg in args:
            self.inputs.append(arg)
        super(SigPlot, self).__init__(**kwargs)

    def show_array(self, data, layer_type="1D", subsize=None):
        """Plot a list with SigPlot

        :param data: one-dimensional list
        :type data: List[float]

        :param layer_type: either '1D' or '2D'
        :type layer_type: str

        :param subsize: If ``layer_type`` is '2D', ``subsize`` is the
                        number of elements per row.
        :type subsize: int

        :Example:
        >>> plot = SigPlot()
        >>> display(plot)
        >>> plot.overlay_href([1, 2, 3, 4], layer_type='2D', subsize=2)

        >>> plot = SigPlot()
        >>> display(plot)
        >>> plot.overlay_href([1, 2, 3, 4], layer_type='1D')
        """
        overrides = {}
        if layer_type == "2D":
            # subsize is *required* if it's 2-D
            if subsize is None and isinstance(data, (list, tuple)):
                raise ValueError("For xraster, a subsize is required")
            elif subsize is not None and isinstance(data, (list, tuple)):
                overrides.update({
                    "subsize": subsize,
                })

        self.array_obj = {
            "data": data,
            "overrides": overrides,
            "layerType": layer_type,
        }

    @register_line_cell_magic
    def overlay_array(self, data):
        self.inputs.append(data)

    def show_href(self, fpath, layer_type):
        """Plot a file or URL with SigPlot

        :param fpath: File-path to bluefile or matfile. Forms accepted:
                      - absolute paths, e.g., /data/foo.tmp
                      - relative paths, e.g., ../foo.tmp
                      - paths with envvars, e.g., $HOME/foo.tmp
                      - paths with tilde, e.g., ~/foo.tmp
                      - local path, e.g., foo.tmp
                      - file in MIDAS aux path, e.g., foo.tmp (actually in /data/midas/`whoami`/foo.tmp)
                      - URL, e.g., http://sigplot.lgsinnovations.com/dat/sin.tmp
        :type fpath: str

        :param layer_type: either '1D' or '2D'
        :type layer_type: str

        :Example:
        >>> plot = SigPlot()
        >>> display(plot)
        >>> plot.overlay_href('foo.tmp', layer_type='2D')
        """
        # if the file is HTTP/HTTPS, SigPlot.js will handle it
        if not fpath.startswith("http"):
            # expand out environment variables and ~
            fpath = os.path.expanduser(os.path.expandvars(fpath))
            # if the file doesn't exist, perhaps it's in a MIDAS aux
            if not os.path.exists(fpath):
                # expand out the aux
                try:
                    fpath_new = bluefile.form_read_path(fpath)
                    if not os.path.exists(fpath_new):
                        raise IOError("No such file %s" % fpath_new)
                    fpath = fpath_new
                except AttributeError:
                    raise IOError("No such file %s" % fpath)

            symlink = False
            if not os.path.isabs(fpath):
                # if it's not an absolute path (i.e., is relative), check if it is
                # beyond ${CWD} or if it starts with a `..`
                if fpath.startswith('..'):
                    # need to symlink
                    symlink = True
            else:
                # check if it is within ${CWD}
                if fpath.startswith(os.getcwd() + '/'):
                    # great, it's already in ${CWD}/
                    # so we're done!
                    fpath_without_cwd = fpath.replace(os.getcwd() + '/', '')
                    print("not need to symlink")
                    print(fpath_without_cwd)
                    fpath = fpath_without_cwd
                else:
                    # it's somewhere else, need to symlink
                    print("need to symlink")
                    symlink = True

            # if we need to symlink
            if symlink:
                # make a data directory
                try:
                    os.mkdir('data')
                except OSError:
                    pass

                # file will be symlinked to ${CWD}/data/
                file_in_data_dir = os.path.join(os.getcwd(), 'data', os.path.basename(fpath))

                print(file_in_data_dir)
                print(fpath)

                # if the symlink fails because it already exists,
                # woohoo, just use the existing one
                try:
                    os.symlink(fpath, file_in_data_dir)
                except FileExistsError:
                    pass

                # set ``fpath`` to just the relative path so we can get it via
                # the Jupyter API (i.e., http://${HOST}:${PORT}/files/data/...)
                fpath = os.path.join('data', os.path.basename(fpath))

        self.href_obj = {
            "filename": fpath,
            "layerType": layer_type,
        }

    @register_line_cell_magic
    def overlay_href(self, path):
        self.inputs.append(path)

    @register_line_cell_magic
    def plot(self, layer_type='1D', subsize=None):
        try:
            display(self)
            for arg in self.inputs:
                if isinstance(arg, (tuple, list, np.ndarray)):
                    data = arg
                    if (layer_type=="2D"):
                        data=np.asarray(data)
                        if len(data.shape) != 2 and subsize is None:
                            raise ValueError(
                                "Data passed in needs to be a 2-D array or ``subsize`` must be provided"
                            )
                        elif len(data.shape)==2:
                            subsize= data.shape[-1]
                            data=data.flatten().tolist()
                        else:
                            data=arg
                    else:
                        if isinstance(arg, np.ndarray):
                            data = data.tolist()


                    self.show_array(data, layer_type=layer_type, subsize=subsize)
                else:
                    sub_args = arg.split('|')
                    for sub_arg in sub_args:
                        self.show_href(sub_arg, layer_type)
        except Exception:
            clear_output()
            raise




    def xplot(*args, **kwargs):
        """Wrapper around SigPlot for 1-D plotting

        Currently supports plotting Python lists, Python tuples, numpy arrays,
        HTTP/HTTPS-prefixed files, and local files.

        :param \*args: A heterogeneous list of files and/or data lists
        :type \*args: List[Union[str, numpy.ndarray, List, Tuple]]

        :param \**kwargs: Not implemented yet.
        :type \**kwargs: Dict[str]

        :Examples:
        >>> xplot(
        ...     "http://sigplot.lgsinnovations.com/dat/sin.tmp|http://sigplot.lgsinnovations.com/dat/pulse.tmp",
        ...     np.arange(0, 4, .001)
        ... )

        >>> xplot("http://sigplot.lgsinnovations.com/dat/sin.tmp", "http://sigplot.lgsinnovations.com/dat/pulse.tmp")

        >>> import numpy as np
        >>> f1 = np.sin(np.arange(0, 20, 0.01))
        >>> f2 = np.cos(np.arange(0, 20, 0.01))
        >>> xplot(f1, f2)

        --

        Below is the argument and switch list for the XMIDAS primitive XPLOT

        --

        XPLOT - a generic Midas file plotter for X-Windows terminals

        <file(s)>   Filename(s) to be plotted (supports types 1000,2000,3000,5000,
        6000)
        <start>     Start abscissa in file (index if IN present below or /INDEX)
        <end>       End abscissa in file (index if IN present below or /INDEX)
        <[IN]mode>  Complex mode (MAgnitude,PHase,LOg,etc.) with optional IN prefix
        <line>      Line type and thickness, 999 for mixed, <0 dashed, >0 solid
        <ylabel>    Optional ordinate label specifier
        <ymin>      Forced ordinate minimum (usually autoscaled)
        <ymax>      Forced ordinate maximum (usually autoscaled)

        Switches:
          /ALL        Don't limit on-screen data to 32k elements/layer, reread
        from file
          /AUTO       Set auto-scale behavior for Y axis: 0=none, 1=min, 2=max,
        3=both
                  This affects scaling of plot field on startup and during rereads.
          /AUTOX      Set auto-scale behavior for X axis: 0=none, 1=min, 2=max,
        3=both
                  This affects scaling of plot field on startup and during rereads.
          /BS=n       Implements limited backing store for the first n zoom levels
          /BUF=n      Specifies a buffer limit other than 32k elements
          /CROSS      Draws crosshairs that follow the mouse in the plotting field
          /FORCELAB   Forces the usage of /xlab and /ylab values regardless of mode
          /INDEX      Plots data files by their indices, rather than by abscissa
        values
          /NOGRID     X-Plot brought up without dashed grid lines across plotting
        field
          /LEGEND     Brings up plot with trace legend in upper right corner
          /MASK=n     Mask containing which actions to report (see MSGMASK)
          /MIMIC=id   Id of XPLOT primitive to mimic (use /MSGID on other XPLOT)
          /MOD        Brings XPLOT up in modify mode
          /MSGID=id   Id of primitive to report actions to
          /NOPAN      X-Plot brought up without pan scrollbars
          /PMT=s      Refresh rate threshold (in seconds) for repeating pan actions
          /PHUNITS=c  Units for phase plot: 'R'adians, 'D'egrees [default], or
        'C'ycles
          /PSFILE=f   Writes out PostScript of initial view to file f
          /NOSPECS    X-Plot brought up with no display specs or axes (S key to
        toggle)
          /NOXAXIS    X-Plot brought up with no x-axis
          /NOYAXIS    X-Plot brought up with no y-axis
          /NOREADOUT  X-Plot brought up with no display specs (S key to toggle)
          /NSEC=n     Splits the plotting field into n sections stacked on top
                  of one another.  Layers are distributed so that layer 1 is in
                  section 1, layer 2 in section 2, etc. wrapping around to the
                  top when there are more layers than sections.
          /SEGMENT    For type 3/6000 files deriving their abscissa values from
        the data
                  file do not connect lines between adjacent abscissa values that
                  are non-increasing.  This does not apply to complex data plotted
                  in R vs I mode.
          /SPECS=c    Brings up plot with specs in 'I'ndex, 'R'ecipr, 'S'lope or
                  'T'imecode (only available when the X axis is also in timecode)
          /STAY       Does not M$ERROR if command line files cannot be opened
          /TRACE=(tag=val,...) Used to set line characteristics for all layers.
                  See the HELP /TRACE. LINE types supported are None,Verticals,
                  Horizontals and Connecting (the default.)
          /XDIV       Number of grid divisions along X axis (>0 appx, <0 exact)
          /XFMT=fmt   Display format for X cursor position; fmt can be GEN, SCI,
                VIS, MAN, ENG, HMS, DMS, (fortran format string) or
                [c format string]
          /XLAB       Units code for the X scale. Run the UNITS command for a list
                of possible values.
          /YDIV       Number of grid divisions along Y axis (>0 appx, <0 exact)
          /YFMT=fmt   Display format for Y cursor position; fmt can be GEN, SCI,
                VIS, MAN, ENG, HMS, DMS, (fortran format string) or
                [c format string]
          /YINV       Inverts Y scale (min Y value at top, max Y value at top)
          /YLAB       Units code for the Y scale. Run the UNITS command for a list
                of possible values.

        """
        try:
            display(self)
            for arg in args:
                if isinstance(arg, (tuple, list, np.ndarray)):
                    if isinstance(arg, np.ndarray):
                        arg = arg.tolist()
                    plot.show_array(arg)
                else:
                    sub_args = arg.split('|')
                    for sub_arg in sub_args:
                        plot.show_href(sub_arg, layer_type="1D")
        except Exception:
            clear_output()
            raise

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
            display(self)
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




