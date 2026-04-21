# Visualization

There are three ways to visualize models composed in PsyNeuLink: statically, using the
{any}`show_graph <ShowGraph.show_graph>` method of a {any}`Composition`; using the **animate** argument of a Composition's
{any}`run <Composition.run>` method to output a gif showing the sequence with which its
{ref}`Nodes <Composition_Nodes>` are executed; or interactively to configure the display and plot Component
{any}`values <Component.value>` using
[PsyNeuLinkView](http://www.psyneuln.deptcpanel.princeton.edu/psyneulink-view-2/) --
a standalone application that interacts closely with the Python script in which a PsyNeuLink model is composed.

:::{note}
The [PsyNeuLinkView](http://www.psyneuln.deptcpanel.princeton.edu/psyneulink-view-2/) application is still under
development; at present, it can be used to display a Composition and arrange its Components. Its functionality is
being actively expanded, and it should soon be able to display animated plots of Component values as a Composition
executes. It can be accessed [here](https://github.com/dillontsmith/PsyNeuLinkView).
:::

At present, use of the Composition's {any}`show_graph <ShowGraph.show_graph>` method and the **animate** argument of its
{any}`run <Composition.run>` method are the primary ways to visualize a {any}`Composition`. The former is described below,
including {ref}`examples <ShowGraph_Examples_Visualization>` of its use.

:::{seealso}
- {doc}`composition` -- the Composition class whose graph can be displayed
:::

```{eval-rst}
.. automodule:: psyneulink.core.compositions.showgraph
   :members:
   :exclude-members: random, ShowGraphError
```
