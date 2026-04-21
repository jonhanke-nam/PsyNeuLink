(mechanisms-and-functions)=
# Mechanisms and Functions

This tutorial covers the two foundational building blocks of every PsyNeuLink model:
**Mechanisms**, which are the computational units, and **Functions**, which define what
computation each Mechanism performs.

## What is a Mechanism?

A {class}`Mechanism` is the basic processing element in PsyNeuLink -- the "block" in a
block-diagram model. Every Mechanism:

1. Receives input through one or more {class}`InputPorts <InputPort>`.
2. Applies a {class}`Function` to transform that input.
3. Produces output through one or more {class}`OutputPorts <OutputPort>`.

Mechanisms fall into two broad categories:

- **ProcessingMechanisms** -- directly transform and transmit information.
- **ModulatoryMechanisms** -- modify or regulate the processing done by other
  Mechanisms (for example, {class}`ControlMechanism` and {class}`LearningMechanism`).

This tutorial focuses on ProcessingMechanisms. ModulatoryMechanisms are covered in the
{doc}`control` and {doc}`learning` tutorials.

## ProcessingMechanisms

A {class}`ProcessingMechanism` is the most general-purpose Mechanism. By default it uses a
{class}`Linear` function, which simply multiplies the input by a slope and adds an intercept:

```python
import psyneulink as pnl

# A ProcessingMechanism with 5-element input and the default Linear function
input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
result = input_layer.execute([1.0, 2.0, 3.0, 4.0, 5.0])
print(result)
# [[1. 2. 3. 4. 5.]]  -- Linear with slope=1 and intercept=0 is the identity
```

You can assign a different function to change the transformation:

```python
# A ProcessingMechanism that applies a Logistic (sigmoid) function
hidden_layer = pnl.ProcessingMechanism(
    input_shapes=2,
    function=pnl.Logistic,
    name='Hidden'
)
result = hidden_layer.execute([0.0, 2.0])
print(result)
# [[0.5, 0.88079708]]
```

### Common ProcessingMechanism Types

PsyNeuLink provides several specialized ProcessingMechanism subclasses:

| Mechanism | Purpose |
|-----------|---------|
| {class}`ProcessingMechanism` | General-purpose; accepts any compatible function |
| {class}`TransferMechanism` | Like ProcessingMechanism, with added integrator and termination features |
| {class}`IntegratorMechanism` | Accumulates input over time using an integrator function |
| {class}`DDM` | Implements drift-diffusion decision processes |
| {class}`LCAMechanism` | Leaky competing accumulator for evidence accumulation |
| {class}`ObjectiveMechanism` | Evaluates the output of other Mechanisms (used by controllers) |

### Specifying Input Shape

The `input_shapes` argument determines the size of the input array the Mechanism expects.
You can alternatively use `default_variable` to specify the exact shape and initial value:

```python
# These two are equivalent -- both create a Mechanism expecting a 3-element input:
m1 = pnl.ProcessingMechanism(input_shapes=3)
m2 = pnl.ProcessingMechanism(default_variable=[[0, 0, 0]])

# For multi-port Mechanisms, default_variable can specify multiple input arrays:
m3 = pnl.ProcessingMechanism(default_variable=[[0, 0], [0, 0, 0]])
# m3 has two InputPorts: one expecting a 2-element array, one expecting a 3-element array
```

## Functions

Every Mechanism has a {attr}`function <Mechanism_Base.function>` that defines the computation it
performs. PsyNeuLink provides a rich library of built-in {class}`Functions <Function>`:

### Transfer Functions

Transfer functions map an input array to an output array of the same size, element-wise:

| Function | Description |
|----------|-------------|
| {class}`Linear` | `slope * x + intercept` (default for ProcessingMechanism) |
| {class}`Logistic` | Sigmoid: $\frac{1}{1 + e^{-gain(x - bias)}}$ |
| {class}`Tanh` | Hyperbolic tangent |
| {class}`ReLU` | Rectified linear unit |
| {class}`Exponential` | Exponential function |
| {class}`SoftMax` | Normalizes an array to a probability distribution |

Example with configurable parameters:

```python
# Create a Logistic function with custom gain and bias
logistic_mech = pnl.ProcessingMechanism(
    input_shapes=3,
    function=pnl.Logistic(gain=2.0, bias=-1.0),
    name='Logistic Layer'
)
result = logistic_mech.execute([0.0, 0.5, 1.0])
print(result)
```

### Combination Functions

Combination functions take multiple arrays and combine them:

| Function | Description |
|----------|-------------|
| {class}`LinearCombination` | Weighted sum or product of arrays |
| {class}`Reduce` | Sums or averages across elements |

### Integrator Functions

Integrator functions accumulate values over repeated executions:

| Function | Description |
|----------|-------------|
| {class}`AdaptiveIntegrator` | Exponentially weighted running average |
| {class}`DriftDiffusionIntegrator` | Noisy evidence accumulation (for DDM) |
| {class}`FitzHughNagumoIntegrator` | Neural oscillator dynamics |

### Statistic and Learning Functions

| Function | Description |
|----------|-------------|
| {class}`Energy` | Computes energy of an array (used in Hopfield/Boltzmann models) |
| {class}`Stability` | Computes stability (entropy, energy) |
| {class}`BackPropagation` | Backpropagation weight update |
| {class}`Hebbian` | Hebbian learning rule |

## Executing Mechanisms Standalone

You can execute any Mechanism on its own, outside of a Composition, using the
{meth}`execute <Mechanism_Base.execute>` method. This is useful for testing and
exploration:

```python
import numpy as np
import psyneulink as pnl

# Create a mechanism with a Logistic function
mech = pnl.ProcessingMechanism(
    input_shapes=5,
    function=pnl.Logistic,
    name='Output'
)

# Execute with a sample input
result = mech.execute([0, 2.5, 10.9, 2, 7.6])
print(result)
# [[0.5, 0.92414182, 0.99998154, 0.88079708, 0.9994998]]
```

Each call to `execute()` runs the Mechanism once and returns its output.

## Function Parameters

Functions have parameters that control their behavior. These parameters can be accessed
and modified through the Mechanism:

```python
mech = pnl.ProcessingMechanism(
    input_shapes=3,
    function=pnl.Logistic(gain=1.0, bias=0.0),
    name='my_mech'
)

# Access function parameters
print(mech.function.gain.base)   # 1.0
print(mech.function.bias.base)   # 0.0

# Modify a parameter
mech.function.slope.base = 2.0

# Parameters can also be accessed through the parameters attribute
print(mech.function.parameters.gain.get())
```

:::{seealso}
The {ref}`BasicsAndPrimer_Parameters` section of the Basics and Primer covers parameter
access, statefulness, and modulation in detail.
:::

## Custom Python Functions

A Mechanism can use any Python function, as long as the function's first argument accepts
an array matching the Mechanism's input shape. When a Python function is assigned, PsyNeuLink
wraps it as a {class}`UserDefinedFunction`:

```python
import numpy as np
import psyneulink as pnl

def my_sinusoidal_fct(input=[[0],[0]], phase=0, amplitude=1):
    frequency = input[0]
    time = input[1]
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)

my_wave_mech = pnl.ProcessingMechanism(
    default_variable=[[0],[0]],
    function=my_sinusoidal_fct,
    name='Sinusoidal'
)

# The phase and amplitude parameters are automatically made available
# for control by a ControlMechanism:
control = pnl.ControlMechanism(
    control_signals=[('phase', my_wave_mech),
                     ('amplitude', my_wave_mech)]
)
```

The key advantages of this wrapping:
- The function's first argument becomes the Mechanism's input (received from other
  Mechanisms via Projections).
- Additional keyword arguments become parameters that can be modulated by
  {class}`ControlMechanisms <ControlMechanism>`.
- The function integrates seamlessly with the rest of PsyNeuLink's infrastructure.

## ModulatoryMechanisms

While ProcessingMechanisms transform information directly, {class}`ModulatoryMechanisms <ModulatoryMechanism>`
modify *how* other Mechanisms process information. The two main types are:

**ControlMechanisms** regulate the parameters of other Mechanisms. For example, a
{class}`ControlMechanism` might adjust the `gain` of a Logistic function based on
detected conflict, implementing cognitive control. See {doc}`control` for details.

**LearningMechanisms** modify the weights of {class}`MappingProjections <MappingProjection>`
based on error signals, implementing learning algorithms like backpropagation and
Hebbian learning. See {doc}`learning` for details.

## Next Steps

Now that you understand Mechanisms and Functions, learn how they connect to each other:

- {doc}`projections-and-pathways` -- connecting Mechanisms with Projections
- {doc}`compositions` -- assembling Mechanisms into executable models
