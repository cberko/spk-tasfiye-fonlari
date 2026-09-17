"""Tüm akışı çalıştırır: python -m tasfiye"""
from . import allocation, fonlar_arasi, dataset, extract, plots, report

for step in (extract, dataset, allocation, fonlar_arasi, plots, report):
    print(f"\n== {step.__name__.split('.')[-1]} ==")
    step.main()
