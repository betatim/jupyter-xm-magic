require.config({
  paths: {
    "sigplot": "/nbextensions/sigplotjs/sigplot-debug"
  },
  shim: {
    "sigplot": {exports: "sigplot"}
  }
});

define('sigplot_ext', ["@jupyter-widgets/base", "sigplot"], function(widgets, sigplot) {
  var img;
  var SigPlotView = widgets.DOMWidgetView.extend({

    /**
     * Instantiates the plot, attaches it to the DOM, and sets up change listeners
     * on the kernel-side (i.e., the model)
     */
    render: function() {
      try {
        // Instantiate a new plot and attach to the element provided in `this.$el[0]`
        this.plot = new sigplot.Plot(this.$el[0], {
          autohide_readout: true,
          autohide_panbars: true,
        });

        // Wait for element to be added to the DOM
        var self = this;
        window.setTimeout(function() {
          self.$el.css('width', '100%');
          self.$el.css('height', '350px');
          self.plot.checkresize()
        }, 0);

        this.listenTo(this.model, 'change:array_obj', this._plot_from_array, this);
        this.listenTo(this.model, 'change:href_obj', this._plot_from_file, this);
        this.listenTo(this.model, 'change:done', this._done, this);

        // TODO: Figure out how to remove internal Jupyter keyboard shortcuts
        // Jupyter.keyboard_manager.remove_shortcut('x');
        // Jupyter.keyboard_manager.remove_shortcut('y');
        // Jupyter.keyboard_manager.remove_shortcut('p');
        // Jupyter.keyboard_manager.remove_shortcut('m');
      } catch(err) {
        console.error("Error rendering sigplot: " + err);
      }
    },

    /**
     * Handles plotting both 1-D (xplot) and 2-D arrays (xraster)
     */
    _plot_from_array: function() {
      var old_array_obj = this.model.previous('array_obj');
      var array_obj = this.model.get('array_obj');

      // Check that the arrays are different
      if (old_array_obj === array_obj) {
        return;   
      } else {
        this.plot.overlay_array(
          array_obj.data,
          array_obj.overrides,
          {layerType: array_obj.layerType});
      }
    },

    /**
     * Plots a file (either local or via HTTP/HTTPS)
     */
    _plot_from_file: function() {
      var old_href_obj = this.model.previous('href_obj');
      var href_obj = this.model.get('href_obj');

      // Check that this is a new file
      if (old_href_obj === href_obj) {
        return;   
      } else {
        var url = href_obj.filename;
        if (!url.startsWith("http")) {
          url = window.location.protocol + '//' + window.location.host + '/files/' + url;
        }
        this.plot.overlay_href(
          url,
          null,
          {layerType: href_obj.layerType},
        );
      }
    },

    _done: function() {
      if (this.model.get('done')) {
        plotLocal=this.plot
        window.setTimeout(function() {
          var img = plotLocal._Mx.active_canvas.toDataURL("image/png");
          var link = document.createElement("a");
          link.href = img;
          link.display = img;
          document.body.appendChild(link);
          document.body.appendChild(link);
          //document.write('<ing src="' + img +'"/>');
          document.body.removeChild(link);
        }, 2000);
      }

    }
  });

  return {
    SigPlotView: SigPlotView

  };
});
