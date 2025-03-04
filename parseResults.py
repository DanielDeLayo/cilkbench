import pandas as pd
import re
import matplotlib.pyplot as plt
from random import random

ntrials=2

#compilers = ["cilkiaf", "tapir"]
compilers = ["cilksanprace", "cilksan", "tapir"]
workers = ["1", "24", "48"]
runtime_pattern = re.compile("^\d+\.\d+$")


#Returns a list of the running time for the given compiler, worker, program tuple
def parse_file(subdir, c, w, p):
  target = subdir + "/Run-" + "-".join([c,w,p]) + ".txt"
  results = []
  
  try:
    with open(target, "r") as f:
      for line in f:
        match = runtime_pattern.findall(line)
        if match:
          results.append(float(match[0]))   
  except:
    return [100 * random()] * ntrials;

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


def configure_plot():
  plt.xlabel("Program")
  plt.ylabel("Runtime (s)")
  #plt.yscale("log")

  # Stop the legend from covering up data
  plt.legend(bbox_to_anchor=(1.02, .5), loc="center left")
  # Workaround for overlapping x labels
  plt.xticks(rotation=90)  
  # Workaround for cut off x labels
  plt.tight_layout()

def plot_prace(df):
  # All plot is harder to make
  df2 = df.min(axis=1).unstack(0).unstack(1)
  print(df2)

  for c in compilers:
    df2[c].plot(title=c + " running times", marker="x", linestyle="none", xticks=range(len(df2)))
    configure_plot()

  plt.savefig("all.pdf")
  plt.show()
  return
  # "Easy" barcharts
  df2["tapir"].plot.bar(title="Tapir running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("tapir.pdf")
  df2["cilksanprace"].plot.bar(title="Cilksanprace running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("cilksanprace.pdf")
  df2["cilksan"].plot.bar(title="Cilksan running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("cilksan.pdf")
  plt.show()

def plot_iaf(df):
  df2 = df.min(axis=1).unstack(0).unstack(1)
  print(df2)
  df2.plot(title="Tapir and Cilkiaf running times", marker="x", linestyle="none", xticks=range(len(df2)))
  configure_plot()
  plt.savefig("all.pdf")
  plt.show()
  return

 # df2 = df.min(axis=1).unstack(0).unstack(1)
  #df2.plot.bar(title="Tapir and Cilkiaf running times", xlabel="Program", ylabel="Runtime (s)", logy=True) 
  df2["tapir"].plot.bar(title="Tapir running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("tapir.pdf")
  df2["cilkiaf"].plot.bar(title="Cilkiaf running times", xlabel="Program", ylabel="Runtime (s)", logy=True)
  plt.savefig("cilkiaf.pdf")

df = cilk5_gather()
print(df)

plot_prace(df)

