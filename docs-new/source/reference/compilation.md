# Compilation

PsyNeuLink includes a runtime compiler to improve performance of executed models.
The performance improvement varies, but it has been observed to be between
one and three orders of magnitude depending on the model.
See [Vesely et al. (2022)](http://www.cs.yale.edu/homes/abhishek/jvesely-cgo22.pdf)
for additional information about the approach taken to compilation, and
{ref}`Composition_Compilation` for its use in executing a {any}`Composition`.


## Overview

The PsyNeuLink runtime compiler works in several steps when invoked via `run` or `execute`:

**Compilation:**

1. The model is initialized. This step is identical to non-compiled execution.
2. Data structures (input/output/parameters) are flattened and converted to LLVM IR form.
3. LLVM IR code is generated to match the semantics of individual components and the used scheduling rules.
4. Host CPU compatible binary code is generated.
5. The resulting function is saved as `ctypes` function and the parameter types are converted to `ctypes` binary structures.

**Execution:**

1. Parameter structures are populated with the data from `Composition` based on the provided `execution_id`. These structures are preserved between invocations so executions with the same `execution_id` will reuse the same binary structures.
2. `ctypes` function from compilation step 5 is executed.
3. Results are extracted from the binary structures and converted to Python format.


## Use

Compiled form of a model can be invoked by passing one of the following values to the `bin_execute` parameter of `Composition.run`, or `Composition.exec`:

- `ExecutionMode.Python`: Normal python execution.
- `ExecutionMode._LLVMPerNode`: Compile and execute individual nodes. The scheduling loop still runs in Python. If any of the nodes fails to compile, an error is raised. **NOTE:** Schedules that require access to node data will not work correctly.
- `ExecutionMode._LLVMExec`: Execution of `Composition.exec` is replaced by a compiled equivalent. If the `Composition` fails to compile, an error is raised.
- `ExecutionMode.LLVMRun`: Execution of `Composition.run` is replaced by a compiled equivalent. If the `Composition` fails to compile, an error is raised.
- `ExecutionMode.Auto`: This option attempts all three above mentioned granularities, and gracefully falls back to lower granularity. Warnings are raised in place of errors. This is the recommended way to invoke compiled execution as the final fallback is the Python baseline.

Note that data other than `Composition.run` outputs are not synchronized between Python and compiled execution.

It is possible to invoke compiled version of `Function`s and `Mechanism`s. This functionality is provided for testing purposes only, because of the lack of data synchronization it is not recommended for general use.

```{eval-rst}
.. automodule:: psyneulink.core.llvm.__init__
   :members: ExecutionMode
   :private-members:
   :exclude-members: random, LLVMBBinaryFunction
```
