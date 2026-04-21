(parameters-and-state)=
# Parameters and State

Every Component in PsyNeuLink has a set of parameters that determine how it
operates and that record the state of its operation. While parameters can be
accessed like ordinary Python attributes, they are actually instances of a
special {class}`Parameters` class that supports statefulness across multiple
execution contexts, historical records, and modulation by other Components.
This page explains how all of this works.

## What is a parameter?

A parameter in PsyNeuLink is an attribute of a Component that:

- Has a **value** that influences computation (e.g., the `gain` of a Logistic
  function, the `matrix` of a MappingProjection).
- May be **stateful**, meaning it can simultaneously have different values in
  different execution contexts.
- May be **modulable**, meaning its effective value can be modified by a
  ModulatoryMechanism (e.g., a ControlMechanism).
- May keep a **history** of previous values.
- Can be **logged** for later analysis.

Every Component has at least a `value` parameter, which stores the result of
the Component's function after execution. The `variable` parameter stores the
input to the function. Beyond these, each Component type defines parameters
specific to its operation.

## Accessing parameter values

### Dot notation

The simplest way to access a parameter is Python dot notation:

```python
>>> output_mech.value
array([[0.65, 0.35]])
```

This returns the most recently assigned value of the parameter. For most
casual inspection, dot notation is sufficient.

### The Parameters interface

For more precise control, every Component exposes a `parameters` attribute
that provides access to all of its parameters as {class}`Parameter` objects:

```python
>>> output_mech.parameters.value
# returns the Parameter object itself

>>> output_mech.parameters.value.get()
array([[0.65, 0.35]])
```

The `get` method, called without arguments, returns the most recently assigned
value -- equivalent to dot notation. However, `get` also accepts a **context**
argument, which is essential for stateful parameters.

## Statefulness and contexts

### Why statefulness matters

PsyNeuLink can execute the same Component in multiple contexts. For example:

- A Mechanism might belong to two different Compositions, each of which runs
  it independently.
- An OptimizationControlMechanism might run internal simulations of a
  Composition to evaluate control allocations, creating additional execution
  contexts alongside the primary one.

In each context, a stateful parameter maintains an independent value. This
ensures that execution in one context does not contaminate the state in another.

### Accessing values in a specific context

To get a parameter's value in a specific context, pass the context to `get`:

```python
>>> output_mech.parameters.value.get('Stroop Model')[0]
array([0.65, 0.35])
```

The context is typically the name of the Composition in which the Mechanism was
executed.

### The baseline context

If a Component has not yet been executed in any Composition, its parameters
exist only in the *baseline* context. Setting a parameter value via dot
notation or `set()` without a context modifies the baseline. When the
Component is later executed in a new context, the baseline value is copied as
the starting value for that context.

:::{warning}
If you change a parameter's baseline value (by setting it before the Component
has been executed in any context, or by calling `set()` without a context),
the new value propagates to all *future* contexts but does not affect contexts
that have already been established.
:::

## Setting parameter values

### Dot notation

For the common case of changing a parameter for the most recent execution
context:

```python
>>> m.function.slope.base = 2
```

After this, the next execution of `m` in the same context will use `slope=2`.

:::{note}
Dot notation sets the value for the *most recent* context in which the
Component executed. If the Component has never been executed (or was only
executed standalone), dot notation sets the baseline value, which then
propagates to new contexts.
:::

### The `set` method

For explicit control over which context is affected:

```python
>>> m.function_parameters.slope.set(2, comp1)
```

This sets the slope to 2 specifically for the `comp1` context, leaving all
other contexts unchanged.

### Worked example: dot notation vs. set

```python
m = ProcessingMechanism(name='m')
comp1 = Composition(name='comp1', nodes=[m])
comp2 = Composition(name='comp2', nodes=[m])

comp1.run({m: [1]})   # returns [array([1.])]
comp2.run({m: [1]})   # returns [array([1.])]

# Dot notation affects the most recent context (comp2)
m.function.slope.base = 2
comp1.run({m: [1]})   # returns [array([1.])]  -- comp1 unaffected
comp2.run({m: [1]})   # returns [array([2.])]  -- comp2 uses new slope

# To change comp1 specifically, use set:
m.function_parameters.slope.set(3, comp1)
comp1.run({m: [1]})   # returns [array([3.])]
comp2.run({m: [1]})   # returns [array([2.])]  -- comp2 still uses 2
```

### Cautionary notes

:::{warning}
Setting a parameter via dot notation *before* a Component has been executed in
any non-default context changes the baseline value, which propagates to all
future contexts:

```python
m = ProcessingMechanism(name='m')
m.function.slope.base = 2       # changes baseline
comp1 = Composition(nodes=[m])
comp1.run({m: [1]})             # returns [array([2.])] -- new baseline propagated
```
:::

:::{warning}
Calling `set()` without specifying a context also changes the baseline, with
the same propagation behavior. However, it does *not* retroactively affect
contexts that have already been established.
:::

## Component parameters vs. Function parameters

It is important to distinguish between parameters of a Component and parameters
of its Function. Every Mechanism has a `function` attribute that is itself a
PsyNeuLink {class}`Function` -- and since Functions are Components, they have
their own parameters.

For example, a ProcessingMechanism with a Logistic function:

- **Mechanism parameters:** `value`, `variable`, `input_shapes`, etc.
- **Function parameters:** `gain`, `bias`, `offset`, etc. (specific to
  Logistic).

Function parameters can be accessed through the Mechanism:

```python
>>> output_mech.function.gain.base
1.0

>>> output_mech.function.parameters.gain.get()
1.0
```

## Modulable parameters and ParameterPorts

### What makes a parameter modulable

Some parameters are *modulable*, meaning their effective value during execution
can be modified by a ModulatoryMechanism (typically a ControlMechanism). For a
parameter to be modulable, it must have a numeric value at the time the
Component is constructed.

When a parameter is modulable, PsyNeuLink automatically creates a
{class}`ParameterPort` for it. The ParameterPort:

1. Takes the parameter's *base value* as input.
2. Receives any {class}`ControlProjection`s that modulate the parameter.
3. Combines the base value with the modulatory input using its function
   (typically multiplication).
4. Produces the *modulated value*, which is what the Component actually uses
   during execution.

### Base vs. modulated values

For modulable parameters, dot notation returns an object with both `base` and
`modulated` attributes:

```python
>>> task_mech.function.gain
(Logistic Logistic Function-5):
    gain.base: 1.0
    gain.modulated: [0.55]
```

- `gain.base` is the intrinsic value of the parameter (what you set directly).
- `gain.modulated` is the value actually used during execution, after
  ControlProjections have been applied.

The modulated value can also be accessed through the ParameterPort directly:

```python
>>> task_mech.parameter_ports[GAIN].value
[0.62]
```

:::{note}
If a parameter is modulable but not currently being modulated by any
ControlProjection, its modulated value equals its base value.
:::

### Parameters that are modulable but not modulated

Some parameters have a default value of `None` or a non-numeric value (e.g., a
function). Since ParameterPorts require numeric values, these parameters do not
get a ParameterPort at construction time, even though they are marked as
modulable in the class definition. For these parameters, dot notation behaves
the same as for non-modulable parameters (returning the value directly rather
than a base/modulated object). If you later set such a parameter to a numeric
value, you may need to reconstruct the Component to get a ParameterPort.

## Parameter history

Stateful parameters can keep a record of previous values, which is useful for
analyzing how a parameter evolves over the course of a simulation.

### Accessing previous values

```python
>>> output_mech.parameters.value.get_previous('Stroop Model')[0]
array([0.55, 0.45])
```

By default, only one previous value is stored. You can increase this by
setting `history_max_length`:

```python
>>> output_mech.parameters.value.history_max_length = 3
```

After running the model, you can access earlier values by passing an index to
`get_previous`:

```python
>>> output_mech.parameters.value.get_previous('Stroop Model', 2)[0]
array([0.38, 0.62])
```

Here, `2` means "two values before the current one."

## Logging

PsyNeuLink provides a logging system that can record the value of any parameter
at each time step of execution.

### Setting up logging

```python
task_mech.log.set_log_conditions(VALUE)
control.log.set_log_conditions(VARIABLE)
control.log.set_log_conditions(VALUE)
```

### Viewing log output

After running the model:

```python
comp.log.print_entries(display=[TIME, VALUE])
```

This produces output like:

```
Log for Stroop Model:

Logged Item:   Time          Value

'CONTROL'      0:0:10:0     [[0.51]]
'CONTROL'      0:1:10:0     [[0.59]]

'TASK'         0:0:0:1      [[0.57 0.56]]
'TASK'         0:0:1:1      [[0.58 0.55]]
...
```

The time format is `run:trial:pass:time_step`. Note that the CONTROL mechanism
has one entry per trial (it executes once per trial), while the TASK mechanism
has multiple entries per trial (it settles over many passes).

### Log export formats

Logs can be exported in several formats:

- `log.nparray()` -- as a NumPy array
- `log.nparray_dictionary()` -- as a dictionary of NumPy arrays, keyed by
  component name
- `log.csv()` -- as CSV text

### Displaying values during execution

In addition to logging, the `run` method provides callback hooks that can
execute arbitrary Python functions at various points during execution:

- `call_before_trial` / `call_after_trial` -- called before/after each TRIAL
- `call_before_pass` / `call_after_pass` -- called before/after each PASS

These are useful for printing diagnostic information, updating external state,
or implementing custom monitoring:

```python
def print_after():
    print(f'output: {output_mech.value[0]}')
    print(f'decision: {decision.value[0]}')

comp.run(inputs=stimuli, call_after_trial=print_after)
```

## Summary

- **Parameters** in PsyNeuLink are instances of a special class that supports
  statefulness, history, modulation, and logging.
- **Statefulness** allows a parameter to have independent values in different
  execution contexts (e.g., different Compositions).
- **Dot notation** accesses the most recent value; the **`get`/`set` methods**
  provide explicit context control.
- **Modulable parameters** have a **base value** (set directly) and a
  **modulated value** (computed by the ParameterPort after applying
  ModulatoryProjections).
- **History** records previous values of stateful parameters for later analysis.
- **Logging** records parameter values at each time step, exportable in
  multiple formats.
