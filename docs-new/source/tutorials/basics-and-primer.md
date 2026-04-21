# Basics and Primer

This page provides a comprehensive introduction to PsyNeuLink, starting with
the core concepts and progressing through increasingly sophisticated examples.
It uses a single evolving model — the **Stroop task** — to demonstrate how
PsyNeuLink's features work together.

```{contents} On this page
:depth: 2
:local:
```

---

## Basics

### Overview

PsyNeuLink models are made up of **Components** and **Compositions**:

- **Components** are objects that perform a specific function
- **Compositions** combine Components into a runnable model

There are two primary kinds of Components:

| Component | Role | Analogy |
|-----------|------|---------|
| **Mechanism** | Processes information — takes input, applies a function, produces output | A "block" in a block diagram; a node in a graph |
| **Projection** | Transmits information between Mechanisms | A "link"; a directed edge in a graph |

Compositions assemble Mechanisms and Projections into pathways that form a
[computational graph](https://en.wikipedia.org/wiki/Graph_(abstract_data_type)).
Compositions can also be nested inside other Compositions to create
hierarchical models (e.g., circuits within a larger system-level model).

A **Scheduler** coordinates execution. By default, it runs Mechanisms in the
order determined by the Projections between them. You can customize execution
order using **Conditions** — for example, to handle feedback pathways or
run Components at different time scales.

### Mechanisms and Projections

Mechanisms and Projections fall into two broad categories:

::::{grid} 2
:gutter: 3

:::{grid-item-card} Processing
**ProcessingMechanisms** directly transmit and transform information, linked
by **PathwayProjections** (typically MappingProjections).

Examples: layers of a neural network, drift diffusion decision processes,
integrators, comparators.
:::

:::{grid-item-card} Modulatory
**ModulatoryMechanisms** modify how other Mechanisms process information,
via **ModulatoryProjections**.

- **ControlMechanisms** modulate parameters of ProcessingMechanisms
- **LearningMechanisms** modify Projection weights
:::

::::

Every Mechanism has a **function** that defines its computation. PsyNeuLink
provides a rich library of built-in functions (linear, logistic, ReLU,
integration, optimization, etc.), but you can also assign any Python function
(see [Customization](#customization) below).

```{figure} ../_static/BasicsAndPrimer_GrandView_fig.svg
:width: 100%

**PsyNeuLink Environment.** Full-colored items are currently implemented;
dimmed items are planned for future implementation.
```

:::{seealso}
- {doc}`mechanisms-and-functions` — focused tutorial on Mechanism types
- {doc}`/explanation/architecture` — in-depth architecture discussion
- {doc}`/reference/quick-reference` — concise reference of all component types
:::

---

## Primer

The examples below illustrate PsyNeuLink's capabilities, progressing from
simple to advanced. They assume some familiarity with computational modeling.

### Simple Configurations

Linking Mechanisms into a model can be as simple as listing them — PsyNeuLink
creates the necessary Projections automatically.

**A 3-layer feedforward network:**

```python
# Construct the Mechanisms:
input_layer = ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = ProcessingMechanism(input_shapes=2, function=Logistic, name='hidden')
output_layer = ProcessingMechanism(input_shapes=5, function=Logistic, name='output')

# Construct the Composition:
my_network = Composition(pathways=[[input_layer, hidden_layer, output_layer]])
```

Each Mechanism can also be executed individually:

```python
output_layer.execute([0, 2.5, 10.9, 2, 7.6])
# array([[0.5, 0.92414182, 0.99998154, 0.88079708, 0.9994998]])
```

The Composition's graph can be visualized with `show_graph()`:

```{figure} ../_static/BasicsAndPrimer_SimplePathway_fig.svg
:width: 30%

**Composition Graph.** Green = `INPUT` node, Red = `OUTPUT` node.
```

Run the Composition with the `run()` method:

```python
my_network.run([1, 4.7, 3.2, 6, 2])
# [array([0.88079707, 0.88079707, 0.88079707, 0.88079707, 0.88079707])]
```

#### Specifying Projections explicitly

PsyNeuLink picks sensible defaults — in the example above, no Projections
were specified, so it created MappingProjections with full connectivity
(weight = 1). But you can specify them explicitly:

```python
# Create a Projection with random weights between -0.1 and +0.1
my_projection = MappingProjection(matrix=(.2 * np.random.rand(2, 5)) - .1)
my_network = Composition()
my_network.add_linear_processing_pathway([input_layer, my_projection, hidden_layer, output_layer])
```

Or insert a weight matrix directly:

```python
my_network.add_linear_processing_pathway(
    [input_layer, (.2 * np.random.rand(2, 5)) - .1, hidden_layer, output_layer]
)
```

#### Adding recurrent connections

A recurrent Projection can be added by repeating a Mechanism in the pathway:

```python
my_network.add_linear_processing_pathway([input_layer, hidden_layer, output_layer, hidden_layer])
```

Or by creating the connection explicitly:

```python
my_network.add_linear_processing_pathway([input_layer, hidden_layer, output_layer])
recurrent_projection = MappingProjection(sender=output_layer, receiver=hidden_layer)
my_network.add_projection(recurrent_projection)
```

:::{seealso}
{doc}`projections-and-pathways` — more on Projections and pathway construction
:::

---

### More Elaborate Configurations

The following implements a model of the
[Stroop task](https://en.wikipedia.org/wiki/Stroop_effect) — a simplified
version of
[Cohen et al. (1990)](https://www.researchgate.net/publication/20956134).
It has:

- A **color naming** pathway
- A **word reading** pathway
- **Task instruction** pathways controlling which to perform
- A **DDM decision** mechanism for determining the response

```python
# Construct the color naming pathway:
color_input = ProcessingMechanism(name='COLOR INPUT', input_shapes=2)
color_input_to_hidden_wts = np.array([[2, -2], [-2, 2]])
color_hidden = ProcessingMechanism(name='COLOR HIDDEN', input_shapes=2, function=Logistic(bias=-4))
color_hidden_to_output_wts = np.array([[2, -2], [-2, 2]])
output = ProcessingMechanism(name='OUTPUT', input_shapes=2, function=Logistic)
color_pathway = [color_input, color_input_to_hidden_wts, color_hidden, color_hidden_to_output_wts, output]

# Construct the word reading pathway (using the same output Mechanism)
word_input = ProcessingMechanism(name='WORD INPUT', input_shapes=2)
word_input_to_hidden_wts = np.array([[3, -3], [-3, 3]])
word_hidden = ProcessingMechanism(name='WORD HIDDEN', input_shapes=2, function=Logistic(bias=-4))
word_hidden_to_output_wts = np.array([[3, -3], [-3, 3]])
word_pathway = [word_input, word_input_to_hidden_wts, word_hidden, word_hidden_to_output_wts, output]

# Construct the task specification pathways
task_input = ProcessingMechanism(name='TASK INPUT', input_shapes=2)
task_color_wts = np.array([[4,4],[0,0]])
task_word_wts = np.array([[0,0],[4,4]])
task_color_pathway = [task_input, task_color_wts, color_hidden]
task_word_pathway = [task_input, task_word_wts, word_hidden]

# Construct the decision pathway:
decision = DDM(name='DECISION', input_format=ARRAY)
decision_pathway = [output, decision]

# Construct the Composition:
Stroop_model = Composition(name='Stroop Model')
Stroop_model.add_linear_processing_pathway(color_pathway)
Stroop_model.add_linear_processing_pathway(word_pathway)
Stroop_model.add_linear_processing_pathway(task_color_pathway)
Stroop_model.add_linear_processing_pathway(task_word_pathway)
Stroop_model.add_linear_processing_pathway(decision_pathway)
```

```{figure} ../_static/BasicsAndPrimer_Stroop_Model.svg
:width: 100%

**Stroop Model.** The full graph of the Composition above.
```

#### Running the model

Inputs are specified as a dictionary mapping `INPUT` Mechanisms to lists of
values (one per trial):

```python
red   = [1, 0]
green = [0, 1]
word  = [0, 1]
color = [1, 0]

#                                    Trial 1  Trial 2
Stroop_model.run(inputs={color_input:[red,     red   ],
                         word_input: [red,     green ],
                         task_input: [color,   color ]})
print(Stroop_model.results)
# [[array([1.]), array([2.80488344])], [array([1.]), array([3.94471513])]]
```

The DDM returns two values per trial: the **decision outcome** (1 or -1) and
the **estimated response time** (in seconds). Notice that the incongruent
trial (Trial 2) has a longer response time than the congruent trial (Trial 1).

:::{note}
On some runs, Trial 2 may return -1 (incorrect) because the DDM's default
function includes a noise term.
:::

---

### Dynamics of Execution

One of PsyNeuLink's most powerful features is simulating models with
Components that execute at **different time scales**.

In the Stroop model above, the DDM uses `DriftDiffusionAnalytical` (its
default), which computes an analytic solution in a single execution. But we
can simulate the actual integration process by switching to
`DriftDiffusionIntegrator` and specifying a termination condition:

```python
# Modify the decision Mechanism to use step-by-step integration:
decision = DDM(name='DECISION',
               input_format=ARRAY,
               reset_stateful_function_when=AtTrialStart(),
               function=DriftDiffusionIntegrator(noise=0.5, threshold=20))

Stroop_model.run(
    inputs={color_input: red, word_input: green, task_input: color},
    termination_processing={TimeScale.TRIAL: WhenFinished(decision)}
)
print(Stroop_model.results)
# [[array([[20.]]), array([[126.]])]]
```

Now the output is the threshold crossing value and the **number of time steps**
it took to get there.

#### Scheduling with Conditions

PsyNeuLink's Scheduler supports Conditions that control when Mechanisms
execute. For example, using an `LCAMechanism` for the task that must settle
before processing begins:

```python
# Use a leaky competing accumulator for the task:
task = LCAMechanism(name='TASK', input_shapes=2)

# Wait for task to execute 10 times before processing color/word:
Stroop_model.scheduler.add_condition(color_hidden, EveryNExecutions(task, 10))
Stroop_model.scheduler.add_condition(word_hidden, EveryNExecutions(task, 10))

Stroop_model.run(inputs={color_input: red, word_input: green, task_input: color})
```

Or use a **convergence criterion** instead of a fixed count:

```python
def converge(mech, thresh):
    return all(abs(v) <= thresh for v in mech.delta)

epsilon = 0.01
Stroop_model.scheduler.add_condition(color_hidden, When(converge, task, epsilon))
Stroop_model.scheduler.add_condition(word_hidden, When(converge, task, epsilon))
```

PsyNeuLink provides many pre-defined Conditions, and you can create custom
ones using any Python function.

:::{seealso}
{doc}`/explanation/scheduling-and-execution` — deep dive into time scales and Conditions
:::

---

### Control

PsyNeuLink makes it easy to add **adaptive control** — Mechanisms that monitor
output and regulate processing. Here we add conflict monitoring to the Stroop
model:

```python
# Construct a control mechanism that monitors conflict and adjusts task gain:
control = ControlMechanism(
    name='CONTROL',
    objective_mechanism=ObjectiveMechanism(
        name='Conflict Monitor',
        monitor=output,
        function=Energy(input_shapes=2, matrix=[[0,-2.5],[-2.5,0]])
    ),
    default_allocation=[0.5],
    control_signals=[(GAIN, task)]
)

# Assign it as the Composition's controller:
Stroop_model = Composition(name='Stroop Model', controller=control)
```

What this does:

1. The **ObjectiveMechanism** monitors the `output` Mechanism and computes
   conflict using the `Energy` function
2. The **ControlMechanism** receives the conflict signal and uses it to
   adjust the `gain` parameter of the `task` Mechanism
3. PsyNeuLink automatically creates the necessary Projections

```{figure} ../_static/BasicsAndPrimer_Stroop_Model_Control.svg
:width: 50%

**Stroop Model with Controller.**
```

#### Running with control

```python
# Setup
task.initial_value = [0.5, 0.5]
task.reset_stateful_function_when = AtTrialStart()

np.set_printoptions(precision=2)
global t
t = 0
def print_after():
    global t
    print(f'\nEnd of trial {t}:')
    print(f'\t\t\t\tcolor  word')
    print(f'\ttask:\t\t{task.value[0]}')
    print(f'\ttask gain:\t   {task.parameter_ports[GAIN].value}')
    print(f'\t\t\t\tred   green')
    print(f'\toutput:\t\t{output.value[0]}')
    print(f'\tdecision:\t{decision.value[0]}{decision.value[1]}')
    print(f'\tconflict:\t  {control.objective_mechanism.value[0]}')
    t += 1

# Run for 4 trials of incongruent stimuli
num_trials = 4
stimuli = {color_input: [red]*num_trials,
           word_input:  [green]*num_trials,
           task_input:  [color]*num_trials}
Stroop_model.run(inputs=stimuli, call_after_trial=print_after)
```

**Output:**

```text
End of trial 0:
                color  word
    task:       [ 0.67  0.51]
    task gain:     [ 0.5]
                red   green
    output:     [ 0.28  0.72]
    decision:   [-1.][ 2.36]
    conflict:     [ 0.51]

End of trial 1:
                color  word
    task:       [ 0.81  0.4 ]
    task gain:     [ 0.51]
                red   green
    output:     [ 0.38  0.62]
    decision:   [-1.][ 3.33]
    conflict:     [ 0.59]

End of trial 2:
                color  word
    task:       [ 0.97  0.19]
    task gain:     [ 0.59]
                red   green
    output:     [ 0.55  0.45]
    decision:   [ 1.][ 3.97]
    conflict:     [ 0.62]

End of trial 3:
                color  word
    task:       [ 1.    0.04]
    task gain:     [ 0.62]
                red   green
    output:     [ 0.65  0.35]
    decision:   [ 1.][ 2.95]
    conflict:     [ 0.57]
```

**What's happening:** Initially, control is low (`0.5`), so the task
representation is weak and the model gives the **wrong answer** ([-1] = green
instead of red). But conflict is detected (`0.51`), which increases control,
which increases task gain, which strengthens the task representation — until
the model eventually gives the **correct answer** ([1] = red) by Trial 2.

```{figure} ../_static/BasicsAndPrimer_Stroop_Model_movie.gif
:width: 75%

**Animation of Stroop Model with Controller.** Generated using
`animate={"show_controller": True}` in the `run()` call.
```

:::{seealso}
- {doc}`control` — focused tutorial on control
- {doc}`/explanation/control-theory` — theoretical foundations
:::

---

### Parameters

Every Component has **parameters** that determine its behavior. Parameters in
PsyNeuLink are instances of a special `Parameters` class that supports:

- **Statefulness** — different values in different execution contexts
- **History** — access to previous values
- **Modulation** — values can be adjusted by ControlMechanisms

#### Accessing parameter values

Use **dot notation** for the most recent value:

```python
output.value[0]      # Most recent value of the output Mechanism
decision.value[0]    # Most recent value of the decision Mechanism
```

Use the **`get()` method** to access values in a specific context:

```python
output.parameters.value.get('Stroop Model - Conflict Monitoring')[0]
# [ 0.65  0.35]
```

Access **previous values** with `get_previous()`:

```python
output.parameters.value.get_previous('Stroop Model - Conflict Monitoring')[0]
# [ 0.55  0.45]    # Value from the prior trial
```

Set the history length to keep more previous values:

```python
output.parameters.value.history_max_length = 3
```

#### Setting parameter values

| Method | When to use |
|--------|-------------|
| `component.param = value` | Simple case — applies to the most recent context |
| `component.parameters.param.set(value, context)` | When you need to target a specific context |

**Dot notation example:**

```python
m = ProcessingMechanism(name='m')
comp1 = Composition(name='comp1', nodes=[m])
comp1.run(inputs={m: 1})
# [array([1.])]

m.function.slope.base = 2
comp1.run(inputs={m: 1})
# [array([2.])]

# But a NEW context is unaffected (statefulness):
comp2 = Composition(name='comp2', nodes=[m])
comp2.run(inputs={m: 1})
# [array([1.])]
```

**`set()` method example** (targeting a specific context):

```python
m.function_parameters.slope.set(2, comp1)
comp1.run({m: [1]})
# [array([2.])]    — changed
comp2.run({m: [1]})
# [array([1.])]    — unchanged
```

:::{warning}
Setting a parameter **before** any execution (or without specifying a context)
changes the **baseline** value, which propagates to all future contexts.
:::

#### Function parameters vs. Component parameters

A Component's `value` is its own parameter. But the Component's `function`
(e.g., `Logistic`) also has parameters (`gain`, `bias`). Access them through
the function:

```python
output.function.gain.base        # 1.0
output.function.parameters.gain.get()  # 1.0
```

#### Modulable parameters

When a parameter is **modulated** by a ControlMechanism, it has both a `base`
value and a `modulated` value:

```python
task.function.gain
# (Logistic Logistic Function-5):
#     gain.base: 1.0
#     gain.modulated: [0.55]

task.function.gain.base       # 1.0  (original value)
task.function.gain.modulated  # [0.55]  (after control)
```

:::{note}
Some parameters are modulable but not yet modulated (e.g., when their default
value is `None`). In that case, dot notation behaves normally.
:::

:::{seealso}
{doc}`/explanation/parameters-and-state` — comprehensive discussion of parameters
:::

---

### Displaying and Logging Values

#### Displaying values during execution

The `run()` method has hooks for custom functions at various points:

- `call_before_trial` / `call_after_trial`
- `call_before_pass` / `call_after_pass`

The `print_after` function in the Control example above uses
`call_after_trial` to display Mechanism values after each trial.

#### Logging

PsyNeuLink has built-in logging for tracking any parameter:

```python
# Enable logging:
task.log.set_log_conditions(VALUE)
control.log.set_log_conditions(VARIABLE)
control.log.set_log_conditions(VALUE)

# After running, print the log:
Stroop_model.log.print_entries(display=[TIME, VALUE])
```

**Output** (first two trials):

```text
Log for Stroop Model:

Logged Item:   Time          Value

'CONTROL'      0:0:10:0     [[0.51]]
'CONTROL'      0:1:10:0     [[0.59]]
...

'TASK'         0:0:0:1      [[0.57 0.56]]
'TASK'         0:0:1:1      [[0.58 0.55]]
'TASK'         0:0:2:1      [[0.59 0.55]]
...
'TASK'         0:0:9:1      [[0.67 0.51]]
'TASK'         0:1:0:1      [[0.68 0.5 ]]
...
```

Time is reported as `run:trial:pass:time_step`. The `control` Mechanism has
one entry per trial; the `task` Mechanism has ten (because of the scheduling
Conditions).

Logs can be exported as **numpy arrays**, **dictionaries**, or **CSV**:

```python
Stroop_model.log.nparray()              # numpy array
Stroop_model.log.nparray_dictionary()   # dict of arrays
Stroop_model.log.csv()                  # CSV format
```

:::{seealso}
{doc}`/howto/log-and-report` — practical guide to logging and reporting
:::

---

### Learning

PsyNeuLink supports learning in two ways:

| Approach | Best for | Speed |
|----------|----------|-------|
| **Native** (LearningMechanisms) | Story-boarding, illustrating process flow, modularity | Slower |
| **AutodiffComposition** (PyTorch) | Large-scale training, performance | ~1000x faster |

#### Native learning: XOR example

```python
# Build a 3-layer network:
input = ProcessingMechanism(name='Input', default_variable=np.zeros(2))
hidden = ProcessingMechanism(name='Hidden', default_variable=np.zeros(10), function=Logistic())
output = ProcessingMechanism(name='Output', default_variable=np.zeros(1), function=Logistic())
input_weights = MappingProjection(name='Input Weights', matrix=np.random.rand(2, 10))
output_weights = MappingProjection(name='Output Weights', matrix=np.random.rand(10, 1))

# Add backpropagation learning:
xor_comp = Composition('XOR Composition')
learning_components = xor_comp.add_backpropagation_learning_pathway(
    pathway=[input, input_weights, hidden, output_weights, output]
)
target = learning_components[TARGET_MECHANISM]

# Train:
xor_inputs = {'stimuli': [[0,0], [0,1], [1,0], [1,1]],
              'targets': [[0],   [1],   [1],   [0]  ]}
xor_comp.learn(inputs={input: xor_inputs['stimuli'],
                       target: xor_inputs['targets']})
```

```{figure} ../_static/BasicsAndPrimer_XOR_Model_fig.svg
:width: 100%

**XOR Model.** Orange items are learning components created automatically.
Diamonds represent MappingProjections (shown as nodes so LearningProjections
can be displayed).
```

#### Rumelhart semantic network

More complex networks can be built by calling `add_backpropagation_learning_pathway`
multiple times:

```python
# Network structure:
#   Representation  Property  Quality  Action
#            \________\_______/_______/
#                         |
#                  Relations_Hidden
#                    _____|_____
#                   /           \
#    Representation_Hidden  Relations_Input
#                /
#    Representation_Input

rep_in = pnl.ProcessingMechanism(input_shapes=10, name='REP_IN')
rel_in = pnl.ProcessingMechanism(input_shapes=11, name='REL_IN')
rep_hidden = pnl.ProcessingMechanism(input_shapes=4, function=Logistic, name='REP_HIDDEN')
rel_hidden = pnl.ProcessingMechanism(input_shapes=5, function=Logistic, name='REL_HIDDEN')
rep_out = pnl.ProcessingMechanism(input_shapes=10, function=Logistic, name='REP_OUT')
prop_out = pnl.ProcessingMechanism(input_shapes=12, function=Logistic, name='PROP_OUT')
qual_out = pnl.ProcessingMechanism(input_shapes=13, function=Logistic, name='QUAL_OUT')
act_out = pnl.ProcessingMechanism(input_shapes=14, function=Logistic, name='ACT_OUT')

comp = Composition(name='Rumelhart Semantic Network')
comp.add_backpropagation_learning_pathway(pathway=[rel_in, rel_hidden])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, rep_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, prop_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, qual_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, act_out])
comp.add_backpropagation_learning_pathway(pathway=[rep_in, rep_hidden, rel_hidden])
```

```{figure} ../_static/BasicsAndPrimer_Rumelhart_Network.svg
:width: 75%

**Rumelhart Semantic Network.** Orange items are learning components.
```

:::{tip}
For faster training, replace `Composition` with `AutodiffComposition` — it
uses PyTorch under the hood and can be up to **1000x faster**.
:::

:::{seealso}
- {doc}`learning` — focused tutorial on learning
- {doc}`/howto/use-pytorch-models` — how to use AutodiffComposition
:::

---

### Customization

A Mechanism can be assigned **any Python function**, as long as its first
argument accepts input shaped like the Mechanism's variable:

```python
def my_sinusoidal_fct(input=[[0],[0]], phase=0, amplitude=1):
    frequency = input[0]
    time = input[1]
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)

my_wave_mech = pnl.ProcessingMechanism(
    default_variable=[[0],[0]],
    function=my_sinusoidal_fct
)
```

When assigned to a Mechanism, the Python function is automatically wrapped as
a `UserDefinedFunction`. This integrates it with PsyNeuLink — its parameters
(`phase`, `amplitude`) become available for control:

```python
control = ControlMechanism(
    control_signals=[('phase', my_wave_mech),
                     ('amplitude', my_wave_mech)]
)
```

This makes PsyNeuLink highly extensible. Functions from other environments
(e.g., complex learning models) can be wrapped and integrated into a
PsyNeuLink model.

---

## Next steps

- {doc}`mechanisms-and-functions` — deep dive into Mechanism types and Functions
- {doc}`compositions` — Compositions, scheduling, and nested models
- {doc}`control` — adaptive control in detail
- {doc}`learning` — native learning and PyTorch integration
- {doc}`/howto/installation` — setting up your development environment
