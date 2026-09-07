# BALANCE auxiliary assay-capacity theorem v1

## Purpose

Convert threat-label partial identification into a quantitative design bound.

When optimized-fitness data leave `m` alternative architectures tied on the active envelope, architecture-specific auxiliary measurements can separate them only if the combined auxiliary code has enough distinct outcomes.

## Setup

At a focal context, let the envelope-defined active threat set be

\[
T=\{D_1,\ldots,D_m\},
\qquad m\ge1.
\]

Suppose `k` auxiliary assays are collected. Assay `r` can produce at most

\[
q_r\ge2
\]

distinguishable registered outcomes on the tied threat set.

Each architecture receives a joint code

\[
H(D_j)=
(h_1(D_j),\ldots,h_k(D_j)).
\]

## Theorem 1 — product-capacity necessary condition

The total number of distinct joint codes is at most

\[
\prod_{r=1}^kq_r.
\]

Therefore unique identification of all `m` tied alternatives requires

\[
\boxed{
\prod_{r=1}^kq_r\ge m.
}
\]

This is an information-capacity condition only. It is necessary, not sufficient: the actual biological code map must also assign distinct codes to the tied architectures.

## Corollary 1a — binary assay lower bound

If every auxiliary assay is binary,

\[
q_r=2,
\]

then

\[
2^k\ge m.
\]

Hence any design that guarantees the capacity to distinguish `m` arbitrary tied alternatives needs at least

\[
\boxed{
k\ge\lceil\log_2m\rceil.}
\]

Examples:

```text
m=1  -> 0 binary assays needed
m=2  -> at least 1
m=3-4 -> at least 2
m=5-8 -> at least 3
```

## Theorem 2 — injective joint code is sufficient

If the registered joint auxiliary map

\[
H:T\to\mathcal H_1\times\cdots\times\mathcal H_k
\]

is injective, then observing the joint code uniquely identifies the architecture within the tied threat set.

Thus the complete criterion is:

```text
capacity: enough possible codes
+
biology: actual registered code map is injective on T.
```

## Theorem 3 — partial-identification class size after assays

For an observed joint code `h_obs`, define

\[
T_{obs}=
\{D_j\in T:H(D_j)=h_{obs}\}.
\]

The remaining architecture uncertainty is exactly the size and composition of `T_obs` under the registered code map.

Each additional assay refines the previous partition of `T`; it can never enlarge an existing equivalence class when data are internally consistent.

Therefore auxiliary evidence produces a nested identification sequence

\[
T=T^{(0)}\supseteq T^{(1)}\supseteq\cdots\supseteq T^{(k)}.
\]

## Theorem 4 — redundant assays add zero separating capacity on the focal tie set

If a new assay outcome is a deterministic function of the already observed joint code on `T`, then it does not split any existing code class and cannot reduce `T_obs`.

So nominally adding another measurement does not increase architecture identification unless it creates a finer partition of the tied alternatives.

This is the discrete-design analogue of the theorem that an auxiliary variable factoring only through existing envelope observables cannot break envelope equivalence.

## Theory -> causal bridge

BALANCE can now plan architecture-label measurements after the optimized-fitness analysis reveals the active threat set:

1. estimate the envelope and identify `T`;
2. count the number of tied candidate alternatives `m`;
3. choose auxiliary assays with sufficient joint capacity;
4. preregister architecture-specific codes;
5. report the post-assay identified subset rather than forcing a unique label.

This avoids over-measuring when the envelope is already unique and avoids under-powered label claims when many alternatives remain tied.

## Claim ceiling

The logarithmic bound is an information-capacity bound, not a claim that arbitrary biological assays can attain the ideal coding scheme. Measurement error, uncertain codes and unregistered alternatives require interval/probabilistic extensions. The result concerns architecture identity conditional on the static BALANCE registry, not PAYOFF dynamics.