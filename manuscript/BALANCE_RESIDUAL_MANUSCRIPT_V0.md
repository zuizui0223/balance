# How to identify and quantify persistent compromise

## Abstract

A real functional conflict does not imply that differentiated architecture should already be favored. We define persistent compromise as the region in which a shared-coordinate conflict exists but the optimized differentiated-accessible world still fails to outperform the optimized shared world. This region can be identified directly without first decomposing architecture gain into recoverability and cost. We then treat position, two-sided depth, reserve, environmental width, connectedness, and hysteresis as estimands of the compromise domain itself. The framework distinguishes identification of the domain from mechanistic decomposition of its boundary and provides concordance tests when both direct and decomposed routes are available.

## 1. Direct identification of the middle world

Let

```text
W_S*(e) = optimized shared-coordinate fitness
W_D*(e) = optimized differentiated-accessible fitness
Delta_W(e)=W_D*(e)-W_S*(e).
```

Persistent compromise is directly identified when

```text
L(e)>0
Delta_W(e)<0.
```

This route does not require prior identification of `s` and `K`.

## 2. Geometry of persistence

When the decomposed representation is available,

```text
Phi=sL-K
rho=K-sL
xi=L/(L+rho)
d_B=min(L,rho).
```

These quantities describe different features of the interior: proximity to the no-conflict boundary, proximity to the architecture crossing, and two-sided depth.

For fixed `s>0` and `K>0`, the deepest point occurs at

```text
L_deep=K/(1+s),
rho_deep=K/(1+s),
xi_deep=1/2.
```

Thus the point of maximal two-sided robustness need not be the midpoint of the admissible conflict-load interval.

## 3. Direct-versus-decomposed concordance

Where both routes are available, compare

```text
Delta_W
```

against

```text
sL-K.
```

A discrepancy is a bridge residual to diagnose, not a quantity to average away. Candidate causes include scale mismatch, context mismatch, omitted ecological channels, or architecture-induced landscape change.

## 4. Persistence across environment and history

The domain can also have width, connectedness, and re-entry structure along environmental gradients. Switching costs introduce a history-dependent band around the static crossing,

```text
-C_DS/T <= Phi <= C_SD/T.
```

This separates static architecture ranking from persistence caused by finite transition costs.

## 5. Empirical route

A direct application requires one matched context in which a genuine shared-axis conflict is established and optimized shared and differentiated-accessible worldlines can be compared on the same reproductive fitness scale. Functional-state and structural-architecture claims remain separate.

## 6. Discussion

The central point is that compromise is not merely the absence of differentiation. It can be a measurable region with its own position, depth, reserve, width, topology, and historical persistence. Mechanistic decomposition into recoverability and architecture cost is valuable but not logically required to establish that the shared world still wins despite a real conflict.

## Scope after SLK integration

SLK owns the cross-repository classification `L>0, Phi<0` as one stage in the flagship hierarchy. This paper owns the direct identification, geometry, concordance, and persistence properties of that region.
