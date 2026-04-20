.. _explanation-architecture:

============
Architecture
============

.. contents:: On this page
   :local:
   :depth: 2

Overview
========

PsyNeuLink is organized around three core abstractions that map onto
concepts from both computational neuroscience and software engineering:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - PsyNeuLink
     - Computational graph
     - Neuroscience analogy
   * - `Mechanism`
     - Node
     - Brain region, neural population, or cognitive process
   * - `Projection`
     - Directed edge
     - Connection, pathway, or modulatory signal
   * - `Composition`
     - Graph / subgraph
     - Circuit, system, or complete model

These compose hierarchically: a `Composition` can contain other Compositions
as nodes, enabling models that span multiple levels of analysis.


Component hierarchy
===================

All PsyNeuLink objects inherit from `Component`, which provides:

- **Parameters** -- configurable values with history, logging, and modulability
- **Ports** -- typed input/output interfaces (InputPort, OutputPort, ParameterPort)
- **Functions** -- pluggable mathematical transformations
- **Execution context** -- support for parallel execution with independent state

.. code-block:: text

   Component
   ├── Mechanism
   │   ├── ProcessingMechanism
   │   │   ├── TransferMechanism
   │   │   ├── IntegratorMechanism
   │   │   └── ObjectiveMechanism
   │   └── ModulatoryMechanism
   │       ├── ControlMechanism
   │       └── LearningMechanism
   ├── Projection
   │   ├── PathwayProjection
   │   │   └── MappingProjection
   │   └── ModulatoryProjection
   │       ├── ControlProjection
   │       └── LearningProjection
   ├── Port
   │   ├── InputPort
   │   ├── OutputPort
   │   ├── ParameterPort
   │   └── ModulatorySignal (ControlSignal, LearningSignal)
   └── Function
       ├── TransferFunctions (Linear, Logistic, ReLU, ...)
       ├── IntegratorFunctions
       ├── LearningFunctions
       ├── ObjectiveFunctions
       ├── OptimizationFunctions
       └── ...


Processing vs. modulation
=========================

PsyNeuLink distinguishes two kinds of information flow:

**Processing** (the "what")
   Data flows through `ProcessingMechanisms <ProcessingMechanism>` connected
   by `PathwayProjections <PathwayProjection>`. This represents the primary
   computational pathway of a model.

**Modulation** (the "how")
   `ModulatoryMechanisms <ModulatoryMechanism>` send `ModulatoryProjections
   <ModulatoryProjection>` to modify the parameters of processing components.
   This enables adaptive behavior -- for example, a `ControlMechanism` can
   adjust the gain of a `TransferMechanism` based on monitored outcomes.

This separation mirrors the distinction in neuroscience between feedforward
processing and neuromodulatory control, and enables clean separation of
concerns in model design.


Execution model
===============

Execution in PsyNeuLink follows these steps:

1. A `Scheduler` determines the order in which Mechanisms execute, based on
   the graph topology and any `Conditions <Condition>` assigned to nodes.
2. Each Mechanism reads from its `InputPorts <InputPort>`, executes its
   `Function`, and writes to its `OutputPorts <OutputPort>`.
3. `Projections <Projection>` transmit values from OutputPorts to InputPorts
   of downstream Mechanisms.
4. ModulatoryMechanisms execute and modify parameters of target components.
5. The cycle repeats for each `TRIAL` (one pass through all inputs) and
   each `TIME_STEP` within a trial.

For performance-critical applications, the entire execution graph can be
compiled to native code via LLVM (see :doc:`/howto/compile-for-speed`).

.. note::

   For a detailed discussion of scheduling semantics, see
   :doc:`scheduling-and-execution`.
