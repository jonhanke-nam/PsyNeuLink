(control-theory)=
# Control Theory in PsyNeuLink

A distinctive feature of PsyNeuLink is its first-class support for *control*
-- the ability of a model to evaluate its own processing and dynamically
regulate its parameters. This page explains the theoretical foundations and
practical mechanics of control in PsyNeuLink.

## Processing vs. modulation revisited

Before diving into control, it is worth re-establishing the distinction between
processing and modulation, since control is a specific form of modulation.

**Processing** is the direct flow of information through a model: inputs arrive
at ProcessingMechanisms, are transformed by their Functions, transmitted by
MappingProjections, and eventually produce outputs.

**Modulation** is a secondary flow of information that *regulates* processing.
Modulatory Components do not contribute to the primary information flow;
instead, they adjust the *parameters* that govern how processing operates.
This mirrors a core principle in neuroscience: the distinction between
information-carrying neural pathways and neuromodulatory systems (e.g.,
dopaminergic, noradrenergic) that tune the gain, threshold, or other operating
characteristics of those pathways.

PsyNeuLink implements two forms of modulation:

1. **Control** -- adjusting operating parameters of Mechanisms (e.g., gain,
   threshold, noise) via ControlMechanisms and ControlProjections.
2. **Learning** -- adjusting connection weights (matrices of MappingProjections)
   via LearningMechanisms and LearningProjections.

This page focuses on control. See {doc}`learning-and-autodiff` for learning.

## The control loop

A typical control loop in PsyNeuLink involves three components:

```
ObjectiveMechanism  --->  ControlMechanism  --->  ParameterPort(s)
   (evaluates              (computes               (modulated
    processing              control                 parameter
    outcome)                signal)                 of target)
```

### ObjectiveMechanism

An {class}`ObjectiveMechanism` monitors the output of one or more
ProcessingMechanisms and evaluates it according to some criterion. For
example, it might compute the *conflict* (degree of co-activation) in a
response layer, the *error* between output and a target, or the *reward*
associated with a decision.

The ObjectiveMechanism's `monitor` parameter specifies which Mechanism outputs
to observe, and its {class}`Function` defines how to evaluate them. Common
choices include:

- **Energy** -- computes the degree of co-activation (conflict) among elements,
  using a weight matrix that defines which elements compete.
- **Distance** -- computes the distance between two vectors (e.g., output and
  target).
- **Stability** -- computes the stability of a network's state.

```python
objective = ObjectiveMechanism(
    name='Conflict Monitor',
    monitor=output_mech,
    function=Energy(input_shapes=2, matrix=[[0, -2.5], [-2.5, 0]])
)
```

PsyNeuLink automatically creates the necessary MappingProjections from the
monitored Mechanism(s) to the ObjectiveMechanism.

### ControlMechanism

A {class}`ControlMechanism` receives input from an ObjectiveMechanism (or
directly from other sources) and uses it to compute control signals. Its
`control_signals` parameter specifies which parameters of which Mechanisms
to regulate.

```python
control = ControlMechanism(
    name='CONTROL',
    objective_mechanism=objective,
    default_allocation=[0.5],
    control_signals=[(GAIN, task_mech)]
)
```

This creates a ControlMechanism that:

1. Receives the conflict value from the ObjectiveMechanism.
2. Uses it (via its Function, which defaults to a Linear transfer) to compute
   a control signal.
3. Sends that signal via a {class}`ControlProjection` to the
   {class}`ParameterPort` for the `gain` parameter of `task_mech`'s Logistic
   function.

The ControlMechanism is typically assigned as the Composition's `controller`:

```python
comp = Composition(name='My Model', controller=control)
```

When assigned as the controller, the ControlMechanism executes at the end (or
beginning) of each TRIAL, after (or before) all other Mechanisms in the
Composition have executed.

### How control signals modulate parameters via ParameterPorts

The link between a ControlMechanism and the parameter it regulates passes
through a {class}`ParameterPort`. Here is the chain in detail:

1. The ControlMechanism's {class}`ControlSignal` (a specialized OutputPort)
   computes a control allocation value.
2. A {class}`ControlProjection` transmits this value to the target
   ParameterPort.
3. The ParameterPort combines the parameter's *base value* with the
   modulatory input using its `function` (typically multiplication, but
   configurable). The result is the *modulated value* of the parameter.
4. When the target Mechanism next executes, it uses the modulated value
   rather than the base value.

This means that changing a ControlMechanism's output does not permanently alter
the parameter -- it modulates it for each execution. The base value remains
unchanged and can be accessed separately (see {doc}`parameters-and-state`).

## The conflict monitoring example

The Stroop model from the Basics and Primer provides a concrete illustration.
The model implements color naming and word reading pathways that converge on a
shared output layer, followed by a DDM decision mechanism. A ControlMechanism
monitors conflict in the output layer and uses it to adjust the gain of a task
representation mechanism:

```python
# Construct the control mechanism
control = ControlMechanism(
    name='CONTROL',
    objective_mechanism=ObjectiveMechanism(
        name='Conflict Monitor',
        monitor=output,
        function=Energy(input_shapes=2, matrix=[[0, -2.5], [-2.5, 0]])
    ),
    default_allocation=[0.5],
    control_signals=[(GAIN, task)]
)

# Add it as the Composition's controller
Stroop_model = Composition(name='Stroop Model', controller=control)
```

When the model is run over multiple trials with an incongruent stimulus
(e.g., the word "green" displayed in red ink, with a "color naming"
instruction):

1. **Trial 0:** Control starts low (0.5). The task representation is weak, so
   the model gives the wrong answer (driven by the stronger word pathway).
   Conflict in the output layer is moderate (0.51).
2. **Trial 1:** The conflict from Trial 0 increases the control signal
   slightly (0.51), strengthening the task representation. The model still
   gives the wrong answer but conflict rises further (0.59).
3. **Trial 2:** Higher control (0.59) produces a stronger task representation.
   The model now gives the correct answer. Conflict is 0.62.
4. **Trial 3:** Even higher control (0.62) firmly commits the task
   representation. The correct answer is given with lower conflict (0.57).

This demonstrates the feedback loop: conflict drives control up, which
strengthens task representation, which reduces conflict over subsequent trials.

## Expected Value of Control (EVC) framework

Beyond reactive conflict monitoring, PsyNeuLink supports more sophisticated
forms of control through the {class}`OptimizationControlMechanism`. This
Mechanism implements the Expected Value of Control (EVC) framework
([Shenhav et al., 2013](https://royalsocietypublishing.org/doi/full/10.1098/rstb.2013.0478)),
which posits that the brain selects control signals to maximize the expected
*value* of controlled processing minus the *cost* of exerting control.

### How it works

The OptimizationControlMechanism:

1. **Defines a search space** over possible control allocations (values of each
   ControlSignal).
2. **Runs internal simulations** of the model for each candidate allocation,
   using the model itself (in a separate execution context, so the primary
   state is not disturbed).
3. **Evaluates each outcome** using an objective function that typically
   combines the expected reward/accuracy with a cost term for the control
   signal magnitude.
4. **Selects the allocation** that maximizes the expected value of control.

The optimization can use various search strategies, including grid search
(evaluating a discrete set of allocations) and gradient-based optimization.

### Model-based vs. model-free control

PsyNeuLink's control framework naturally supports both model-based and
model-free approaches:

- **Model-based control** (as in the EVC framework): The controller runs
  internal simulations of the model to predict outcomes under different
  control allocations. This is computationally expensive but allows the
  controller to anticipate and proactively adjust to changing task demands.

- **Model-free control** (as in the conflict monitoring example): The
  controller reacts to directly observed signals (e.g., conflict) without
  internal simulation. This is computationally cheap but purely reactive --
  the controller can only respond to what has already happened, not
  anticipate what will happen.

Both approaches use the same architectural components (ControlMechanisms,
ObjectiveMechanisms, ControlProjections); the difference lies in the
complexity of the ControlMechanism's function and whether it invokes
internal simulations.

## What can be controlled

ControlMechanisms can regulate any *modulable parameter* of any Mechanism or
Projection in the Composition. Common targets include:

| Parameter                          | Effect of modulation                                     |
|------------------------------------|----------------------------------------------------------|
| `gain` of a Logistic function      | Increases or decreases the sharpness of the sigmoid      |
| `threshold` of a DDM               | Adjusts the speed-accuracy tradeoff                      |
| `noise` of an integrator           | Adjusts stochasticity of processing                      |
| `rate` of an integrator            | Adjusts the speed of integration                         |
| `bias` of a transfer function      | Shifts the baseline activation                           |
| `matrix` of a MappingProjection    | Scales or transforms connection weights                  |

A single ControlMechanism can regulate multiple parameters simultaneously,
using separate ControlSignals for each. Each ControlSignal can have its own
cost function and allocation range.

## Gating: a specialized form of control

{class}`GatingMechanism` is a subtype of ControlMechanism that specifically
modulates the *input* or *output* of a Mechanism (via its InputPorts or
OutputPorts) rather than its function parameters. Gating is conceptually
equivalent to multiplying a Mechanism's input or output by a scalar gate
value, and is useful for implementing attention-like mechanisms that
selectively enable or suppress processing pathways.

## Timing of control

By default, the controller executes at the *end* of each TRIAL, after all
other Mechanisms have executed. This means its control signals take effect on
the *next* TRIAL. This is appropriate for models of reactive control (e.g.,
conflict monitoring), where the controller responds to the outcome of the
current trial.

The controller can also be configured to execute at the *start* of each TRIAL,
before processing begins. This is appropriate for models of proactive control,
where the controller sets parameters in anticipation of the current trial's
demands (based on prior experience or internal simulation).

## Summary

- **Control** in PsyNeuLink implements the modulation of processing parameters
  by dedicated ControlMechanisms, mirroring neuromodulatory regulation in the
  brain.
- The basic control loop runs from an **ObjectiveMechanism** (which evaluates
  processing) through a **ControlMechanism** (which computes control signals)
  to **ParameterPorts** (which modulate target parameters).
- The **EVC framework** extends this with model-based optimization, using
  internal simulations to select the control allocation that maximizes expected
  value minus cost.
- **Gating** is a specialized form of control that modulates inputs or outputs
  rather than function parameters.
- Control operates on the **TRIAL time scale**, with signals taking effect
  either at the end or beginning of each TRIAL.
