# Export to MDF format

PsyNeuLink supports the [ModECI Model Description Format](https://github.com/ModECI/MDF)
(MDF), a standardized serialization format for exchanging computational models
of brain and psychological function across different simulation environments.
This is part of the broader [OpenNeuro](https://openneuro.org) effort for open
science in computational neuroscience.

## What you can do with MDF

- **Export** any PsyNeuLink {class}`Composition` or {class}`Component` to MDF
  (JSON or YAML).
- **Import** an MDF model back into PsyNeuLink as a fully functional Python
  script.
- **Share** models with collaborators who use other MDF-compatible simulation
  platforms.

## Exporting a Composition to MDF

### Get the MDF model object

Use the `as_mdf_model` method to get an MDF Model object:

```python
import psyneulink as pnl

mech_a = pnl.TransferMechanism(name='A', input_shapes=3)
mech_b = pnl.TransferMechanism(name='B', input_shapes=2)
comp = pnl.Composition(name='MyModel', pathways=[mech_a, mech_b])

mdf_model = comp.as_mdf_model()
```

### Get serialized JSON or YAML

Use `json_summary` or `yaml_summary` for string output, or
`get_mdf_serialized` for one or more compositions:

```python
# JSON string from the composition
json_str = comp.json_summary

# YAML string from the composition
yaml_str = comp.yaml_summary

# Using the module-level function (supports multiple compositions)
from psyneulink.core.globals.mdf import get_mdf_serialized
json_str = get_mdf_serialized(comp, fmt='json')
```

### Write to a file

```python
from psyneulink.core.globals.mdf import write_mdf_file

# Write as JSON (format inferred from extension)
write_mdf_file(comp, filename='my_model.json')

# Write as YAML
write_mdf_file(comp, filename='my_model.yaml')

# Specify output directory
write_mdf_file(comp, filename='my_model.json', path='/path/to/output')
```

## Importing an MDF model into PsyNeuLink

Use `generate_script_from_mdf` to create a valid Python script from an MDF
model (either a file path, a serialized string, or an MDF Model object):

```python
from psyneulink.core.globals.mdf import generate_script_from_mdf

# From a file
script = generate_script_from_mdf('my_model.json')

# Execute the generated script to load objects into the current namespace
exec(script)
```

After calling `exec()`, all PsyNeuLink objects defined in the MDF file are
available in the current namespace. Use `get_compositions` to retrieve them:

```python
from psyneulink.core.globals.mdf import get_compositions
compositions = get_compositions()
```

:::{warning}
`generate_script_from_mdf` uses `exec()` internally. Only use it with MDF
files from **known and trusted sources**, as it can execute arbitrary Python
code embedded in the file.
:::

## Simple edge format

MDF models can be exported in two styles:

- **PsyNeuLink native format** -- Projections are represented directly as
  edges with functions (the default for PsyNeuLink-to-PsyNeuLink exchange).
- **Simple edge format** -- Projections are decomposed into two edges and an
  intermediate node, because the generic MDF execution engine does not support
  functions on edges.

```python
# Export in simple edge format (for cross-platform compatibility)
json_str = get_mdf_serialized(comp, fmt='json', simple_edge_format=True)

# Export in native PsyNeuLink format
json_str = get_mdf_serialized(comp, fmt='json', simple_edge_format=False)
```

PsyNeuLink can re-import models in either format.

## Supported formats

| Extension | Format |
|-----------|--------|
| `.json`   | JSON   |
| `.yml`    | YAML   |
| `.yaml`   | YAML   |

## Example: round-trip export and import

```python
import psyneulink as pnl
from psyneulink.core.globals.mdf import write_mdf_file, generate_script_from_mdf

# Build a model
input_mech = pnl.TransferMechanism(name='input', input_shapes=2)
output_mech = pnl.TransferMechanism(name='output', input_shapes=2, function=pnl.Logistic)
model = pnl.Composition(name='MyModel', pathways=[input_mech, output_mech])

# Export
write_mdf_file(model, filename='my_model.json')

# Import
script = generate_script_from_mdf('my_model.json')
exec(script)

# The re-imported composition should produce the same results
# when run with the same inputs as the original.
```

## MDF specification

The MDF format is under active development. For the latest specification, see
the [MDF documentation](https://github.com/ModECI/MDF/blob/main/docs/README.md#model).

## Next steps

- {doc}`build-a-feedforward-network` -- build models to export
- {doc}`visualize-models` -- visualize models before or after export
