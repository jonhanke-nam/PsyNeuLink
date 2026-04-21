(control-tutorial)=
# Control

One of PsyNeuLink's most distinctive features is its built-in support for **control** --
Mechanisms that evaluate the output of other Mechanisms and use the result to regulate
their processing. This tutorial shows how to add control to a model, using the Stroop
task as a running example.

## Overview

Control in PsyNeuLink involves three components working together:

1. **ObjectiveMechanism** -- monitors the output of one or more Mechanisms and computes
   an evaluation (for example, the amount of response conflict).
2. **ControlMechanism** -- receives the evaluation from the ObjectiveMechanism and uses it
   to set the parameters of other Mechanisms (for example, adjusting the gain of a
   Logistic function).
3. **ControlProjections** -- carry the control signals from the ControlMechanism to the
   parameters being regulated.

PsyNeuLink automates much of the wiring when you specify these components in the
ControlMechanism's constructor.

## Setting Up the Stroop Model

Before adding control, we need the base Stroop model. Here is the full construction
(see {doc}`basics-and-primer` for a detailed walkthrough):

```python
import numpy as np
import psyneulink as pnl

# Color naming pathway
color_input = pnl.ProcessingMechanism(name='COLOR INPUT', input_shapes=2)
color_input_to_hidden_wts = np.array([[2, -2], [-2, 2]])
color_hidden = pnl.ProcessingMechanism(name='COLOR HIDDEN', input_shapes=2,
                                        function=pnl.Logistic(bias=-4))
color_hidden_to_output_wts = np.array([[2, -2], [-2, 2]])
output = pnl.ProcessingMechanism(name='OUTPUT', input_shapes=2, function=pnl.Logistic)
color_pathway = [color_input, color_input_to_hidden_wts, color_hidden,
                 color_hidden_to_output_wts, output]

# Word reading pathway
word_input = pnl.ProcessingMechanism(name='WORD INPUT', input_shapes=2)
word_input_to_hidden_wts = np.array([[3, -3], [-3, 3]])
word_hidden = pnl.ProcessingMechanism(name='WORD HIDDEN', input_shapes=2,
                                       function=pnl.Logistic(bias=-4))
word_hidden_to_output_wts = np.array([[3, -3], [-3, 3]])
word_pathway = [word_input, word_input_to_hidden_wts, word_hidden,
                word_hidden_to_output_wts, output]

# Task pathways
task_input = pnl.ProcessingMechanism(name='TASK INPUT', input_shapes=2)
task = pnl.LCAMechanism(name='TASK', input_shapes=2)
task_color_wts = np.array([[4, 4], [0, 0]])
task_word_wts = np.array([[0, 0], [4, 4]])
task_color_pathway = [task_input, task_color_wts, color_hidden]
task_word_pathway = [task_input, task_word_wts, word_hidden]

# Decision pathway
decision = pnl.DDM(name='DECISION', input_format=pnl.ARRAY)
decision_pathway = [output, decision]
```

## Constructing the ControlMechanism

The {class}`ControlMechanism` constructor lets you specify *what* to monitor, *how* to
evaluate it, and *what* to control -- all in one place:

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

Let's break this down:

### The ObjectiveMechanism

The **objective_mechanism** argument creates an {class}`ObjectiveMechanism` that:

- **Monitors** the `output` Mechanism (PsyNeuLink automatically creates the necessary
  MappingProjection from `output` to the ObjectiveMechanism).
- Uses the {class}`Energy` function to evaluate the output. The Energy function with the
  off-diagonal weight matrix `[[0, -2.5], [-2.5, 0]]` computes the degree of
  *co-activation* between the two output units -- this is a standard measure of response
  conflict (higher values mean both responses are active, indicating conflict).

### Default Allocation

The **default_allocation** sets the initial control signal value. Here, `[0.5]` means
control starts at a moderate level.

### Control Signals

The **control_signals** argument specifies which parameters to regulate. The tuple
`(GAIN, task)` tells PsyNeuLink to control the `gain` parameter of the `task`
Mechanism's {class}`Logistic` function. PsyNeuLink creates a {class}`ControlProjection`
from the ControlMechanism to the `task` Mechanism's gain {class}`ParameterPort`.

## Assigning the Controller to a Composition

The ControlMechanism is assigned as the Composition's {attr}`controller <Composition.controller>`:

```python
Stroop_model = pnl.Composition(name='Stroop Model', controller=control)
Stroop_model.add_linear_processing_pathway(color_pathway)
Stroop_model.add_linear_processing_pathway(word_pathway)
Stroop_model.add_linear_processing_pathway(task_color_pathway)
Stroop_model.add_linear_processing_pathway(task_word_pathway)
Stroop_model.add_linear_processing_pathway(decision_pathway)
```

When a ControlMechanism is the Composition's controller, it executes **at the end of each
trial**, after all other Mechanisms have run. Its output (the control signal) then takes
effect on the next trial.

:::{note}
A Composition's controller can also be configured to execute at the *start* of a trial.
:::

## Visualizing the Controlled Model

Use `show_controller=True` to see the control components in the graph:

```python
Stroop_model.show_graph(show_controller=True)
```

This displays the ObjectiveMechanism, the ControlMechanism, and the ControlProjection
to the `task` Mechanism, in addition to all the processing pathways.

```{figure} ../_static/BasicsAndPrimer_Stroop_Model_Control.svg
:width: 50%

**Stroop Model with Controller.** Generated by `Stroop_model.show_graph(show_controller=True)`.
```

## Running the Controlled Model

Configure the `task` Mechanism to reset at the beginning of each trial, then run:

```python
# Configure task resets
task.initial_value = [0.5, 0.5]
task.reset_stateful_function_when = pnl.AtTrialStart()

# Define stimuli
red   = [1, 0]
green = [0, 1]
color = [1, 0]

num_trials = 4
stimuli = {
    color_input: [red] * num_trials,
    word_input:  [green] * num_trials,
    task_input:  [color] * num_trials,
}

# Optional: print state after each trial
np.set_printoptions(precision=2)
trial_num = 0

def print_after():
    global trial_num
    print(f'\nEnd of trial {trial_num}:')
    print(f'\ttask:      {task.value[0]}')
    print(f'\ttask gain: {task.parameter_ports[pnl.GAIN].value}')
    print(f'\toutput:    {output.value[0]}')
    print(f'\tdecision:  {decision.value[0]} {decision.value[1]}')
    print(f'\tconflict:  {control.objective_mechanism.value[0]}')
    trial_num += 1

Stroop_model.run(inputs=stimuli, call_after_trial=print_after)
```

### Interpreting the Output

```text
End of trial 0:
    task:      [ 0.67  0.51]
    task gain: [ 0.5]
    output:    [ 0.28  0.72]
    decision:  [-1.] [ 2.36]
    conflict:  [ 0.51]

End of trial 1:
    task:      [ 0.81  0.4 ]
    task gain: [ 0.51]
    output:    [ 0.38  0.62]
    decision:  [-1.] [ 3.33]
    conflict:  [ 0.59]

End of trial 2:
    task:      [ 0.97  0.19]
    task gain: [ 0.59]
    output:    [ 0.55  0.45]
    decision:  [ 1.] [ 3.97]
    conflict:  [ 0.62]

End of trial 3:
    task:      [ 1.    0.04]
    task gain: [ 0.62]
    output:    [ 0.65  0.35]
    decision:  [ 1.] [ 2.95]
    conflict:  [ 0.57]
```

Here is what happens across the four trials:

- **Trial 0**: Control is low (0.5), so the `task` Mechanism's representation of the
  color instruction is weak (0.67 vs 0.51). The stronger word pathway dominates, and the
  model gives the *wrong* response (-1 = green instead of +1 = red). Conflict is moderate
  (0.51).

- **Trials 1-2**: Conflict increases control, which increases the gain of the `task`
  Mechanism. This strengthens the task representation, gradually shifting the output
  toward the correct response.

- **Trial 3**: The task representation is now strong (1.0 vs 0.04), the model gives the
  correct response (+1 = red), and conflict begins to decrease.

This demonstrates the core control loop: **conflict drives control, which drives attention,
which resolves conflict**.

## Animation

The `animate` argument generates a step-by-step animation of the Composition's execution:

```python
Stroop_model.run(inputs=stimuli, animate={"show_controller": True})
```

```{figure} ../_static/BasicsAndPrimer_Stroop_Model_movie.gif
:width: 75%

**Animation of Stroop Model with Controller.** Generated with `animate={"show_controller": True}`.
```

## Monitoring Parameter Values During Control

You can use the {attr}`modulated <ParameterPort.value>` value of a parameter to see the
effect of control:

```python
# Base value of gain (as defined in the Logistic function)
print(task.function.gain.base)
# 1.0

# Modulated value (after control has been applied)
print(task.gain.modulated)
# [0.62]
```

The base value is unchanged, but the *modulated* value reflects the effect of the
ControlProjection. See {ref}`BasicsAndPrimer_Parameters` for more on base vs. modulated
values.

## Advanced Control

PsyNeuLink supports more sophisticated forms of control beyond the simple reactive
loop shown here:

- **OptimizationControlMechanism** -- runs internal simulations to optimize control
  signals, for example to maximize the expected value of control (EVC).
- **Model-based control** -- the controller can simulate different allocations and
  choose the one that optimizes a specified outcome.
- **Multiple control signals** -- a single ControlMechanism can regulate multiple
  parameters across multiple Mechanisms simultaneously.

## Next Steps

- {doc}`learning` -- training networks with backpropagation and AutodiffComposition
- {doc}`basics-and-primer` -- full reference including the Parameters and Logging sections
