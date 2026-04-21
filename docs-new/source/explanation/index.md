(explanation)=
# Explanation

These pages provide in-depth discussions of PsyNeuLink's design, architecture,
and theoretical foundations. They are intended to deepen your understanding of
*why* PsyNeuLink works the way it does, rather than giving step-by-step
instructions (see the [Tutorials](../tutorials/index) for that) or exhaustive
API listings (see the [Reference](../reference/index) for that).

```{toctree}
:maxdepth: 2

architecture
component-hierarchy
scheduling-and-execution
control-theory
learning-and-autodiff
parameters-and-state
```

## Where to start

- **New to PsyNeuLink?** Begin with the {doc}`architecture` page, which
  introduces the three core abstractions -- Mechanisms, Projections, and
  Compositions -- and explains how they fit together.

- **Designing a model?** The {doc}`component-hierarchy` page gives a complete
  map of every built-in component type and when to use each one.

- **Working with dynamics or multi-timescale models?** Read
  {doc}`scheduling-and-execution` for a thorough treatment of the Scheduler,
  Conditions, and PsyNeuLink's time-scale hierarchy.

- **Adding control or learning?** See {doc}`control-theory` and
  {doc}`learning-and-autodiff` for the theoretical background behind
  PsyNeuLink's modulatory and learning subsystems.

- **Debugging parameter values?** The {doc}`parameters-and-state` page
  explains statefulness, contexts, modulation, and logging.
