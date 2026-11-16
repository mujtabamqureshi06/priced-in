"""Priced In: valuation of undeveloped mining assets against observed market prices.

The package will hold the forward simulation engine, the claim valuations
(project, operator equity, royalty or stream), the price adapters and the
inversion layer. See ``docs/ROADMAP.md`` for what exists today.
"""

from importlib.metadata import version

__all__ = ["__version__"]

__version__: str = version("pricedin")
