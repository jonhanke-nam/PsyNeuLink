# Use PyTorch models with AutodiffComposition

{class}`AutodiffComposition` is a subclass of {class}`Composition` that
constructs and trains feedforward neural networks using either direct LLVM
compilation or automatic translation to [PyTorch](https://pytorch.org/). Both
approaches can accelerate training by up to three orders of magnitude compared
to standard PsyNeuLink learning.

## Overview

An AutodiffComposition is built the same way as a regular Composition -- you
create mechanisms, projections, and pathways -- but when you call `learn()`, the
network is automatically translated to an equivalent PyTorch model for fast
gradient-based training via backpropagation.

Key advantages over standard PsyNeuLink learning:

- **Speed** -- PyTorch and LLVM backends are dramatically faster.
- **Familiarity** -- leverages PyTorch's mature optimization ecosystem.
- **Nesting** -- AutodiffCompositions can be nested inside other Compositions
  for modular model design.

Key restrictions:

- Primarily limited to **feedforward** architectures with **supervised
  learning** (backpropagation).
- Nodes can have only **one OutputPort** (though it may have multiple efferent
  projections).
- **No modulatory components** (ControlMechanisms, LearningMechanisms, etc.)
  can be included directly. These are constructed automatically during
  learning.
- **No separate bias parameters** -- use {class}`Composition` bias nodes
  instead.

## Creating an AutodiffComposition

```python
import numpy as np
import psyneulink as pnl

# Define mechanisms
input_mech = pnl.TransferMechanism(function=pnl.Linear, input_shapes=3)
output_mech = pnl.TransferMechanism(function=pnl.Linear, input_shapes=2)

# Define a projection with random initial weights
proj = pnl.MappingProjection(
    matrix=np.random.randn(3, 2),
    sender=input_mech,
    receiver=output_mech
)

# Create the AutodiffComposition
my_autodiff = pnl.AutodiffComposition()
my_autodiff.add_node(input_mech)
my_autodiff.add_node(output_mech)
my_autodiff.add_projection(sender=input_mech, projection=proj, receiver=output_mech)
```

You can also use `add_linear_processing_pathway()` just like a regular
Composition:

```python
my_autodiff = pnl.AutodiffComposition()
my_autodiff.add_linear_processing_pathway([input_mech, output_mech])
```

## Training (learning mode)

Call `learn()` with a dict containing **inputs**, **targets**, and
(optionally) **epochs**:

```python
my_inputs  = {input_mech: [[1, 2, 3]]}
my_targets = {output_mech: [[4, 5]]}

my_autodiff.learn(inputs={
    "inputs": my_inputs,
    "targets": my_targets,
    "epochs": 100
})
```

### Execution modes for learning

The **execution_mode** argument of `learn()` controls which backend is used:

| Mode                       | Description                                              |
|----------------------------|----------------------------------------------------------|
| `ExecutionMode.PyTorch`    | **(default)** Translate to PyTorch model for training.   |
| `ExecutionMode.LLVMRun`   | Compile to native code via LLVM. Fastest, but limited to backpropagation with MSE or cross-entropy loss. |
| `ExecutionMode.Python`     | Use standard PsyNeuLink learning components. Slowest; does not support nested compositions. |

```python
# Explicitly use PyTorch mode (the default)
my_autodiff.learn(inputs=input_dict, execution_mode=pnl.ExecutionMode.PyTorch)

# Use LLVM for maximum speed
my_autodiff.learn(inputs=input_dict, execution_mode=pnl.ExecutionMode.LLVMRun)
```

:::{note}
Specifying `ExecutionMode.PyTorch` in the `run()` method (not `learn()`)
causes the composition to execute using the Python interpreter, *not* PyTorch.
This is so that modulation from enclosing compositions can take effect during
inference.
:::

## Running in test mode

After training, switch to `run()` for inference:

```python
result = my_autodiff.run(inputs={input_mech: [[1, 2, 3]]})
print(result)
```

## Learning rates

Learning rates can be specified at two levels:

1. **Composition-wide** -- in the constructor or in `learn()`:

   ```python
   my_autodiff = pnl.AutodiffComposition(learning_rate=0.01)
   # or override per call:
   my_autodiff.learn(inputs=input_dict, learning_rate=0.001)
   ```

2. **Per-projection** -- via the `learning_rate` parameter of individual
   {class}`MappingProjection` objects. These are forwarded to the
   corresponding PyTorch parameters.

Rates specified in `learn()` override those in the constructor, but apply only
to that execution.

:::{tip}
To freeze a projection during training, set its `learnable` attribute to
`False`:

```python
my_proj = pnl.MappingProjection(matrix=fixed_weights, learnable=False)
```
:::

## Nesting AutodiffCompositions

An AutodiffComposition can be nested inside another Composition (or another
AutodiffComposition) for modular designs. All nested compositions must be
AutodiffCompositions during learning:

```python
outer_comp = pnl.Composition()
outer_comp.add_node(my_autodiff)

training_input = {my_autodiff: {
    "inputs":  {input_mech: [[1, 2, 3]]},
    "targets": {output_mech: [[4, 5]]},
    "epochs": 50
}}

outer_comp.learn(inputs=training_input)
```

:::{warning}
Nested compositions are only supported in PyTorch mode. Attempting to use
LLVM or Python mode with nested AutodiffCompositions raises an error.
:::

During learning, internal components of a nested AutodiffComposition are
*not* accessible to the outer composition. After training, when you use
`run()`, the internal components become accessible for modulation and
monitoring.

## Exchanging parameters with PyTorch modules

Use `copy_torch_param_to_projection_matrix` and
`copy_projection_matrix_to_torch_param` to transfer weight matrices between
PsyNeuLink projections and PyTorch parameters:

```python
# Copy from a PyTorch parameter to a PsyNeuLink projection
my_autodiff.copy_torch_param_to_projection_matrix(
    torch_param=some_pytorch_param,
    projection=my_proj
)

# Copy from a PsyNeuLink projection to a PyTorch parameter
my_autodiff.copy_projection_matrix_to_torch_param(
    projection=my_proj,
    torch_param=some_pytorch_param
)
```

## Logging

Logging in AutodiffCompositions works the same as in standard Compositions.
Because the internal mechanisms are not directly executed (they are translated
to PyTorch or LLVM), only these parameters can be logged:

1. The `matrix` parameter of projections
2. The `value` parameter of inner components

## Loss functions

For LLVM mode, specify the loss function in the constructor:

```python
my_autodiff = pnl.AutodiffComposition(loss_spec=pnl.Loss.CROSS_ENTROPY)
```

Available options include `Loss.MSE` (default) and `Loss.CROSS_ENTROPY`.

## Next steps

- {doc}`build-a-feedforward-network` -- basics of constructing network
  pathways
- {doc}`compile-for-speed` -- more about LLVM compilation modes
- {doc}`log-and-report` -- detailed guide to logging component values
