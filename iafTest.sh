#!/usr/bin/env bash

export CILKIAF_CACHE=10000

rm cilk5/Run*
bash regressionTest.sh -t -iaf -w=48,24,1

