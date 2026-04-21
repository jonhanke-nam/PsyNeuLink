# Build a feedforward network

This guide shows how to construct, configure, and run feedforward neural
networks in PsyNeuLink using {class}`ProcessingMechanism` nodes connected by
{class}`MappingProjection` edges inside a {class}`Composition`.

## A minimal 3-layer network

The simplest approach is to list your mechanisms in order inside a
{class}`Composition`. PsyNeuLink automatically creates {class}`MappingProjection`
connections between adjacent layers with full-connectivity weight matrices
(all weights = 1):

```python
import psyneulink as pnl

# Define the layers
input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = pnl.ProcessingMechanism(input_shapes=2, function=pnl.Logistic, name='Hidden')
output_layer = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='Output')

# Assemble into a Composition
my_network = pnl.Composition(pathways=[[input_layer, hidden_layer, output_layer]])
```

The pathway `[input_layer, hidden_layer, output_layer]` tells PsyNeuLink to
create projections connecting Input -> Hidden -> Output. Each mechanism uses
the function you specify (or {class}`Linear` by default).

### Running the network

Call `run()` with an input dictionary or a single array sized for the first
mechanism in the pathway:

```python
result = my_network.run([1, 4.7, 3.2, 6, 2])
print(result)
# [[0.88079707, 0.88079707, 0.88079707, 0.88079707, 0.88079707]]
```

### Executing a single mechanism

Any mechanism can be executed on its own (useful for debugging or for use
outside a Composition):

```python
output_layer.execute([0, 2.5, 10.9, 2, 7.6])
# array([[0.5, 0.92414182, 0.99998154, 0.88079708, 0.9994998]])
```

### Viewing the graph

Use `show_graph()` to visualize the network. INPUT nodes appear in green,
OUTPUT nodes in red:

```python
my_network.show_graph()
```

## Specifying weights

By default, PsyNeuLink creates full-connectivity matrices with weights of 1.
You can specify a custom weight matrix by inserting it (or a
{class}`MappingProjection`) between mechanisms in the pathway.

### Insert a matrix directly

```python
import numpy as np

my_network = pnl.Composition()
my_network.add_linear_processing_pathway([
    input_layer,
    (0.2 * np.random.rand(5, 2)) - 0.1,   # 5x2 random weights in [-0.1, 0.1]
    hidden_layer,
    output_layer
])
```

PsyNeuLink infers that the array is a weight matrix and wraps it in a
{class}`MappingProjection` automatically.

### Insert a MappingProjection explicitly

```python
my_proj = pnl.MappingProjection(
    matrix=(0.2 * np.random.rand(5, 2)) - 0.1
)

my_network = pnl.Composition()
my_network.add_linear_processing_pathway([
    input_layer, my_proj, hidden_layer, output_layer
])
```

This gives you a reference to the projection object so you can inspect or
modify its `matrix` parameter later.

## Building a Stroop model

A more realistic example: a model of the
[Stroop task](https://en.wikipedia.org/wiki/Stroop_effect) with two input
pathways (color naming and word reading), a task pathway, and a decision
mechanism. This is based on
[Cohen et al. (1990)](https://www.researchgate.net/publication/20956134).

```python
import numpy as np
import psyneulink as pnl

# --- Color naming pathway ---
color_input = pnl.ProcessingMechanism(name='COLOR INPUT', input_shapes=2)
color_input_to_hidden_wts = np.array([[2, -2], [-2, 2]])
color_hidden = pnl.ProcessingMechanism(
    name='COLOR HIDDEN', input_shapes=2, function=pnl.Logistic(bias=-4)
)
color_hidden_to_output_wts = np.array([[2, -2], [-2, 2]])
output = pnl.ProcessingMechanism(name='OUTPUT', input_shapes=2, function=pnl.Logistic)
color_pathway = [color_input, color_input_to_hidden_wts,
                 color_hidden, color_hidden_to_output_wts, output]

# --- Word reading pathway (shares the output layer) ---
word_input = pnl.ProcessingMechanism(name='WORD INPUT', input_shapes=2)
word_input_to_hidden_wts = np.array([[3, -3], [-3, 3]])
word_hidden = pnl.ProcessingMechanism(
    name='WORD HIDDEN', input_shapes=2, function=pnl.Logistic(bias=-4)
)
word_hidden_to_output_wts = np.array([[3, -3], [-3, 3]])
word_pathway = [word_input, word_input_to_hidden_wts,
                word_hidden, word_hidden_to_output_wts, output]

# --- Task pathways ---
task_input = pnl.ProcessingMechanism(name='TASK INPUT', input_shapes=2)
task_color_wts = np.array([[4, 4], [0, 0]])
task_word_wts = np.array([[0, 0], [4, 4]])
task_color_pathway = [task_input, task_color_wts, color_hidden]
task_word_pathway = [task_input, task_word_wts, word_hidden]

# --- Decision pathway ---
decision = pnl.DDM(name='DECISION', input_format=pnl.ARRAY)
decision_pathway = [output, decision]

# --- Assemble the Composition ---
Stroop_model = pnl.Composition(name='Stroop Model')
Stroop_model.add_linear_processing_pathway(color_pathway)
Stroop_model.add_linear_processing_pathway(word_pathway)
Stroop_model.add_linear_processing_pathway(task_color_pathway)
Stroop_model.add_linear_processing_pathway(task_word_pathway)
Stroop_model.add_linear_processing_pathway(decision_pathway)
```

### Running the Stroop model

Define stimuli and run for two trials -- one congruent, one incongruent:

```python
red   = [1, 0]
green = [0, 1]
word  = [0, 1]
color = [1, 0]

#                                         Trial 1   Trial 2
Stroop_model.run(inputs={color_input: [red,       red   ],
                         word_input:  [red,       green ],
                         task_input:  [color,     color ]})
print(Stroop_model.results)
# [[array([1.]), array([2.80488344])], [array([1.]), array([3.94471513])]]
```

The {class}`DDM` returns two values per trial: the decision outcome (1 or -1)
and the estimated mean decision time. Notice the incongruent trial (Trial 2)
takes longer.

## Adding a recurrent connection

You can create a recurrent (feedback) projection by repeating a mechanism in
the pathway:

```python
my_network = pnl.Composition()
my_network.add_linear_processing_pathway([
    input_layer, hidden_layer, output_layer, hidden_layer
])
```

This tells PsyNeuLink to create a projection from `output_layer` back to
`hidden_layer`. Alternatively, add the recurrent projection explicitly:

```python
my_network = pnl.Composition()
my_network.add_linear_processing_pathway([input_layer, hidden_layer, output_layer])

recurrent_proj = pnl.MappingProjection(sender=output_layer, receiver=hidden_layer)
my_network.add_projection(recurrent_proj)
```

## Next steps

- {doc}`add-control-to-a-model` -- add conflict monitoring and control to the
  Stroop model
- {doc}`visualize-models` -- customize `show_graph()` displays
- {doc}`use-pytorch-models` -- train feedforward networks with PyTorch via
  {class}`AutodiffComposition`
