# BALANCE theory -> direct/causal predictions v2

## Purpose

Translate the current middle-world mathematics into direct empirical measurements while preserving the central Chapter-2 rule:

\[
L>0
\quad\text{and}\quad
W_S^*>W_A^*,
\]

where `W_A*` is the best registered accessible alternative envelope.

The advanced geometry does not replace the direct worldline comparison. It specifies what can be tested after repeated matched contexts are available.

---

## A. Focal Pedicularis direct layer

The immediate focal route still uses the same-context SCH handoff plus Experiment B.

### A1. Conflict qualification

Consume a positive context-locked SCH `L` on the same fitness scale.

No positive `L` -> no BALANCE promotion.

### A2. Direct worldline ordering

From the shared Experiment-B surface estimate optimized shared and alternative-accessible fitness:

\[
W_S^*,\qquad W_A^*.
\]

Primary state call:

\[
\boxed{L>0,\quad \rho_A=W_S^*-W_A^*>0.}
\]

For the current focal functional-state design, the evidence ceiling remains functional-state middle world unless structural architecture/cost is independently established.

### A3. Direct interior coordinates

Once BALANCE is identified, report

\[
\rho_A,
\qquad
\xi_F=\frac{L}{L+\rho_A},
\qquad
d_F=\min(L,\rho_A).
\]

These are direct Chapter-2 quantities and do not require BITA `s,K` decomposition.

---

## B. Repeated-environment geometry

The following results require matched direct worldline receipts across environmental contexts.

### B1. Deepest fitness context

If `L(e)` increases and `rho_A(e)` decreases monotonically along a one-dimensional path, the fitness-deepest point satisfies

\[
L=\rho_A,
\qquad
\xi_F=1/2.
\]

This is a fitness-margin center, not necessarily the environmental-distance center.

### B2. Metric environmental depth

Register an environmental perturbation metric `Q` independently of the outcome.

For a local status margin `f`, estimate its environmental gradient and compute

\[
d_Q(f)=
\frac{f}{\sqrt{\nabla f^\top Q^{-1}\nabla f}}.
\]

The middle-world environmental depth is the minimum distance to the SCH-facing or any registered architecture-facing boundary.

This allows a direct empirical distinction between:

```text
large fitness reserve but steep environmental boundary
small fitness reserve but shallow environmental boundary
```

### B3. Width-depth relationship

Along a one-dimensional repeated-context path, estimate left/right boundary slopes and test the registered width-depth bounds.

Under approximately constant slopes `ell` and `r`, the predicted deepest fitness reserve is

\[
d^*=W_e\frac{\ell r}{\ell+r}.
\]

Departure beyond uncertainty is a geometry/model audit rather than automatic evidence for history dependence.

### B4. Affine-envelope no-reentry and threat-switch bound

When the optimized shared worldline and all registered alternative worldlines are prospectively modeled as affine along one scalar environmental coordinate,

\[
W_S^*(e)=a_Se+b_S,
\qquad
W_{D_j}^*(e)=a_je+b_j,
\]

the best-alternative reserve

\[
\rho_A(e)=W_S^*(e)-\max_jW_{D_j}^*(e)
\]

must be concave and piecewise affine.

Prospective signatures are:

- the positive architecture-reserve set `{rho_A>0}` is one connected interval;
- after the shared world loses to the alternative envelope it cannot later regain static architecture dominance on the same affine path;
- each alternative architecture can occupy at most one connected upper-envelope segment;
- with `m` alternatives, threat identity switches at most `m-1` times, apart from explicit tie intervals;
- reserve slopes are non-increasing across exact envelope switches.

Observed architecture-side re-entry or repeated return of the same threat architecture is therefore a model-audit trigger, not immediate evidence for hysteresis. Curved worldlines, changing accessibility scope or nonstatic effects must be considered before biological interpretation.

### B5. Two-endpoint continuous-interval certificate

The same affine-envelope assumptions give a useful design reduction. Because `rho_A(e)` is concave on a closed scalar interval,

\[
\min_{e\in[e_L,e_R]}\rho_A(e)
=
\min\{\rho_A(e_L),\rho_A(e_R)\}.
\]

Therefore, if both endpoint reserves are bounded strictly above zero,

\[
\rho_A(e_L)>0,
\qquad
\rho_A(e_R)>0,
\]

then shared fitness exceeds the entire registered alternative envelope for every interior context:

\[
\boxed{
\rho_A(e)>0\quad\forall e\in[e_L,e_R].
}
\]

The smaller endpoint reserve is also a conservative lower bound on architecture-facing fitness margin throughout the interval.

If the SCH conflict margin `L(e)` is itself affine or otherwise concave and both endpoint conflict margins are positive, the same logic certifies the **entire interval** as static BALANCE.

This is explicitly model-based. A strong design should use the two endpoints for the formal certificate and retain at least one interior context as a held-out affine-shape check. If the affine model fails, inference reverts to the sampled contexts rather than preserving the endpoint certificate.

---

## C. Multiple accessible alternative architectures

This layer should only be used when more than one biologically accessible alternative is genuinely registered.

### C1. Alternative envelope

For each alternative `j`, estimate

\[
W_{D_j}^*,
\qquad
\rho_j=W_S^*-W_{D_j}^*.
\]

Then

\[
W_A^*=\max_jW_{D_j}^*,
\qquad
\rho_A=\min_j\rho_j.
\]

A BALANCE call requires positive reserve against **every** registered accessible alternative.

### C2. Dominance pruning

An alternative can be removed from envelope calculations only after proving it is dominated over the declared environmental domain.

Sample-grid dominance is not continuous-domain dominance unless interpolation/shape constraints justify it.

Report both:

- full biological accessibility registry;
- mathematically nondominated envelope candidates.

### C3. Accessibility partial identification

If

\[
A_{def}\subseteq A_{true}\subseteq A_{poss},
\]

then compute inner/outer BALANCE domains rather than silently choosing one accessibility set.

The possible-set envelope gives the conservative/robust BALANCE call; the definite-set envelope gives the optimistic outer call.

---

## D. Small boundary certificates

### D1. Helly no-middle-world certificate

In `p` environmental dimensions with convex status sets, an empty BALANCE intersection has a certificate involving at most

\[
p+1
\]

convex constraints.

Empirical use:

- fit registered convex/affine status surfaces;
- if no common middle-world region remains, identify a smallest/low-cardinality obstruction set;
- report which SCH, alternative-architecture or environmental-feasibility boundaries jointly destroy the domain.

### D2. Chebyshev dual support

For affine status boundaries, solve the metric Chebyshev-center LP and report dual multipliers `mu_k`.

There exists an optimal dual certificate with at most `p+1` positive multipliers.

The local shadow-price interpretation is

\[
\frac{\partial t^*}{\partial b_k}=\mu_k^*.
\]

Thus the dual identifies which boundaries actually limit maximum environmental robustness and how much outward relaxation of each would increase the deepest radius.

---

## E. Falsifiers / downgrade conditions

The advanced BALANCE geometry is downgraded if:

- `context_id` or fitness scale does not match SCH;
- an accessible alternative is omitted and later shown to dominate the registered envelope;
- interval uncertainty leaves worldline order unresolved;
- the chosen environmental metric is selected post hoc to maximize depth;
- a claimed continuous-domain dominance relation is supported only on sampled points;
- affine/convex assumptions fail materially between sampled contexts;
- apparent re-entry is only an envelope identity switch without a sign change in `rho_A`;
- an affine-path claim shows genuine architecture-reserve re-entry or repeated disjoint activity of the same alternative beyond uncertainty;
- a two-endpoint certificate is retained after held-out interior contexts reject the affine worldline assumption.

## F. Promotion ladder

```text
BALANCE-T
sandwiched-domain + geometry theory

BALANCE-C1
same-context direct WS*/WA* comparison identifies occupancy

BALANCE-C2/C3
repeated contexts recover depth, width, critical surfaces and limiting boundaries

BALANCE-G
same direct middle-world signatures recur in independent systems
```

PAYOFF frequency dependence cannot substitute for any direct worldline stage.
