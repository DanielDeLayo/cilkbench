#!/usr/bin/env bash

export CILKIAF_CACHE=10000

bash regressionTest.sh -t -iaf -cilk -w=48,24,1

