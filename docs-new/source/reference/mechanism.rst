.. _ref-mechanism:

=========
Mechanism
=========

A Mechanism is the basic processing unit in PsyNeuLink. It receives input
via `InputPorts <InputPort>`, transforms it using a `Function`, and makes
the result available via `OutputPorts <OutputPort>`.

.. seealso::

   - :doc:`/tutorials/mechanisms-and-functions` -- tutorial introduction
   - :doc:`transfer-mechanism` -- most commonly used Mechanism type

.. rubric:: Subclasses

**Processing**

- `TransferMechanism` -- :doc:`transfer-mechanism`
- `IntegratorMechanism` -- :doc:`integrator-mechanism`
- `ObjectiveMechanism` -- :doc:`objective-mechanism`

**Modulatory**

- `ControlMechanism` -- :doc:`control-mechanism`
- `LearningMechanism` -- :doc:`learning-mechanism`

.. rubric:: Related

- `Port` -- input/output interfaces (:doc:`port`)
- `Function` -- the transformation applied (:doc:`functions`)

----

.. automodule:: psyneulink.core.components.mechanisms.mechanism
   :members:
   :private-members:
   :exclude-members: MechParamsDict, MechanismError, MonitoredOutputPortsOption, random, Parameters, _input_port_variables_getter
