# Add control to a model

PsyNeuLink makes it straightforward to add control mechanisms that monitor the
output of processing mechanisms and use the results to regulate parameters of
other mechanisms. This guide walks through constructing a
{class}`ControlMechanism`, connecting it via an {class}`ObjectiveMechanism`,
and configuring {class}`ControlSignal` projections.

## Core concepts

- **{class}`ControlMechanism`** -- evaluates information from one or more
  sources and generates control signals that modulate parameters of other
  mechanisms.
- **{class}`ObjectiveMechanism`** -- monitors specified output(s) of
  processing mechanisms and computes a scalar value (e.g., conflict or reward)
  that drives the ControlMechanism.
- **{class}`ControlSignal`** -- a signal sent from a ControlMechanism to one
  or more {class}`ParameterPort` objects, modifying parameter values such as
  `gain`, `bias`, or `noise`.

## Example: conflict monitoring in the Stroop model

Building on the Stroop model from {doc}`build-a-feedforward-network`, we add a
conflict-monitoring controller that adjusts the gain of a task mechanism based
on response conflict.

### Step 1 -- Create the processing components

```python
import numpy as np
import psyneulink as pnl

# Color naming pathway
color_input = pnl.ProcessingMechanism(name='COLOR INPUT', input_shapes=2)
color_hidden = pnl.ProcessingMechanism(
    name='COLOR HIDDEN', input_shapes=2, function=pnl.Logistic(bias=-4)
)
output = pnl.ProcessingMechanism(name='OUTPUT', input_shapes=2, function=pnl.Logistic)
color_pathway = [color_input, np.array([[2,-2],[-2,2]]),
                 color_hidden, np.array([[2,-2],[-2,2]]), output]

# Word reading pathway
word_input = pnl.ProcessingMechanism(name='WORD INPUT', input_shapes=2)
word_hidden = pnl.ProcessingMechanism(
    name='WORD HIDDEN', input_shapes=2, function=pnl.Logistic(bias=-4)
)
word_pathway = [word_input, np.array([[3,-3],[-3,3]]),
                word_hidden, np.array([[3,-3],[-3,3]]), output]

# Task mechanism -- an LCA that settles before downstream processing
task = pnl.LCAMechanism(name='TASK', input_shapes=2)
task_color_pathway = [task, np.array([[4,4],[0,0]]), color_hidden]
task_word_pathway  = [task, np.array([[0,0],[4,4]]), word_hidden]

# Decision mechanism
decision = pnl.DDM(name='DECISION', input_format=pnl.ARRAY)
decision_pathway = [output, decision]
```

### Step 2 -- Create the ControlMechanism

The `ControlMechanism` constructor takes:

- **objective_mechanism** -- an {class}`ObjectiveMechanism` that monitors
  processing output and computes a value the controller uses as input.
- **default_allocation** -- the initial control signal value.
- **control_signals** -- a list of `(parameter_name, mechanism)` tuples
  specifying which parameters to modulate.

```python
control = pnl.ControlMechanism(
    name='CONTROL',
    objective_mechanism=pnl.ObjectiveMechanism(
        name='Conflict Monitor',
        monitor=output,
        function=pnl.Energy(input_shapes=2, matrix=[[0, -2.5], [-2.5, 0]])
    ),
    default_allocation=[0.5],
    control_signals=[(pnl.GAIN, task)]
)
```

Here the {class}`ObjectiveMechanism` uses the {class}`Energy` function to
compute conflict -- the degree of co-activation between competing response
units in the `output` mechanism. That conflict value is sent to the
`ControlMechanism`, which maps it to a gain value applied to the `task`
mechanism's {class}`Logistic` function.

PsyNeuLink automatically creates:

- A {class}`MappingProjection` from `output` to the ObjectiveMechanism
- A {class}`MappingProjection` from the ObjectiveMechanism to the
  ControlMechanism
- A {class}`ControlProjection` from the ControlMechanism to the `gain`
  {class}`ParameterPort` of the `task` mechanism

### Step 3 -- Assemble the Composition

Pass the control mechanism as the **controller** of the Composition:

```python
Stroop_model = pnl.Composition(name='Stroop Model', controller=control)

Stroop_model.add_linear_processing_pathway(color_pathway)
Stroop_model.add_linear_processing_pathway(word_pathway)
Stroop_model.add_linear_processing_pathway(task_color_pathway)
Stroop_model.add_linear_processing_pathway(task_word_pathway)
Stroop_model.add_linear_processing_pathway(decision_pathway)
```

Visualize the full model with the controller visible:

```python
Stroop_model.show_graph(show_controller=True)
```

### Step 4 -- Configure execution and run

Reset the task mechanism at the start of each trial and run for several
trials:

```python
task.initial_value = [0.5, 0.5]
task.reset_stateful_function_when = pnl.AtTrialStart()

red   = [1, 0]
green = [0, 1]
color = [1, 0]

num_trials = 4
stimuli = {
    color_input: [red]   * num_trials,
    word_input:  [green] * num_trials,
    task:        [color] * num_trials,
}

Stroop_model.run(inputs=stimuli)
print(Stroop_model.results)
```

Because the controller executes at the end of each trial by default, its
effect appears on the *next* trial. Over successive incongruent trials the
conflict signal rises, the controller increases the gain on the task
mechanism, and the task representation strengthens -- improving accuracy.

## Specifying multiple control signals

A single ControlMechanism can regulate several parameters at once:

```python
control = pnl.ControlMechanism(
    objective_mechanism=pnl.ObjectiveMechanism(monitor=output),
    control_signals=[
        (pnl.GAIN, task),
        (pnl.NOISE, color_hidden),
    ]
)
```

Each entry in `control_signals` creates a separate {class}`ControlSignal` and
corresponding {class}`ControlProjection`.

## Using OptimizationControlMechanism

For more sophisticated control that searches over possible allocations, use
{class}`OptimizationControlMechanism`. It runs internal simulations of the
model to find the control allocation that optimizes an objective:

```python
ocm = pnl.OptimizationControlMechanism(
    name='Controller',
    monitor_for_control=[(pnl.MEAN, some_output_mech)],
    control_signals=(pnl.GAIN, some_task_mech),
    agent_rep=my_composition
)
my_composition.add_controller(ocm)
```

## Controlling when the controller executes

By default a Composition's controller executes at the end of each trial. You
can change this with the **controller_mode** argument:

```python
my_comp = pnl.Composition(
    controller=control,
    controller_mode='before'  # execute controller BEFORE processing
)
```

## Next steps

- {doc}`build-a-feedforward-network` -- build the processing model this guide
  extends
- {doc}`fit-parameters` -- use {class}`ParameterEstimationComposition` to fit
  model parameters to data
- {doc}`visualize-models` -- display controllers, objective mechanisms, and
  control projections in graphs
