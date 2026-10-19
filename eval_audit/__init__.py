"""Paired counterfactual audit of already scored model responses."""

from .core import AuditError, audit, load_pairs

__all__ = ["AuditError", "audit", "load_pairs"]
