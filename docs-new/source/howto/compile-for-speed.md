# Compile for speed with LLVM

PsyNeuLink includes a runtime compiler that translates models to native
machine code via [LLVM](https://llvm.org/). This can improve execution
performance by **one to three orders of magnitude** depending on the model.
See [Vesely et al. (2022)](http://www.cs.yale.edu/homes/abhishek/jvesely-cgo22.pdf)
for details on the compilation approach.

## How compilation works

When you invoke `run()` or `execute()` with a compiled execution mode, the
following steps occur:

**Compilation phase:**

1. The model is initialized (identical to non-compiled execution).
2. Data structures (inputs, outputs, parameters) are flattened and converted
   to LLVM IR form.
3. LLVM IR code is generated to match the semantics of individual components
   and the scheduling rules in use.
4. Host-CPU-compatible binary code is generated.
5. The resulting function is saved as a `ctypes` function and parameter types
   are converted to `ctypes` binary structures.

**Execution phase:**

1. Parameter structures are populated from the {class}`Composition` based on
   the provided `execution_id`. These structures are preserved between
   invocations, so executions with the same `execution_id` reuse the same
   binary structures.
2. The compiled `ctypes` function is called.
3. Results are extracted from the binary structures and converted back to
   Python format.

## Execution modes

Pass one of these {class}`ExecutionMode` values to the **bin_execute** (or
**execution_mode**) parameter of `Composition.run()` or
`Composition.execute()`:

| Mode                          | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| `ExecutionMode.Python`        | Normal Python execution (no compilation). This is the default.             |
| `ExecutionMode.LLVM`          | Compile and execute individual nodes. The scheduling loop still runs in Python. |
| `ExecutionMode.LLVMRun`      | Replace the entire `Composition.run()` with a compiled equivalent. Best performance for most models. |
| `ExecutionMode.Auto`          | Attempt `LLVMRun`, then fall back to node-level compilation, then to Python. **Recommended for general use.** |
| `ExecutionMode.PyTorch`       | For {class}`AutodiffComposition` only: use PyTorch for `learn()` and Python for `run()`. |
| `ExecutionMode.PTX`           | Compile individual nodes for GPU execution via CUDA.                       |
| `ExecutionMode.PTXRun`        | Compile the entire run loop for GPU execution via CUDA.                    |

### Examples

```python
import psyneulink as pnl

mech_a = pnl.TransferMechanism(name='A', input_shapes=3)
mech_b = pnl.TransferMechanism(name='B', input_shapes=3)
comp = pnl.Composition(pathways=[mech_a, mech_b])

# Recommended: try compiled, fall back gracefully
comp.run(inputs={mech_a: [[1, 2, 3]]}, execution_mode=pnl.ExecutionMode.Auto)

# Maximum speed if the model compiles successfully
comp.run(inputs={mech_a: [[1, 2, 3]]}, execution_mode=pnl.ExecutionMode.LLVMRun)

# Standard Python execution (for debugging or comparison)
comp.run(inputs={mech_a: [[1, 2, 3]]}, execution_mode=pnl.ExecutionMode.Python)
```

## Using Auto mode

`ExecutionMode.Auto` is the safest way to benefit from compilation. It
progressively attempts the highest-performance modes and falls back
gracefully:

1. Try `LLVMRun` (compile the entire run loop)
2. If that fails, try compiling individual nodes
3. If that fails, fall back to Python execution

Warnings (rather than errors) are raised when a higher mode fails,
so your model always runs:

```python
comp.run(inputs={mech_a: [[1, 2, 3]]}, execution_mode=pnl.ExecutionMode.Auto)
```

## Compiled learning with AutodiffComposition

{class}`AutodiffComposition` supports compiled learning via LLVM:

```python
my_autodiff.learn(
    inputs=training_dict,
    execution_mode=pnl.ExecutionMode.LLVMRun
)
```

This provides the fastest training for supervised learning with
backpropagation, supporting MSE and cross-entropy loss functions. See
{doc}`use-pytorch-models` for details.

## Important caveats

### Data synchronization

Data other than `Composition.run()` outputs are **not** synchronized between
Python and compiled execution. This means:

- Intermediate mechanism values may not be updated in the Python-side objects
  after compiled execution.
- If you need to inspect intermediate values, use `ExecutionMode.Python` or
  log the specific values you need.

### Schedule limitations

`ExecutionMode.LLVM` (per-node compilation) runs the scheduling loop in
Python but executes each node as compiled code. Schedules that require access
to node data (e.g., conditions that inspect a mechanism's current value)
**will not work correctly** in this mode. Use `ExecutionMode.LLVMRun` or
`ExecutionMode.Auto` instead.

### Compilation of individual Functions and Mechanisms

It is technically possible to invoke compiled versions of individual
{class}`Function` and {class}`Mechanism` objects. However, this is provided
for **testing purposes only** -- the lack of data synchronization makes it
unreliable for general use.

## Performance tips

- Use `ExecutionMode.LLVMRun` for batch execution of many trials.
- For parameter estimation ({class}`ParameterEstimationComposition`),
  compilation can dramatically reduce search time.
- The first call with a compiled mode incurs a one-time compilation cost.
  Subsequent calls with the same `execution_id` reuse the compiled binary.
- GPU modes (`PTX`, `PTXRun`) require a CUDA-compatible GPU and appropriate
  drivers.

## Next steps

- {doc}`use-pytorch-models` -- LLVM and PyTorch modes for
  AutodiffComposition
- {doc}`fit-parameters` -- speed up parameter estimation with compilation
- {doc}`log-and-report` -- understand logging limitations under compilation
