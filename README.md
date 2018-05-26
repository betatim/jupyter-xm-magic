# X-MIDAS Jupyter Notebook Magic!

![magic](magic.gif)

## Installation

- Install Python 2.6+ or 3.5+
- Install `pip` (usually bundled with Python)
- Install Jupyter using `pip`
- Note: you do not need X-MIDAS installed to use the inline plotting via [SigPlot](https://github.com/lgsinnovations/sigplot).

```
pip install jupyter
```

- Install the XMIDAS Jupyter Notebook extension

```
[/path/to/ipython-xm-magic]$ python setup.py install
```

## Running

- To enable the `xm` extension so you can run X-MIDAS commands from the notebook, start X-MIDAS, ensure XMPY is added to the path, and launch jupyter with `xmpy`

```
$ xmstart
$ xm
X-MIDAS> xmp +xmpy
Configuration: XMPY,SYS
X-Midas> pyenv
Establishing XMPY build environment
X-MIDAS> xmjupyter
...
```

- If you only want the SigPlot interactive plotting, you can just run

```
$ jupyter notebook
```

In either case, once the notebook has launched, loading the `xm` extension is pretty straightforward, just run

```
%load_ext xm_magic
```

and voilà!