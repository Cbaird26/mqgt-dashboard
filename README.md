# mqgt-dashboard

Unified falsification dashboard: run receipts, metrics, plots, joint exclusion.

## Purpose

Combines bounds from multiple constraint channels to produce joint exclusion plots and dashboard JSON with allowed regions, next test recommendations, and orthogonality analysis.

## Installation

```bash
pip install -e .
```

## Dependencies

- All channel repos (fifth-force, collider, precision, cosmology, etc.)
- mqgt-core-params
- mqgt-api-schema

## Usage

```bash
mqgt-dashboard generate-joint
```
