import pandas as pd
import re
import matplotlib.pyplot as plt

ntrials=2
compilers = ["cilkiaf", "tapir"]
workers = ["1", "24", "48"]
runtime_pattern = re.compile("^\d+\.\d+$")


#Returns a list of the running time for the given compiler, worker, program tuple
def parse_file(subdir, c, w, p):
  target = subdir + "/Run-" + "-".join([c,w,p]) + ".txt"
  results = []
  
  with open(target, "r") as f:
    for line in f:
      match = runtime_pattern.findall(line)
      if match:
        results.append(float(match[0]))
  
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
  df.to_csv("cilk5.csv")

  return df

def read_csv(name):

  df = pd.read_csv(name, index_col=[0,1,2])
  
  return df


def plot(df):
  df2 = df.min(axis=1).unstack(0).unstack(1)
  df2.plot.bar(title="Tapir and Cilkiaf running times", xlabel="Program", ylabel="Runtime (s)", logy=True) 
  plt.savefig("all.pdf")
  df2["tapir"].plot.bar(title="Tapir running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("tapir.pdf")
  df2["cilkiaf"].plot.bar(title="Cilkiaf running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("cilkiaf.pdf")
  plt.show()


df = cilk5_gather()
print(df)

plot(df)

