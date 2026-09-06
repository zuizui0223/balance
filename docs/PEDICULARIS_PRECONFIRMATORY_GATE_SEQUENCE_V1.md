# Pedicularis rex — pre-confirmatory gate sequence v1

## Purpose

Do not jump directly from the two-experiment design to the 20-cell / 10-cell confirmatory experiments. The sister SCH repository already contains three fail-closed technical gates that must qualify the Chapter-1 surface first.

## Ordered gates

### Gate P0 — multilevel exsertion manipulation

Required SCH receipt:

```text
SCH_PEDICULARIS_STAGE_P0_Z_MANIPULATION_V1
status = PEDICULARIS_Z_MANIPULATION_VALIDATED
```

Purpose:

- recover ordered, meaningfully separated realized exsertion levels in `P. rex`;
- keep corolla opening, tube diameter, bract height, lower-lip angle, orientation and water state within preregistered off-target tolerances;
- keep mechanical damage below its frozen limit.

Source contract in SCH:

```text
docs/SCH_PEDICULARIS_STAGE_P0_DATA_CONTRACT_V1.md
```

If P0 fails, do not force Pedicularis into the causal SCH surface. Return first-execution priority to Dalechampia / Castilleja while retaining Pedicularis as a natural D1 / water-defence anchor.

### Gate P — pollination-weight intervention

Required SCH receipt:

```text
SCH_PEDICULARIS_POLLINATION_WEIGHT_V1
status = PEDICULARIS_POLLINATION_WEIGHT_VALIDATED
```

Current registered contrast:

```text
NATURAL
vs
SUPPLEMENTED
```

Purpose: verify that the P manipulation changes the pollination-dependent reproductive contribution in the intended direction without invalidating the common outcome scale.

Evaluator in SCH:

```text
scripts/evaluate_pedicularis_pollination_weight.py
```

### Gate G — independent seed-predator intervention

Required SCH receipt:

```text
SCH_PEDICULARIS_PREDATOR_METHOD_V3
status = PEDICULARIS_PREDATOR_METHOD_VALIDATED
```

Purpose:

- lower seed-predator attack/predation;
- preserve the pollinator-entry lane and pollen/initial-seed-set tolerance;
- hold the Chapter-2 water-defence y state fixed;
- avoid handling damage / realized-z shifts.

Preferred pilot logic is a timed post-pollination lower-flower/fruit sleeve, with a local ovipositor barrier as fallback; no specific material is assumed successful before the pilot.

Source contract in SCH:

```text
docs/SCH_PEDICULARIS_STAGE_G_FIELD_PILOT_V1.md
```

## Readiness assembly

Only after all three gates are positive should SCH assemble:

```text
SCH_PEDICULARIS_FULL_SURFACE_READINESS_V3
status = PEDICULARIS_FULL_SURFACE_READY
```

using:

```text
scripts/assemble_pedicularis_full_surface_readiness.py
```

The readiness receipt requires the same focal population and season across the registered method receipts.

## Then run the two-experiment programme

```text
P0 + P + G positive
        ↓
Experiment A / SCH
>=5 z × 2 P × 2 G
water-y fixed
        ↓
PEDICULARIS_THREE_WORLD_SCH_BUNDLE_V1
        ↓
Experiment B / BALANCE + BITA
same >=5 x × 2 water-y
        ↓
PEDICULARIS_XY_SURFACE_HANDOFF_V1
```

The power/variance pilot described in `PEDICULARIS_TWO_EXPERIMENT_FIELD_PILOT_V1.md` is layered onto this sequence; it does not replace P0, P or G method qualification.

## Current empirical status

All of the above are execution contracts. None of P0, P, G, Experiment A or Experiment B is promoted as a new positive biological result until the corresponding real field receipt exists.
