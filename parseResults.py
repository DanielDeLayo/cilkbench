import pandas as pd


compilers = ["cilkiaf", "tapir"]
workers = ["1", "24", "48"]
programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "nqueens", "qsort", "rectmul", "strassen"]

# LAYOUT: Compilers, Programs, Workers
index = pd.MultiIndex.from_product([compilers, programs, workers],names=["Compiler", "Program", "Worker"])

data = []

for c in compilers:
  for p in programs:
    for w in workers:
      data.append((c + p + w + "A", c + p + w + "B"))

df = pd.DataFrame(data, index)

print(df)

