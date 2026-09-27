# Plain-language summary: checking data center cooling models fairly

Large computing systems produce enough heat to warm a small neighborhood. They
need liquid and air cooling systems that work reliably while computers change
from quiet periods to heavy workloads. Engineers use computer models to predict
temperatures, water flow, and controller behavior. The difficulty is that two
models can look different simply because they were given different inputs or
asked to predict different things.

This project creates a fair-test recipe for cooling models. It identifies which
measurements belong to the same cooling circuit, records the units and timing
of each signal, and requires every model to use the same inputs and report the
same outputs. The first case uses an existing monitoring record from the
Marconi100 supercomputer. It includes readings from the liquid-cooling
controller and from hundreds of computer nodes.

The first analysis found an important quality-control lesson. A controller
channel reported a fixed 6-degree temperature difference, while the directly
measured supply and return temperatures changed over time. A good model test
must use the changing measurements, rather than treating the fixed controller
value as proof that a model is correct.

The work is deliberately careful about what it does not yet know. The public
record does not identify exactly which racks belong to each controller panel.
Until that map is documented, the project will not claim that it has validated
an individual rack or a chip-cooling model. Instead, it provides reusable code
and a transparent checklist so researchers and operators can see what the data
can support today and what information is still required.
