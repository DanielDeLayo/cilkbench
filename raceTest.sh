#!/usr/bin/env bash

#bash regressionTest.sh -t -prace -csan -cprace -w=48,24,1
rm cilk5/Run*
bash regressionTest.sh -cprace -csan -t -w=48,24,1
tar -czf results.tar.gz cilk5/Run*

