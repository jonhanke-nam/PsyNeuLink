# Visualize models with show_graph

PsyNeuLink provides three ways to visualize a {class}`Composition`:

1. **`show_graph()`** -- generate a static graph image (the focus of this
   guide).
2. **`animate`** argument of `run()` -- produce an animated GIF showing the
   execution sequence.
3. **PsyNeuLinkView** -- a standalone interactive application (under active
   development).

## Basic usage

Every Composition has a `show_graph()` method. Call it with no arguments to
see the default display:

```python
import psyneulink as pnl

a = pnl.ProcessingMechanism(name='A', input_shapes=3, output_ports=[pnl.RESULT, pnl.MEAN])
b = pnl.ProcessingMechanism(name='B', input_shapes=5)
c = pnl.ProcessingMechanism(name='C', input_shapes=2, function=pnl.Logistic(gain=pnl.CONTROL))

comp = pnl.Composition(name='Comp', enable_controller=True)
comp.add_linear_processing_pathway([a, c])
comp.add_linear_processing_pathway([b, c])

comp.show_graph()
```

By default:

- **Mechanisms** are ovals; **nested Compositions** are rectangles.
- **INPUT nodes** are green, **OUTPUT nodes** are red, **SINGLETON nodes**
  (both INPUT and OUTPUT) are brown.
- **Projections** appear as unlabeled arrows.

:::{note}
`show_graph()` requires the [Graphviz](https://www.graphviz.org/) system
package. Install it with `brew install graphviz` (macOS),
`apt-get install graphviz` (Debian/Ubuntu), or `choco install graphviz`
(Windows).
:::

## Display structure options

These arguments control *what* information is shown.

### show_node_structure

Show internal detail (Ports, roles) for each node:

```python
comp.show_graph(show_node_structure=True)
```

Use `pnl.ALL` for maximum detail including port functions and values.

### show_projections

Label projections with their names and/or weight matrix dimensions:

```python
comp.show_graph(show_projection_labels=True)
```

### show_controller

Display the Composition's controller, its ObjectiveMechanism, and all
ControlProjections:

```python
comp.show_graph(show_controller=True)
```

Controller-related components are drawn in blue by default; the controller
node itself in purple.

### show_learning

Display learning components (LearningMechanisms, LearningProjections, etc.):

```python
comp.show_graph(show_learning=True)
```

Learning components are drawn in orange by default.

### show_cim

Show the Composition's {class}`CompositionInterfaceMechanism` nodes (input_CIM
and output_CIM):

```python
comp.show_graph(show_cim=True)
```

### show_nested

Control how nested Compositions are displayed:

```python
# Show nested compositions expanded (embedded)
comp.show_graph(show_nested=True)

# Show nested compositions as separate inset graphs
comp.show_graph(show_nested=pnl.INSET)

# Limit nesting depth
comp.show_graph(show_nested=2)  # expand up to 2 levels
```

## Display attribute customization

Colors, shapes, and arrow styles can be customized using the
**show_graph_attributes** argument of the Composition constructor:

```python
comp = pnl.Composition(
    show_graph_attributes={
        'input_color': 'blue',
        'output_color': 'orange',
    }
)
```

### Default shapes

| Element                  | Shape            |
|--------------------------|------------------|
| Mechanism                | oval             |
| Nested Composition       | square           |
| CYCLE node               | doublecircle     |
| FEEDBACK_SENDER node     | octagon          |
| CONTROLLER node          | doubleoctagon    |
| ControlProjection        | box (arrowhead)  |

### Default colors

| Role / type              | Color   |
|--------------------------|---------|
| INPUT node               | green   |
| OUTPUT node              | red     |
| SINGLETON node           | brown   |
| Control components       | blue    |
| Controller               | purple  |
| Learning components      | orange  |
| Inactive Projection      | red     |

The colors, shapes, and arrow styles accept any value supported by
[GraphViz](https://www.graphviz.org/doc/info/attrs.html).

## Output formats

By default, `show_graph()` renders inline in Jupyter notebooks or opens a
viewer window. You can also save to a file:

```python
# Save as PDF
comp.show_graph(output_fmt='pdf', filename='my_model')

# Save as PNG
comp.show_graph(output_fmt='png', filename='my_model')

# Get the Graphviz source string
source = comp.show_graph(output_fmt='source')
```

## Animation

Generate a GIF that highlights each node as it executes, by passing the
**animate** argument to `run()`:

```python
comp.run(
    inputs={a: [[1, 2, 3]]},
    animate=True
)
```

Customize the animation with a dict:

```python
comp.run(
    inputs={a: [[1, 2, 3]]},
    animate={
        'show_controller': True,
        'unit': 'EXECUTION_SET',    # highlight by execution set
        'duration': 0.5,            # seconds per frame
        'movie_name': 'my_animation',
    }
)
```

:::{note}
Animation of components *within* a nested Composition is not currently
supported. The nested Composition's bounding box is highlighted when it
executes.
:::

## Combining options

Options can be combined freely:

```python
comp.show_graph(
    show_controller=True,
    show_learning=True,
    show_node_structure=True,
    show_nested=True,
    show_cim=True,
    show_projection_labels=True,
)
```

## Next steps

- {doc}`build-a-feedforward-network` -- construct models to visualize
- {doc}`add-control-to-a-model` -- add controllers that appear in graphs
- {doc}`log-and-report` -- inspect numeric values alongside visual displays
