import pandas as pd
import re
import matplotlib.pyplot as plt
from random import random

ntrials=2

# The compilers and prefixes variables determine what is plotted
# Prefixes are used for regression plots

# IAF
compilers = ["cilkiaf", "tapir"]
prefixes = ["simpleopt", "noopt", "locktest", "2_10_sampling"]

# Cilkprace
#compilers = ["cilksanprace", "cilksan", "tapir"]
#prefixes = ["baseline"]


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
    return [0] * ntrials;

  #print(target)
  #print(results)
    
  return results
  
  

def cilk5_gather(prefix):
  programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "nqueens", "qsort", "rectmul", "strassen"]

  # LAYOUT: Compilers, Programs, Workers
  index = pd.MultiIndex.from_product([compilers, programs, workers],names=["Compiler", "Program", "Worker"])

  data = []

  for c in compilers:
    for p in programs:
      for w in workers:
        data.append(parse_file("cilk5", c, p, w))

  df = pd.DataFrame(data, index)
  df.to_csv(prefix + ".csv")

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

def plot(df, prefix):
  # All plot is harder to make
  df2 = df.min(axis=1).unstack(0).unstack(1)
  print(df2)

  for c in compilers:
    df2[c].plot.bar(title=c + " running times (" + prefix + ")")
    #df2[c].plot.bar(title=c + " running times", xticks=range(len(df2)))
    configure_plot()

    plt.savefig(prefix+"_"+c+".pdf")

def plot_rel(data, baseline, prefix):
  data2 = data.min(axis=1).unstack(0).unstack(1)
  baseline2 = baseline.min(axis=1).unstack(0).unstack(1)
  df2 = data2/baseline2
  print(df2)
  
  for c in compilers:
    df2[c].plot.bar(title=c + " slowdown (" + prefix + ")")
    configure_plot()
    plt.ylabel("Slowdown Factor")

    plt.savefig(prefix+"_"+c+"_rel.pdf")

def plot_lines(df, prefix):
  # All plot is harder to make
  df2 = df.min(axis=1)
  for program, df3 in df2.groupby("Program"):
    df4 = df3.unstack("Compiler").droplevel("Program")
    print(df4)
    print(df4.index)
    df4.plot(title=program + " running times (" + prefix + ")",
            marker='o')
    configure_plot()

    plt.xscale("log")
    plt.yscale("log")

    plt.savefig(prefix+"_line_"+program+".pdf")

def plot_rel_tapir(df, prefix):
  baseline = df.min(axis=1).unstack(0).unstack(1)["tapir"]
  
  for c in compilers:
    if c == "tapir":
      continue
    data = df.min(axis=1).unstack(0).unstack(1)[c]
    df2 = data/baseline
    print(df2)
    df2.plot.bar(title=c + " slowdown (" + prefix + ")")
    configure_plot()
    plt.ylabel("Slowdown Factor vs Tapir")
    plt.savefig(prefix+"_"+c+"_slowdown.pdf")
  

def plot_regression():
  for p in prefixes:
    pass #TODO: Plot the speedup over time. Maybe use Geo Mean? 

    
def plot_all():
  for p in prefixes:
    df = read_csv(p + ".csv")
    plot(df, p)
    plot_rel_tapir(df, p)
    plot_lines(df, p)


def plot_new(prefix):
  df = cilk5_gather(prefix)
  print(df)
  plot(df, prefix)
  plot_rel_tapir(df, prefix)

#plot_new("test")
#plt.show()

plot_all()
plt.show()

