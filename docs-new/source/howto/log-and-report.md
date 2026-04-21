# Log and report values

PsyNeuLink provides two complementary systems for observing what happens
during model execution:

- **Logging** -- record the values of Component attributes over the course of
  execution for later analysis.
- **Reporting** -- print formatted output to the console (or other devices)
  as a Composition or Mechanism executes.

## Logging

Every {class}`Component` has a {class}`Log` object (accessed via its `log`
attribute) that can record the component's `value` and the values of its
sub-components under configurable conditions.

### Loggable items

The items that can be logged for a component are listed in its
`loggable_items` property:

```python
import psyneulink as pnl

my_mech = pnl.TransferMechanism(name='mech_A', input_shapes=2)
print(my_mech.loggable_items)
# {'InputPort-0': 'OFF', 'slope': 'OFF', 'RESULT': 'OFF',
#  'integration_rate': 'OFF', 'intercept': 'OFF', 'noise': 'OFF', ...}
```

For **Mechanisms**, loggable items include:

- `value` -- the mechanism's output value
- InputPort values
- ParameterPort values (all user-configurable parameters of the mechanism and
  its function)
- OutputPort values

For **MappingProjections**, loggable items include:

- `value` -- the projection's output
- `matrix` -- the weight matrix

### Setting log conditions

Use `set_log_conditions()` to specify *when* values should be recorded. The
condition is a {class}`LogCondition` flag:

| LogCondition        | When the value is recorded                          |
|---------------------|-----------------------------------------------------|
| `OFF`               | Never (default)                                     |
| `INITIALIZATION`    | When the component is created                       |
| `EXECUTION`         | Each time the component executes                    |
| `TRIAL`             | At the end of each trial                            |
| `LEARNING`          | During learning                                     |

```python
my_mech_A = pnl.TransferMechanism(name='mech_A', input_shapes=2)
my_mech_B = pnl.TransferMechanism(name='mech_B', input_shapes=3)
comp = pnl.Composition(pathways=[my_mech_A, my_mech_B])
proj_A_to_B = my_mech_B.path_afferents[0]

# Log noise and RESULT for mech_A on every execution
my_mech_A.set_log_conditions([pnl.NOISE, pnl.RESULT])

# Log the projection matrix
proj_A_to_B.set_log_conditions(pnl.MATRIX)
```

If no condition is specified, `LogCondition.EXECUTION` is used by default.

#### Combining conditions

Conditions can be combined using bitwise operators or as a list:

```python
# Log during both execution and learning
my_mech.set_log_conditions('value', pnl.LogCondition.EXECUTION | pnl.LogCondition.LEARNING)

# Equivalent list syntax
my_mech.set_log_conditions('value', [pnl.EXECUTION, pnl.LEARNING])
```

### Logging values programmatically

Use `log_values()` to make a manual log entry at any point:

```python
my_mech.log.log_values({pnl.VALUE: my_mech.value})
```

### Viewing logged items

Check which items are actively being logged:

```python
print(my_mech_A.logged_items)
# {'RESULT': 'EXECUTION', 'noise': 'EXECUTION'}
```

### Accessing log entries

After running the model, log entries can be accessed in several formats.

#### Print to console

```python
my_mech_A.log.print_entries()
```

Output:

```
Log for mech_A:

Logged Item:   Time       Context                  Value
'RESULT'      0:0:0     "EXECUTING ..."           [0.  0.]
'RESULT'      0:1:0     "EXECUTING ..."           [0.  0.]
'noise'       0:0:0     "EXECUTING ..."           [0.]
'noise'       0:1:0     "EXECUTING ..."           [0.]
```

Each entry is a tuple of (time, context, value):

- **time** -- the RUN, TRIAL, PASS, and TIME_STEP of the recording
- **context** -- a string indicating the execution context
- **value** -- the recorded value

#### CSV format

```python
print(my_mech_A.log.csv(entries=[pnl.NOISE, pnl.RESULT], owner_name=False, quotes=None))
# 'Run', 'Trial', 'Time_step', 'noise', 'RESULT'
# 0, 0, 0, 0.0, 0.0 0.0
# 0, 1, 0, 0.0, 0.0 0.0
```

#### NumPy array

```python
arr = my_mech_A.log.nparray(entries=[pnl.RESULT], header=True)
```

#### NumPy dictionary

```python
d = my_mech_A.log.nparray_dictionary(entries=[pnl.RESULT])
```

## Reporting

Reporting provides real-time formatted output during execution. It is
controlled by arguments to a Composition's `run()`, `execute()`, or `learn()`
methods.

### Output reporting

Use the **report_output** argument with a {class}`ReportOutput` option:

```python
comp.run(
    inputs={my_mech_A: [[1, 2]]},
    report_output=pnl.ReportOutput.FULL
)
```

| ReportOutput option | Behavior                                                  |
|---------------------|-----------------------------------------------------------|
| `OFF`               | No output reporting (default)                             |
| `USE_PREFS`         | Report based on each component's `reportOutputPref`       |
| `TERSE`             | Brief report as each component executes                   |
| `FULL`              | Detailed report at the end of each trial, including inputs, outputs, and (optionally) parameters |

#### Reporting parameters

Control which parameters appear in output reports with **report_params**:

```python
comp.run(
    inputs={my_mech_A: [[1, 2]]},
    report_output=pnl.ReportOutput.FULL,
    report_params=pnl.ReportParams.ALL
)
```

#### Per-mechanism reporting preferences

Set `reportOutputPref` on individual mechanisms to control their reporting
independently:

```python
my_mech_A.reportOutputPref = ['integration_rate', 'slope']
comp.run(inputs={my_mech_A: [[1, 2]]}, report_output=pnl.ReportOutput.USE_PREFS)
```

### Progress reporting

Track execution progress (trial count and progress bar) with
**report_progress**:

```python
comp.run(
    inputs={my_mech_A: [[1, 2]] * 100},
    num_trials=100,
    report_progress=pnl.ReportProgress.ON
)
```

If the total number of trials is known, an estimated-time-remaining bar is
shown. Otherwise, a spinner is displayed.

### Simulation reporting

For compositions with a controller that runs simulations, control whether
simulation output is included:

```python
comp.run(
    inputs=my_inputs,
    report_output=pnl.ReportOutput.FULL,
    report_simulations=pnl.ReportSimulations.ON
)
```

Simulation output is indented relative to the controller output.

### Reporting devices

By default, reports go to the Python console. You can redirect them:

```python
comp.run(
    inputs=my_inputs,
    report_output=pnl.ReportOutput.FULL,
    report_to_devices=pnl.ReportDevices.RECORD
)

# Access recorded reports
print(comp.recorded_reports)
```

## Next steps

- {doc}`visualize-models` -- complement logging with graphical displays
- {doc}`build-a-feedforward-network` -- build a model to log and report on
- {doc}`compile-for-speed` -- note that compiled execution may limit which
  values can be logged
