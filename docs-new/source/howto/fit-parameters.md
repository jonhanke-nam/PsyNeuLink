# Fit parameters with ParameterEstimationComposition

{class}`ParameterEstimationComposition` (PEC) is a specialized
{class}`Composition` that estimates the values of specified parameters of a
model so that its outputs best match empirical data (via maximum-likelihood
estimation) or optimize a user-defined objective function.

## Overview

A PEC wraps an existing model Composition and searches over combinations of
parameter values using an optimization algorithm. There are two modes:

- **Data fitting** -- find parameters that maximize the likelihood of observed
  data, using kernel density estimation (KDE).
- **Parameter optimization** -- find parameters that maximize or minimize a
  user-supplied scalar objective function.

## Data fitting

### Step 1 -- Build a model Composition

```python
import numpy as np
import psyneulink as pnl

# A simple DDM-based decision model
input_mech = pnl.TransferMechanism(name='input', input_shapes=1)
decision = pnl.DDM(
    name='DDM',
    function=pnl.DriftDiffusionAnalytical(
        drift_rate=1.0,
        threshold=1.0,
        noise=0.5,
        starting_value=0.0
    )
)
model = pnl.Composition(name='DDM Model', pathways=[input_mech, decision])
```

### Step 2 -- Prepare the data

Data must be a `pandas.DataFrame` where each column corresponds to one of the
outcome variables. Categorical outcomes (e.g., choice) should be represented
as `pandas.Categorical`:

```python
import pandas as pd

data = pd.DataFrame({
    'decision': pd.Categorical([1, -1, 1, 1, -1, 1]),
    'rt': [0.68, 0.75, 0.52, 0.61, 0.89, 0.57]
})
```

### Step 3 -- Construct the ParameterEstimationComposition

The key arguments are:

| Argument                  | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| **model**                 | The Composition whose parameters are being estimated.                      |
| **parameters**            | A dict mapping each parameter to the values to sample.                     |
| **outcome_variables**     | The OUTPUT ports whose values are compared to data.                        |
| **data**                  | A DataFrame of empirical observations (for data fitting).                  |
| **optimization_function** | The optimizer to use (e.g., `'differential_evolution'`).                   |
| **num_estimates**         | Number of independent samples per parameter combination.                   |

```python
pec = pnl.ParameterEstimationComposition(
    name='PEC',
    model=model,
    parameters={
        ('drift_rate', decision): np.linspace(0.1, 2.0, 20),
        ('threshold', decision): np.linspace(0.5, 2.0, 20),
    },
    outcome_variables=[
        decision.output_ports[pnl.DECISION_VARIABLE],
        decision.output_ports[pnl.RESPONSE_TIME],
    ],
    data=data,
    optimization_function='differential_evolution',
    num_estimates=100,
)
```

:::{note}
The `outcome_variables` must be a subset of the output ports of the model's
terminal mechanism.
:::

### Step 4 -- Run the estimation

```python
pec.run(inputs={input_mech: [[1.0]]})
print(pec.optimized_parameter_values)
```

The `optimized_parameter_values` attribute contains the parameter values that
best fit the data. The `results` attribute also stores these optimal values.

## Parameter optimization

Instead of fitting to data, you can optimize an arbitrary objective function.
Specify **objective_function** instead of **data**:

```python
def my_objective(results):
    """results shape: (num_estimates, num_trials, num_outcome_variables)"""
    return np.mean(results[:, :, 0])   # e.g., maximize mean accuracy

pec = pnl.ParameterEstimationComposition(
    name='PEC-opt',
    model=model,
    parameters={
        ('drift_rate', decision): np.linspace(0.1, 2.0, 20),
        ('threshold', decision): np.linspace(0.5, 2.0, 20),
    },
    outcome_variables=[
        decision.output_ports[pnl.DECISION_VARIABLE],
        decision.output_ports[pnl.RESPONSE_TIME],
    ],
    objective_function=my_objective,
    optimization_function='differential_evolution',
    num_estimates=50,
)
```

:::{warning}
Do not specify both **data** and **objective_function**. Specify exactly one
of them -- PEC raises an error if both are provided.
:::

## Supported optimizers

Currently the supported optimization function is:

- **`'differential_evolution'`** -- uses
  [`scipy.optimize.differential_evolution`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html)

## Controlling the number of trials

The **num_trials_per_estimate** argument controls how many trials the model is
run for each evaluation of a parameter combination. If left unspecified, the
model runs until all input trials are exhausted.

## Tips

- Start with a small `num_estimates` to verify the PEC runs correctly, then
  increase it for publication-quality fits.
- For models with stochastic components (e.g., DDM with noise), a higher
  `num_estimates` produces smoother likelihood surfaces.
- The controller and its associated components are constructed automatically --
  do not specify a `controller` in the PEC constructor.

## Next steps

- {doc}`add-control-to-a-model` -- understand control mechanisms, which PEC
  uses internally
- {doc}`compile-for-speed` -- speed up parameter estimation with LLVM
  compilation
