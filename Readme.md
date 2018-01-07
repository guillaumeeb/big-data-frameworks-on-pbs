# Big Data or grah frameworks on PBS

## Introduction

This projects contains tooling and documentation for launching Spark, Flink or Dask on a PBS cluster with 
a shared repository. See readme files in all the subdirectories for more informations.

The mechanisms are always the same : 
 1. qsub a PBS job which takes sevral chunks using select option
 2. Use pbs-dsh command to start scheduler and workers on reserved chunks
 3. Either wait for qdel or submit a given application to the newly started cluster.

