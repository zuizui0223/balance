# Bounded-Phi identification and reset-enabled observation design

Status: optional extension; synthetic examples only. Related contract:
[error-free switching identification](EMPIRICAL_IDENTIFICATION_CONTRACT.md).
The primary static BALANCE estimand and original dynamics are unchanged.

## Separate forcing uncertainty from state uncertainty

Each ordered observation is (Phi_lower,Phi_upper,state), bounding the unknown
true forcing. State labels are exact in this model. Fixed external context,
fixed costs and payoff horizon, the instantaneous deterministic switching rule,
and monotonicity of the LATENT forcing must be declared. A noisy observed center
need not itself be monotone, but its bands must admit a monotone true path.

Use nonnegative threshold coordinates:

    c_F=F=C_SD/T,     c_R=-R=C_DS/T,     W=c_F+c_R.

For the reverse path replace Phi by -Phi and reverse each interval's endpoints.
Both paths then use an increasing forcing coordinate and switch iff Phi>c.
Equality retains the old state.

## Identification from the whole record

For increasing latent values x_i in [l_i,u_i], define

    L_i=max_{j<=i} l_j,   U_i=min_{j>=i} u_j.

These are sharp marginal constraints under monotonicity. If a prefix lower bound
exceeds the current upper bound, no monotone true path exists. With the last old
state at i and the first new state at i+1,

    c in [max(0,L_i), U_{i+1}).

The open upper endpoint follows from strict switching. The interval is not just
the adjacent raw measurement band: earlier and later records can tighten it.
A no-switch path yields c>=max(0,L_last), with no invented upper bound.
Recrossing on a monotone path, impossible latent ordering and empty intersections
are rejected. Additional unknown error correlations are not assumed away; the
Cartesian bands give conservative projections if those correlations exist.

For independently bounded T, total costs are projected as T*W. An exact supplied
T removes the cost/horizon scaling ambiguity but does not turn finite threshold
brackets into point estimates. These sets are not automatic confidence intervals.

## One genuinely prospective next observation

Bisection is allowed only if a matched reset to the OLD architecture is available
without changing the costs, horizon or external context. It is not a procedure
for an irreversible unreset trajectory.

For c in [l,u), let w=u-l. A query at nominal q has unknown actual forcing in
[q-e,q+e]. Its two possible outcomes retain the following outer sets:

    stay:   c in [max(l,q-e),u),
    switch: c in [l,min(u,q+e)).

Before seeing which outcome occurs, the midpoint q=(l+u)/2 minimizes the worst
remaining span. The exact minimax value and guaranteed gain are

    w_next_worst=min(w,w/2+e),
    gain=max(0,w/2-e).

With one equal-cost query and target W=c_F+c_R, choose the direction with the
larger gain. No realized future outcome is supplied to the planner.

The recurrence above approaches a 2e span per threshold. At w<=2e no single
query guarantees further contraction. The two-direction minimax width-span floor
is 2(e_F+e_R), within this bounded-adversarial-query model. It is NOT a universal
measurement limit: more accurate calibration, a justified stochastic error
model, dependent-error information or a different experimental action can change it.

## Synthetic example

Upward: old state at [0.095,0.105], new at [0.115,0.125].
Downward: old state at [-0.055,-0.045], new at [-0.085,-0.075].

    c_F in [0.095,0.125), c_R in [0.045,0.085)
    signed reverse threshold R in (-0.085,-0.045]
    W in [0.14,0.21).

With independent T=10, total switching cost lies in [1.4,2.1).
If the next query error is e=0.005 in either direction:

    forward query Phi=0.11: gain >=0.010
    reverse query Phi=-0.065: gain >=0.015.

So the next reset-enabled query targets the reverse threshold; the width-span
uncertainty contracts from 0.070 to at most 0.055 regardless of the observed state.
This designs the next measurement, not a state transition intervention guarantee.

## Numerical contract and reproduction

All endpoint algebra uses exact rational arithmetic; float interval displays
round outward. `query_phi_exact` records the rational nominal command. Instrument
rounding must be included in the declared query error, not silently ignored.

    python -m balance_domain.bounded_switching_design
    python -m pytest -q tests/test_bounded_switching_design.py

Files: `balance_domain/bounded_switching_design.py` and the matching tests.
