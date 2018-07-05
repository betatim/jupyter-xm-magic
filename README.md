# SigPlot Jupyter Notebook Extension! [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/amatma/jupyter-xm-magic/master?filepath=SigPlotExtensionTest.ipynb)

## Installation (If not runnign the notebook on [myBinder](https://mybinder.org/v2/gh/amatma/jupyter-xm-magic/master?filepath=SigPlotExtensionTest.ipynb))
- Download extension from [GitHub](https://github.com/amatma/jupyter-xm-magic)
- Install Python 2.6+ or 3.5+
- Install `pip` (usually bundled with Python)
- Install Jupyter using `pip`
- Note: you do not need X-MIDAS installed to use  [SigPlot](https://github.com/lgsinnovations/sigplot).

```
pip install jupyter
```

- Install the SigPlot Jupyter Notebook extension

```
[/path/to/ipython-xm-magic]$ python setup.py install
```
- To launch the notebook, simply run:

$ jupyter notebook

Once the notebook has launched, loading the extension is pretty straightforward, just run
```
%load_ext xm_magic

```
## SigPlot Usage
- Sigplot(args*) - creates a sigplot with each arg as input data
- overlay_array(data) - adds an array of numbers to the sigplot's input data
- overlay_href(path) - adds data from an online source to the sigplot
- overlay_file(path) - adds data from a file to the sigplot
- plot() - displays an interactive sigplot  
