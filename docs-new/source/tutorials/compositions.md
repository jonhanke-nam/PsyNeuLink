(compositions-tutorial)=
# Compositions

This tutorial covers {class}`Compositions <Composition>` -- the top-level container that
assembles Mechanisms and Projections into a runnable model. You will learn how to create
Compositions, add pathways, run them with inputs, inspect results, schedule execution at
multiple time scales, nest Compositions, and visualize model graphs.

## Creating a Composition

A {class}`Composition` can be created empty and built up incrementally, or initialized with
pathways in its constructor:

```python
import numpy as np
import psyneulink as pnl

# Option 1: Build incrementally
comp = pnl.Composition(name='My Model')
input_mech = pnl.ProcessingMechanism(input_shapes=3, name='Input')
output_mech = pnl.ProcessingMechanism(input_shapes=3, function=pnl.Logistic, name='Output')
comp.add_linear_processing_pathway([input_mech, output_mech])

# Option 2: Specify pathways in the constructor
input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = pnl.ProcessingMechanism(input_shapes=2, function=pnl.Logistic, name='Hidden')
output_layer = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='Output')

my_network = pnl.Composition(
    name='Simple Network',
    pathways=[[input_layer, hidden_layer, output_layer]]
)
```

## Adding Nodes and Pathways

### Adding Pathways

Use {meth}`~Composition.add_linear_processing_pathway` to add a sequence of Mechanisms
and optional Projections:

```python
comp = pnl.Composition(name='Stroop Model')
comp.add_linear_processing_pathway(color_pathway)
comp.add_linear_processing_pathway(word_pathway)
comp.add_linear_processing_pathway(task_color_pathway)
comp.add_linear_processing_pathway(task_word_pathway)
comp.add_linear_processing_pathway(decision_pathway)
```

When a Mechanism appears in more than one pathway, PsyNeuLink recognizes it as the same
node and creates the appropriate converging or diverging connections.

### Adding Individual Nodes

You can also add Mechanisms individually:

```python
comp.add_nodes([mechanism_a, mechanism_b])
```

And then connect them with explicit Projections:

```python
comp.add_projection(
    pnl.MappingProjection(sender=mechanism_a, receiver=mechanism_b)
)
```

## Running a Composition

### Single Trial

Call the {meth}`~Composition.run` method with an input dictionary mapping each `INPUT`
Mechanism to its input value:

```python
result = my_network.run(inputs={input_layer: [1, 4.7, 3.2, 6, 2]})
print(result)
# [array([0.88079707, 0.88079707, 0.88079707, 0.88079707, 0.88079707])]
```

If the Composition has only one `INPUT` Mechanism, you can pass the input directly:

```python
result = my_network.run([1, 4.7, 3.2, 6, 2])
```

### Multiple Trials

Provide a list of inputs for each Mechanism. Each element of the list is the input for
one trial:

```python
red   = [1, 0]
green = [0, 1]
color = [1, 0]
word  = [0, 1]

                                   # Trial 1  Trial 2
Stroop_model.run(inputs={color_input:[red,     red   ],
                         word_input: [red,     green ],
                         task_input: [color,   color ]})
```

### Accessing Results

After running, results are available via several attributes:

- {attr}`~Composition.results` -- the output of all `OUTPUT` Mechanisms for every trial
- {attr}`~Composition.output_values` -- the output of all `OUTPUT` Mechanisms for the most
  recent trial

```python
print(Stroop_model.results)
# [[array([1.]), array([2.80488344])], [array([1.]), array([3.94471513])]]
```

The results attribute stores a list of trial results. Each trial result contains the
output values of every `OUTPUT` Mechanism. In the Stroop example, the {class}`DDM` is the
only OUTPUT Mechanism and it produces two values: the decision outcome (1 or -1) and the
estimated mean decision time in seconds.

## Scheduling and Multi-Timescale Execution

By default, each Mechanism in a Composition executes once per pass through the graph, in
the order determined by the Projections between them. PsyNeuLink's {class}`Scheduler` lets
you override this with {class}`Conditions <Condition>` that control when each Mechanism
executes.

### Termination Conditions

You can specify when a trial should end using `termination_processing`:

```python
decision = pnl.DDM(
    name='DECISION',
    input_format=pnl.ARRAY,
    reset_stateful_function_when=pnl.AtTrialStart(),
    function=pnl.DriftDiffusionIntegrator(noise=0.5, threshold=20)
)

comp.run(
    inputs={color_input: red, word_input: green, task_input: color},
    termination_processing={pnl.TimeScale.TRIAL: pnl.WhenFinished(decision)}
)
```

This runs the trial until the DDM's integration process crosses its threshold, rather than
executing each Mechanism only once.

### Scheduling Conditions

Conditions can specify how many times a Mechanism must wait for another to execute before
it runs, or make execution contingent on a custom function:

```python
# Make color_hidden wait until task has executed 10 times
comp.scheduler.add_condition(color_hidden, pnl.EveryNExecutions(task, 10))
comp.scheduler.add_condition(word_hidden, pnl.EveryNExecutions(task, 10))
```

You can also use arbitrary functions as conditions:

```python
def converge(mech, thresh):
    return all(abs(v) <= thresh for v in mech.delta)

epsilon = 0.01
comp.scheduler.add_condition(color_hidden, pnl.When(converge, task, epsilon))
comp.scheduler.add_condition(word_hidden, pnl.When(converge, task, epsilon))
```

This makes the hidden layers wait until the `task` Mechanism's value has converged (i.e.,
the change between successive executions falls below `epsilon`).

PsyNeuLink provides a rich set of {ref}`pre-defined Conditions <Condition_Pre-Specified_List>`,
but you can also create custom Conditions from any Python function.

## Execution Hooks

The {meth}`~Composition.run` method supports callback arguments that let you execute
custom code at specific points during a run:

| Argument | When it runs |
|----------|-------------|
| `call_before_trial` | Before each trial |
| `call_after_trial` | After each trial |
| `call_before_pass` | Before each pass through the graph |
| `call_after_pass` | After each pass through the graph |

Example:

```python
def print_after():
    print(f'output: {output.value[0]}')
    print(f'decision: {decision.value[0]}')

comp.run(inputs=stimuli, call_after_trial=print_after)
```

## Nested Compositions

A Composition can contain other Compositions as nodes, creating hierarchical models. This
is useful for organizing complex models into modular sub-systems:

```python
# Create a sub-model
sub_model = pnl.Composition(name='Sub-Model')
sub_model.add_linear_processing_pathway([mech_a, mech_b])

# Embed it in a larger model
full_model = pnl.Composition(name='Full Model')
full_model.add_nodes([input_mech, sub_model, output_mech])
full_model.add_projection(pnl.MappingProjection(sender=input_mech, receiver=sub_model))
full_model.add_projection(pnl.MappingProjection(sender=sub_model, receiver=output_mech))
```

When a nested Composition is executed as part of its outer Composition, it runs its full
internal graph for each execution step.

## Visualizing the Graph

Every Composition can display its computational graph using {meth}`~ShowGraph.show_graph`:

```python
comp.show_graph()
```

`INPUT` nodes are colored green and `OUTPUT` nodes are colored red. Several options
control what is shown:

| Option | What it shows |
|--------|--------------|
| `show_node_structure=True` | Internal ports and parameters of each node |
| `show_controller=True` | The Composition's controller and its connections |
| `show_learning=True` | Learning components (LearningMechanisms, LearningProjections) |

```python
# Show the Stroop model with its controller
Stroop_model.show_graph(show_controller=True)
```

### Animation

The **animate** argument of {meth}`~Composition.run` generates an animated visualization
of execution:

```python
comp.run(inputs=stimuli, animate={"show_controller": True})
```

This produces a frame-by-frame animation showing which Mechanisms execute at each step.

## Graph Export

Compositions are represented internally as dependency dictionaries, making them compatible
with graph-theoretic packages like [NetworkX](https://networkx.github.io) and
[igraph](http://igraph.org). They can also be exported as JSON for exchange with other
modeling tools.

## Next Steps

- {doc}`control` -- adding control mechanisms that monitor and regulate processing
- {doc}`learning` -- training the model's Projections
- {doc}`basics-and-primer` -- comprehensive reference document
