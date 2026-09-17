"""Tüm akışı çalıştırır: python -m tasfiye"""
from . import allocation, dataset, extract, plots

for step in (extract, dataset, allocation, plots):
    print(f"\n== {step.__name__.split('.')[-1]} ==")
    step.main()
