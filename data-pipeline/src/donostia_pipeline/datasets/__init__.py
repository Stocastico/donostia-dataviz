"""Dataset modules: each turns one raw source into ``Metric`` objects.

Adding a dataset = add a module here exposing ``build(ctx) -> list[Metric]`` and
register it in ``build.DATASETS``. No frontend changes are needed; the new
metric appears in the UI via ``metrics.json``.
"""
