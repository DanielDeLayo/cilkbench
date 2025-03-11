import pandas as pd
import re
import matplotlib.pyplot as plt
from random import random
import os

ntrials=2

# The compilers and prefixes variables determine what is plotted
# Prefixes are used for regression plots

# IAF
compilers = ["cilkiaf"]

workers = ["1", "24", "48"]

#Returns a list of the running time for the given compiler, worker, program tuple
def parse_file(subdir, c, w, p):
  target = subdir + "/Run-" + "-".join([c,w,p]) + ".txt"
  results = None
  
  with open(target, "r") as f:
    results = parse_frames(f, int(p))

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

def grab_df(file_handle):
  # Record start
  where = file_handle.tell()

  total, max_cache = [int(x) for x in file_handle.readline().split(",")]
  df = pd.read_table(file_handle, sep=',', names=["Size", "Hits"], skiprows=1, nrows=max_cache, index_col=0) 
  df.attrs['total'] = total
  # Return to start
  file_handle.seek(where)
  return df

def parse_frames(file_handle, num):
  sampled = {}
  verified = {}
  line = file_handle.readline()
  while line:
    if line.startswith("sampled"):
      w = int(line[7:])
      if w in sampled:
        sampled[w] = sampled[w].merge(grab_df(file_handle), left_index=True, right_index=True, suffixes=["0", "1"])
      else:
        sampled[w] = grab_df(file_handle)
    if line.startswith("verify"):
      w = int(line[6:])
      if w in verified:
        verified[w] = verified[w].merge(grab_df(file_handle), left_index=True, right_index=True, suffixes=["0", "1"])
      else:
        verified[w] = grab_df(file_handle)
    line = file_handle.readline()

  return (sampled, verified) 


def plot(sampled, verified):
  #Force the same x axis
  fig, ax = plt.subplots()

  #First plot: Hitrate
  ax.plot(verified.index, verified["Hits0"], label="Hitrate Curve (True)")
  ax.set_xlabel("Size (Cachelines)")

  #Second plot: Measured Time
  ax.plot(sampled.index, sampled["Hits0"], color="red", label="Hitrate Curve (Sampled)", linestyle='--')
  ax.legend()
  ax.set_title("Sampled vs True hitrate curve")

  plt.savefig("verify.pdf")
  #plt.show()


sampled, verified = parse_file("cilk5", "cilkiaf", "cholesky", "48")

plot(sampled[0], verified[0])

sampled[0].to_csv("sampled")
verified[0].to_csv("verified")
df2 = verified[16] / (sampled[16])
df2.to_csv("delme")

