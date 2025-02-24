import pandas as pd
import re

ntrials=2
compilers = ["cilkiaf", "tapir"]
workers = ["1", "24", "48"]
runtime_pattern = re.compile("^\d+\.\d+$")


# Returns a list of the running time for the given compiler, worker, program tuple
def parse_file(subdir, c, w, p):
  target = subdir + "/Run-" + "-".join([c,w,p]) + ".txt"
  results = []
  
  with open(target, "r") as f:
    for line in f:
      match = runtime_pattern.findall(line)
      if match:
        results.append(match[0])
  
  #print(target)
  #print(results)
    
  return results
  
  

def cilk5_gather():
  programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "nqueens", "qsort", "rectmul", "strassen"]

  # LAYOUT: Compilers, Programs, Workers
  index = pd.MultiIndex.from_product([compilers, programs, workers],names=["Compiler", "Program", "Worker"])

  data = []

  for c in compilers:
    for p in programs:
      for w in workers:
        data.append(parse_file("cilk5", c, p, w))

  df = pd.DataFrame(data, index)

  print(df)


cilk5_gather()

