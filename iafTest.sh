#!/usr/bin/env bash

export CILKIAF_CACHE=65536

rm cilk5/Run*
#bash regressionTest.sh -t -iaf -w=48,24,1
bash regressionTest.sh -t -iaf -w=1
tar -czf results.tar.gz cilk5/Run*

