.. _ref-composition:

===========
Composition
===========

.. seealso::

   - :doc:`/tutorials/compositions` -- tutorial introduction
   - :doc:`autodiff-composition` -- PyTorch-based learning
   - :doc:`parameter-estimation-composition` -- parameter fitting

.. rubric:: Subclasses

- `AutodiffComposition` -- :doc:`autodiff-composition`
- `ParameterEstimationComposition` -- :doc:`parameter-estimation-composition`

.. rubric:: Related

- `NodeRole` -- roles assigned to nodes in a Composition
- `Pathway` -- sequences of Mechanisms and Projections
- `Scheduler` -- controls execution order (:doc:`scheduling`)

----

.. automodule:: psyneulink.core.compositions.composition
   :members: Composition, NodeRole
   :private-members:
   :exclude-members: Parameters, show_structure, CompositionError, get_inputs_format, external_input_ports_of_all_input_nodes, external_input_ports
