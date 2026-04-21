(scheduling-and-execution)=
# Scheduling and Execution

One of PsyNeuLink's most powerful features is its ability to simulate models
whose components execute at different time scales -- for example, a recurrent
network that settles over many iterations before passing information to a
decision process that integrates evidence over a still longer time scale. This
page explains the execution model in depth.

## Time scales

PsyNeuLink defines four nested time scales that structure every execution:

```
RUN
└── TRIAL
    └── PASS
        └── TIME_STEP
```

| Time scale            | What it represents                                                        |
|-----------------------|---------------------------------------------------------------------------|
| `TimeScale.RUN`       | The entire call to `Composition.run()`. A RUN consists of one or more TRIALs. |
| `TimeScale.TRIAL`     | Processing of a single input. A TRIAL consists of one or more PASSes.     |
| `TimeScale.PASS`      | One sweep through the Composition's graph in which every node gets the opportunity to execute. |
| `TimeScale.TIME_STEP` | A single node executing once within a PASS.                               |

### How time is reported

PsyNeuLink timestamps are reported as four-part tuples:

```
run : trial : pass : time_step
```

For example, `0:2:5:1` means run 0, trial 2, pass 5, time step 1. This format
appears in logging output and is useful for diagnosing execution order.

## The Scheduler

Every {class}`Composition` has a {class}`Scheduler` that governs when each node
(Mechanism or nested Composition) executes. The Scheduler is responsible for:

1. Determining the order in which nodes are considered for execution.
2. Evaluating each node's {class}`Condition`(s) to decide whether it should
   execute in the current PASS.
3. Tracking the passage of time across TIME_STEPs, PASSes, TRIALs, and RUNs.

### Default execution order

When no Conditions are specified, the Scheduler executes every node exactly
once per PASS, in the topological order determined by the Composition's graph.
Topological order means that a node executes only after all of its upstream
(afferent) nodes have executed. For a simple chain `A -> B -> C`, the order
is `A`, then `B`, then `C`.

### Termination conditions

The Scheduler uses *termination conditions* to decide when to end a PASS and
when to end a TRIAL:

- **PASS termination:** By default, a PASS ends when every node that was
  eligible to execute has done so.
- **TRIAL termination:** By default, a TRIAL ends after one PASS. This can be
  overridden by specifying a termination condition for `TimeScale.TRIAL` in the
  `termination_processing` argument of `Composition.run()`.

For example, to run a TRIAL until a DDM decision mechanism crosses threshold:

```python
from psyneulink import *

decision = DDM(
    name='DECISION',
    function=DriftDiffusionIntegrator(noise=0.5, threshold=20),
    reset_stateful_function_when=AtTrialStart()
)

# ... (add decision to Composition) ...

comp.run(
    inputs={input_mech: stimulus},
    termination_processing={TimeScale.TRIAL: WhenFinished(decision)}
)
```

Here the TRIAL continues for as many PASSes as necessary until the DDM's
integration process crosses the threshold, at which point `WhenFinished`
evaluates to `True` and the TRIAL ends.

## Conditions

{class}`Condition`s are the building blocks of custom execution schedules.
A Condition is a callable that returns `True` or `False` to indicate whether a
node should execute. Conditions are assigned to the Scheduler using its
`add_condition` method.

### Pre-specified Conditions

PsyNeuLink provides a rich library of pre-built Conditions:

#### Absolute Conditions

These depend only on the node's own execution history:

| Condition             | Meaning                                                      |
|-----------------------|--------------------------------------------------------------|
| `Always`              | Execute on every opportunity (the default).                  |
| `Never`               | Never execute.                                               |
| `AtPass(n)`           | Execute only on PASS number *n* within a TRIAL.              |
| `AtTrial(n)`          | Execute only on TRIAL number *n* within a RUN.               |
| `EveryNCalls(n)`      | Execute every *n*-th time the node is considered.            |

#### Relative Conditions

These depend on the execution state of *other* nodes:

| Condition                       | Meaning                                                                |
|---------------------------------|------------------------------------------------------------------------|
| `EveryNExecutions(node, n)`     | Execute every time *node* has executed *n* times since the last execution of the conditioned node. |
| `AfterNCalls(node, n)`          | Execute only after *node* has been called *n* times in the current TRIAL. |
| `WhenFinished(node)`            | Execute (or terminate) when *node* signals that it has finished.       |
| `WhenFinishedAll(*nodes)`       | Execute when all specified nodes have finished.                        |
| `WhenFinishedAny(*nodes)`       | Execute when any of the specified nodes has finished.                  |

#### Composite Conditions

Conditions can be combined with boolean logic:

| Condition                    | Meaning                           |
|------------------------------|-----------------------------------|
| `All(cond1, cond2, ...)`    | All sub-conditions must be True.  |
| `Any(cond1, cond2, ...)`    | At least one must be True.        |
| `Not(cond)`                 | Inverts a condition.              |

### Custom Conditions

When the pre-specified Conditions are insufficient, you can use any Python
function as a Condition through the `When` class (or pass a callable directly).
The function receives access to the Scheduler and the current context, and
returns a boolean.

```python
def has_converged(mech, threshold):
    """True when all elements of the Mechanism's delta are below threshold."""
    return all(abs(v) <= threshold for v in mech.delta)

epsilon = 0.01
comp.scheduler.add_condition(
    color_hidden,
    When(has_converged, task, epsilon)
)
```

This example causes `color_hidden` to wait until the `task` Mechanism's value
has stopped changing appreciably -- a convergence criterion for a settling
network.

## Multi-timescale execution: worked examples

### Example 1: DDM integration to threshold

In the Stroop model from the Basics and Primer, the default DDM uses an
analytic solution (`DriftDiffusionAnalytical`) that completes in a single
execution. To instead simulate the integration dynamics step by step, you
assign `DriftDiffusionIntegrator` as the DDM's function and set a TRIAL
termination condition:

```python
decision = DDM(
    name='DECISION',
    input_format=ARRAY,
    reset_stateful_function_when=AtTrialStart(),
    function=DriftDiffusionIntegrator(noise=0.5, threshold=20)
)

Stroop_model.run(
    inputs={color_input: red, word_input: green, task_input: color},
    termination_processing={TimeScale.TRIAL: WhenFinished(decision)}
)
```

In this configuration, each PASS executes all upstream ProcessingMechanisms
(which complete in one step) and then executes the DDM (which integrates one
step). The TRIAL continues for as many PASSes as it takes for the DDM to
cross its threshold. The output records both the decision value (which equals
the threshold, by definition) and the number of integration steps.

### Example 2: settling a task representation before processing

Sometimes one part of a model needs many executions to produce its output
before downstream nodes should execute. The following example uses a leaky
competing accumulator (LCA) for the `task` Mechanism, which settles for 10
executions before the hidden layers execute:

```python
task = LCAMechanism(name='TASK', input_shapes=2)

Stroop_model.scheduler.add_condition(
    color_hidden, EveryNExecutions(task, 10)
)
Stroop_model.scheduler.add_condition(
    word_hidden, EveryNExecutions(task, 10)
)
```

The Scheduler now holds `color_hidden` and `word_hidden` back until `task` has
executed 10 times. Because the `output` Mechanism depends on both hidden
layers, it automatically waits until they have both executed.

### Example 3: convergence-based settling

Rather than fixing a number of settling steps, you can allow the network to
settle until a convergence criterion is met:

```python
def converge(mech, thresh):
    return all(abs(v) <= thresh for v in mech.delta)

epsilon = 0.01
Stroop_model.scheduler.add_condition(
    color_hidden, When(converge, task, epsilon)
)
Stroop_model.scheduler.add_condition(
    word_hidden, When(converge, task, epsilon)
)
```

Now `color_hidden` and `word_hidden` wait until the change in `task`'s value
(its `delta`) drops below 0.01 in every element, indicating that the LCA has
settled to a stable attractor.

## Coordination across time scales

A key design principle is that PsyNeuLink does not impose a single "clock" on
all components. Different Mechanisms can effectively operate at different
rates within the same TRIAL:

- A recurrent network may execute hundreds of times per TRIAL to settle.
- A decision mechanism may integrate evidence over dozens of steps.
- A control mechanism may execute once per TRIAL (at the end or beginning).

The Scheduler coordinates all of this. It maintains counters for each node's
execution count at each time scale, and Conditions can reference these counters
to express dependencies like "execute node B only after node A has executed 100
times."

### The controller's time scale

When a Composition has a `controller` (a ControlMechanism assigned to the
Composition), it operates on its own schedule, typically executing once per
TRIAL -- either at the end (the default) or at the beginning. This means that
the controller observes the results of the current TRIAL's processing and
adjusts parameters for the next TRIAL (or, if configured to execute at the
start, it adjusts parameters before processing begins).

An {class}`OptimizationControlMechanism` takes this further by running
internal simulations (using the model itself) to evaluate different control
allocations before choosing the best one. These simulations are executed in
separate contexts, so they do not interfere with the model's primary
execution state.

## Summary

- PsyNeuLink's four **time scales** (RUN, TRIAL, PASS, TIME_STEP) provide a
  structured hierarchy for execution.
- The **Scheduler** walks the graph each PASS and uses **Conditions** to
  determine which nodes execute.
- **Pre-specified Conditions** handle common patterns (counts, dependencies,
  convergence); **custom Conditions** handle anything else.
- Components can operate at **different rates** within the same TRIAL,
  enabling models that mix fast dynamics (settling, integration) with slower
  processes (decision, control).
- The **controller** operates on the TRIAL time scale, adjusting parameters
  between (or before) TRIALs based on processing outcomes.
