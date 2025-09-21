#!/usr/bin/env bash

export CILKIAF_CACHE=65536
export LD_LIBRARY_PATH=/home/daniel/cilkiaf/build/lib:$LD_LIBRARY_PATH

rm cilk5/Run*
#bash regressionTest.sh -t -iaf -w=48,24,1
#bash regressionTest.sh -t -iaf -w=1,2,4,8,16
bash regressionTest.sh -t -iaf -w=1,4,16
tar -czf results.tar.gz cilk5/Run*

