import pandas as pd
import re
import matplotlib.pyplot as plt
from random import random
import os
import tarfile

ntrials=1
sampling_log = 7
sampling=2 ** sampling_log
one_sample = True
one_sample = False


wrong_invariant_warning = "[Uninit]"
use_wrong_invariant = None
#use_wrong_invariant = False


cut = 0
#cut = 100

workers = ["1", "4", "16"]
workers = ["1"]


def set_correctness(value):
  global use_wrong_invariant, wrong_invariant_warning
  use_wrong_invariant = value
  if (use_wrong_invariant):
    wrong_invariant_warning = " [Incorrect]"
  else:
    wrong_invariant_warning = ""
  
set_correctness(True)

def untar(what):
  with tarfile.open(what, "r:gz") as tf:
    tf.extractall()

#Returns a list of the running time for the given compiler, worker, program tuple
def parse_file(subdir, c, p, w):
  target = subdir + "/Run-" + "-".join([c,p,w]) + ".txt"
  results = None
  
  with open(target, "r") as f:
    results = parse_frames(f, int(w))

  return results


def grab_df(file_handle):
  # Record start
  where = file_handle.tell()
  nextline = file_handle.readline()
  if (nextline[0] == 's' or nextline[0] == 'v'):
    file_handle.seek(where)
    return None
  total, max_cache, total_unsampled = [int(x) for x in nextline.split(",")]
  df = pd.read_table(file_handle, sep=',', names=["Size", "Hits"], skiprows=1, nrows=max_cache, index_col=0) 
  df.attrs['total'] = total
  df["Misses"] = total - df["Hits"]
  if (use_wrong_invariant):
    df["MissRate"] = df["Misses"]/total
  else:
    df["MissRate"] = df["Misses"]/total_unsampled
  # Return to start
  file_handle.seek(where)
  return df

def parse_frames(file_handle, num):
  sampled = {}
  verified = {}

  sampled_total = 0
  real_total = 0
  
  line = file_handle.readline()
  while line:
    if line.startswith("sampled"):
      w = int(line[7:].strip().split(" ")[0])
      part = int(line[7:].strip().split(" ")[1])
      df = grab_df(file_handle)
      if df is not None:
        sampled_total += df.attrs['total']
        if w in sampled:
          sampled[w] = sampled[w].merge(df, left_index=True, right_index=True, suffixes=[None, part])
        else:
          sampled[w] = df
    if line.startswith("verify"):
      w = int(line[6:])
      df = grab_df(file_handle)
      if df is not None:
        real_total += df.attrs['total']
        if w in verified:
          verified[w] = verified[w].merge(df, left_index=True, right_index=True, suffixes=[None, "?"])
        else:
          verified[w] = df
    line = file_handle.readline()
  print("real vs sampled totals:", real_total == int(sampled_total/sampling), ",", real_total, "==",  int(sampled_total/sampling))
  print("real vs sampled total:", real_total == sampled_total, ",", real_total, "==",  sampled_total)

  return (sampled, verified) 


def plot_diff(sampled, verified, p, ax):
  if (one_sample):
    return
  #Force the same x axis
  #fig, ax = plt.subplots()
  ax.set_xlabel("Size (Cachelines)")
  ax.set_ylabel("Missrate Error %")

  ax.set_title(p+ ": Sampled vs Actual missrate errors (Trimmed first " + str(cut) + ")" + wrong_invariant_warning)
  ax.set_title(p+ ": Sampled vs Actual missrate errors" + wrong_invariant_warning)


  for k, v in sampled.items(): 
    rightmost = min(len(sampled[k]), len(verified[k]))
    print(rightmost)
    ax.plot(sampled[k].index[cut:rightmost], 100 * (sampled[k]["MissRate"][cut:rightmost] - verified[k]["MissRate"][cut:rightmost])/ verified[k]["MissRate"][cut:rightmost], color="red", label="Missrate 0 Error", linestyle='--')
    for i in range(1, sampling):  
      ax.plot(sampled[k].index[cut:rightmost], 100 * (sampled[k]["MissRate" + str(i)][cut:rightmost] - verified[k]["MissRate"][cut:rightmost])/ verified[k]["MissRate"][cut:rightmost], color="red", label="Missrate " + str(i) + " Error", linestyle='--')

  # Stop the legend from covering up data
  if (False): #one_sample or sampling < 10):
    ax.legend(bbox_to_anchor=(1.02, .5), loc="center left")
  # Workaround for cut off artists
  plt.tight_layout()
  plt.savefig("verify_diff.pdf")
  #plt.show()

def plot(sampled, verified, p, ax):
  #Force the same x axis
  ax.set_xlabel("Size (Cachelines)")
  ax.set_ylabel("Missrate")
  
  if (verified):
    ax.set_title(p + ": Sampled vs Actual missrate (Trimmed first " + str(cut) + ")" + wrong_invariant_warning)
    ax.set_title(p + ": Sampled vs Actual missrate" + wrong_invariant_warning)
  else:
    ax.set_title(p + ": Sampled missrate (Trimmed first " + str(cut) + ")" + wrong_invariant_warning)

  linestyle = None
  for k, v in sampled.items(): 

    print(sampled[k])
    if (verified):
      print(verified[k])
      linestyle="--"
  
    #Second plot: Missrate
    ax.plot(sampled[k].index[cut:], sampled[k]["MissRate"][cut:], color="red", label="Missrate 0 (Sampled)", linestyle=linestyle)
    # Remaining plots: Extra missrates
    
    if (not one_sample):
      for i in range(1, sampling):
        ax.plot(sampled[k].index[cut:], sampled[k]["MissRate" + str(i)][cut:], color="red", label="Missrate " + str(i) + " (Sampled)", linestyle='--')
    if (verified):
    #First plot: Hitrate
      ax.plot(verified[k].index[cut:], verified[k]["MissRate"][cut:], color="blue", label="Missrate (Actual)")

  # Stop the legend from covering up data
  if (False): #one_sample or sampling < 10):
    ax.legend(bbox_to_anchor=(1.02, .5), loc="center left")
  # Workaround for cut off artists
  plt.tight_layout()
  plt.savefig("verify.pdf")
  #plt.show()


  #plot(sampled, None, p)

  #    plot(sampled, verified, p)
  #    plot_diff(sampled, verified, p)
  #plt.show()

def iaf_sweep(prefix, a, b):
  programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "nqueens", "qsort", "rectmul", "strassen"]
  dfs = []
  for i in range(a, b+1):
    what = prefix + "_2_" + str(i)
  
    untar(what + ".tar.gz")

    for p in programs:
      for w in workers:
        sampled, verified = parse_file("cilk5", "cilkiaf", p, w)
        print(sampled, verified)
        plot(sampled, verified, p + ", " + w)
    plt.show()



def wrong_right_compare(smallest, largest, what):
  global sampling, sampling_log, use_wrong_invariant

  count = largest - smallest + 1

  fig, ax = plt.subplots(count, 2, layout="constrained")
  for sampling_log in range(smallest, largest+1):
    sampling = 2 ** sampling_log
    
    # Right Pass
    set_correctness(True)
    sampled, verified = parse_file("../examples", "cilkiaf", "doubling", str(sampling_log))
    print("SAMPLED", len(sampled), sampled)
    print("VERIFIED", len(verified), verified)
    plot(sampled, verified, "doubling", ax[sampling_log-smallest, 0])
    
    # Wrong Pass
    set_correctness(False)
    sampled, verified = parse_file("../examples", "cilkiaf", "doubling", str(sampling_log))
    print("SAMPLED", len(sampled), sampled)
    print("VERIFIED", len(verified), verified)
    plot(sampled, verified, "doubling", ax[sampling_log-smallest, 1])
    #plt.savefig("doubling_2_" +  str(sampling_log) + ".pdf", dpi=1000)
    #plot_diff(sampled, verified, "doubling", ax[sampling_log-smallest, 1])
    #plt.savefig("doubling_2_" +  str(sampling_log) + "_err.pdf", dpi=1000)
  fig.subplots_adjust(wspace=0.2, hspace=0.2)
  
  

if __name__ == "__main__":
  subdir = "cilk5"
  programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "nqueens", "qsort", "rectmul", "strassen"]
  programs = ["cholesky", "cilksort", "fft", "heat", "lu", "matmul", "qsort", "rectmul", "strassen"]
  #programs = ["fft", "qsort", "rectmul", "strassen", "cilksort"]
  programs = ["fft", "rectmul", "strassen", "matmul", "heat", "cilksort"]
  programs = ["qsort", "fft", "cholesky", "nqueens"]
  #programs = ["qsort", "fft", "cholesky"]
  #programs = ["heat"]
  
  #Hijacking for testing
  #programs = ["boolean"]
  #subdir = "../examples" 
  

  #iaf_sweep("global", 7, 20)
  #plt.show()
  
  wrong_right_compare(2, 10, "doubling")
  plt.show()


  #for p in programs:
  #  for w in workers:
  #    sampled, verified = parse_file(subdir, "cilkiaf", p, w)

  #plot(sampled, None, p)

  #    plot(sampled, verified, p)
  #    plot_diff(sampled, verified, p)
  #plt.show()

  #sampled[0].to_csv("sampled")
  #verified[0].to_csv("verified")
  #df2 = verified[16] / (sampled[16])
  #df2.to_csv("delme")

