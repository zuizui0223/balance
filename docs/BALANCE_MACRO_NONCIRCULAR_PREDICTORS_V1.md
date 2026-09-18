# BALANCE macro non-circular predictor operationalization v1

## Purpose

Prevent the comparative macro analysis from explaining an architecture outcome with predictors that were inferred from that same outcome.

The two highest-priority pilot predictors are:

```text
H1  alternative_accessibility
H2  functional_coupling
```

Both are biologically attractive and both are vulnerable to circular coding.

## Forbidden shortcuts

The following are invalid.

```text
observed structural differentiation
-> alternative_accessibility = HIGH
```

```text
observed shared persistence
-> functional_coupling = HIGH
```

```text
many published differentiated alternatives
-> alternative_repertoire = MULTIPLE
```

unless the relevant opportunity or coupling evidence is independently established.

Current architecture state is the response, not predictor evidence.

## Predictor receipts

Every confirmatory predictor value requires a source-specific receipt stored separately from the outcome ledger.

A receipt records:

- cluster;
- predictor;
- proposed value;
- source;
- evidence type;
- whether the evidence is independent of the focal architecture outcome;
- adjudication state;
- notes explaining the causal/time ordering.

Multiple receipts may exist for one predictor. Independent adjudicated receipts must agree before the predictor is promoted.

## H1 — alternative accessibility

### Construct

Alternative accessibility is the biological opportunity for a function-separating architecture to be generated or expressed **before using the observed focal split as evidence**.

It is not:

- the fitness advantage of the alternative;
- the observed presence of differentiation;
- the number of alternatives a reviewer can imagine.

### Preferred evidence

Strong evidence may include:

1. experimental creation or activation of an alternative before its fitness outcome is known;
2. pre-existing serial or repeated modules that can be perturbed independently;
3. ancestral reconstruction showing separate latent modules before the focal transition;
4. sister-lineage evidence of the same developmental route when the focal architecture state is blinded;
5. independently characterized duplication/recombination/developmental mechanisms that generate the alternative.

### Weak or circular evidence

Do not promote from:

- the focal differentiated phenotype itself;
- a post hoc statement that differentiation 'must have been accessible';
- an alternative found only after searching outcome-positive lineages;
- current copy number when copy number is itself the outcome being explained.

### Pilot value classes

```text
LOW
MEDIUM
HIGH
UNRESOLVED
NA
```

The classes remain provisional until receipt coverage is adequate.

## H2 — functional coupling

### Construct

Functional coupling is the degree to which the two functions depend on the same material, mechanics, timing, or coordinated performance in the integrated/shared state.

It must be measured or justified from the shared/integrated architecture or an independently reconstructed ancestor.

### Preferred evidence

Examples:

- measured performance covariance/trade-off in the shared state;
- shared material that cannot be allocated independently;
- obligatory sequential dependence between the functions;
- physical linkage demonstrated by perturbation;
- direct evidence that changing one function changes the other before structural differentiation is considered.

### Invalid evidence

Do not code HIGH because:

- the system remains integrated;
- no differentiated state is known;
- two functions occur in the same organ without evidence of dependence.

Do not code LOW because:

- separate modules are currently observed;
- a duplicate exists now.

## Evidence types

Receipts use one of:

```text
PRE_OUTCOME_MEASUREMENT
INTEGRATED_STATE_EXPERIMENT
ANCESTRAL_RECONSTRUCTION
SISTER_LINEAGE_COMPARATOR
EXPERIMENTAL_ALTERNATIVE_GENERATION
DEVELOPMENTAL_MECHANISM
OUTCOME_DERIVED
UNCLEAR
```

Only the first six can potentially be marked outcome-independent.

`OUTCOME_DERIVED` must have

```text
outcome_independence = FALSE
```

and cannot license a confirmatory predictor.

## Adjudication

```text
SCREENED
ADJUDICATED
REJECTED
```

A screened receipt is discovery material.

An adjudicated receipt has been checked against the source and the codebook.

A rejected receipt remains visible so that circular evidence is not silently rediscovered later.

## Agreement rule

For one cluster × predictor:

1. collect all receipts;
2. retain only `ADJUDICATED` and `outcome_independence=TRUE`;
3. if none remain, predictor is not confirmatory-ready;
4. if retained values disagree, fail closed;
5. if they agree, that value may be compared to the macro-ledger value.

The macro-ledger value must match the receipt-derived value.

## Primary model gate

A cluster cannot enter the eventual H1/H2 confirmatory model unless:

```text
macro row:
  ADJUDICATED
  multifunctionality == YES
  conflict_status == POSITIVE
  structural_differentiation resolved

and

alternative_accessibility:
  independently adjudicated receipt exists
  value is not UNRESOLVED/NA

and

functional_coupling:
  independently adjudicated receipt exists
  value is not UNRESOLVED/NA
```

This is stricter than the current pilot logical screen by design.

## Potential H1 refinement

The pilot may show that broad 'accessibility' is too subjective for cross-domain work.

If so, replace it before confirmatory freeze with more observable components such as:

```text
pre-existing module multiplicity:
  SINGLETON / PAIRED / SERIAL_REPEATED / COPYABLE

independent developmental control:
  absent / partial / demonstrated

function-separating manipulation:
  unavailable / possible / experimentally demonstrated
```

This would turn accessibility from a judgement into a derived latent construct.

## Potential H2 refinement

If broad coupling is unreliable, decompose it into:

```text
shared material/resource
task simultaneity
mechanical dependence
obligate sequential dependence
performance covariance
```

No confirmatory cross-domain H2 test should precede a measurement-invariance audit.

## Claim ceiling

Passing this receipt gate establishes that a comparative predictor was coded independently of the response.

It does not make the predictor causal. Confounding, phylogenetic dependence, publication bias and historical reconstruction remain separate problems.
