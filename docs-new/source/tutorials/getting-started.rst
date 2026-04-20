.. _tutorial-getting-started:

===============
Getting Started
===============

This tutorial introduces PsyNeuLink's core concepts: **Mechanisms**,
**Projections**, and **Compositions**. By the end, you will be able to build
and run a simple model.

.. contents:: On this page
   :local:
   :depth: 2

Prerequisites
=============

Install PsyNeuLink into a virtual environment:

.. code-block:: bash

   pip install psyneulink

Or use the Makefile (see :doc:`/howto/installation`):

.. code-block:: bash

   make install

Verify the installation:

.. code-block:: python

   >>> import psyneulink as pnl
   >>> print(pnl.__version__)


Core concepts
=============

PsyNeuLink models are built from three kinds of objects:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Concept
     - Description
   * - **Mechanism**
     - A processing unit that takes input, applies a function, and produces
       output. Analogous to a "block" in a block diagram or a node in a
       computational graph.
   * - **Projection**
     - A directed connection that transmits the output of one Mechanism to
       the input of another. Analogous to an edge in a computational graph.
   * - **Composition**
     - A container that assembles Mechanisms and Projections into a runnable
       model. Handles scheduling, execution, and results.


Your first Mechanism
====================

A `TransferMechanism` is the simplest processing unit. It takes an input
vector, applies a function, and produces an output:

.. code-block:: python

   >>> import psyneulink as pnl

   >>> # Create a mechanism with a logistic (sigmoid) function
   >>> my_mech = pnl.TransferMechanism(
   ...     name='my_mechanism',
   ...     function=pnl.Logistic(gain=1.0, bias=0)
   ... )
   >>> print(my_mech)
   (TransferMechanism my_mechanism)

The ``function`` argument determines what transformation is applied. PsyNeuLink
provides many built-in functions:

- `Linear` -- identity or affine transformation
- `Logistic` -- sigmoid activation
- `ReLU` -- rectified linear unit
- `SoftMax` -- normalized exponential
- `Exponential`, `Tanh`, and many more (see `TransferFunctions`)


Building a Composition
======================

To create a model, connect Mechanisms into a `Composition`:

.. code-block:: python

   >>> # Create two mechanisms
   >>> input_layer = pnl.TransferMechanism(
   ...     name='input',
   ...     function=pnl.Linear
   ... )
   >>> output_layer = pnl.TransferMechanism(
   ...     name='output',
   ...     function=pnl.Logistic
   ... )

   >>> # Assemble into a composition
   >>> model = pnl.Composition(name='simple_model')
   >>> model.add_linear_processing_pathway([input_layer, output_layer])

`add_linear_processing_pathway` connects the Mechanisms in order, automatically
creating `MappingProjections <MappingProjection>` between them.


Running the model
=================

Use `Composition.run` to execute the model with a set of inputs:

.. code-block:: python

   >>> result = model.run(inputs={input_layer: [1.0]})
   >>> print(result)
   [[0.73105858]]

The input is passed to ``input_layer``, which applies a `Linear` function
(identity), then the result is transmitted via a `MappingProjection` to
``output_layer``, which applies a `Logistic` function:

.. math::

   \text{output} = \frac{1}{1 + e^{-1.0}} \approx 0.731

You can run multiple trials by passing a list of inputs:

.. code-block:: python

   >>> results = model.run(inputs={input_layer: [[0.0], [0.5], [1.0], [2.0]]})
   >>> print(results)
   [[0.88079708]]

.. note::

   `Composition.run` returns only the output of the **last trial**. To see
   all results, inspect ``model.results``:

   .. code-block:: python

      >>> for trial_result in model.results:
      ...     print(trial_result)


Visualizing the model
=====================

PsyNeuLink can generate a graph of your model's structure:

.. code-block:: python

   >>> model.show_graph()

This requires `Graphviz <https://graphviz.org>`_ to be installed on your
system.


Next steps
==========

- :doc:`mechanisms-and-functions` -- deeper dive into Mechanism types and
  the Function library
- :doc:`compositions` -- learn about scheduling, nested compositions, and
  more complex model structures
- :doc:`control` -- add adaptive control to your models
- :doc:`learning` -- train models with learning rules or PyTorch autodiff
