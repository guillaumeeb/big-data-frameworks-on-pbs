# Big Data or graph frameworks on PBS

## Introduction

This projects contains tooling and documentation for launching Spark, Flink or Dask on a PBS cluster that has access to
a shared file system.

The mechanisms are always the same : 
 1. qsub a PBS job which takes sevral chunks using select option
 2. Use pbs-dsh command to start scheduler and workers on reserved chunks
 3. Either wait for qdel or submit a given application to the newly started cluster.

See how it works and how to use the provided tooling in each framework directory:
* [Spark](spark)
* [Dask](dask)
* [Flink (in progress)](flink)

## Quick example

These tools are made for being easy to use, once downloaded into your cluster, you will be able to start a Spark
application as easy as that:
````bash
#!/bin/bash
#PBS -N spark-cluster-path
#PBS -l select=9:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub template for CNES HAL
# Scheduler: PBS

#Environment
export JAVA_HOME=/work/logiciels/rhall/jdk/1.8.0_112
export SPARK_HOME=/work/logiciels/rhall/spark/2.2.1
export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH

$PBS_O_WORKDIR/pbs-launch-spark -n 4 -m "18000M" $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````

## Contact

This project has been tested on @CNES (Centre National d'Etude Spatial -- the French Space Agency) HPC cluster.
Feel free to open an issue to ask for a correction or even for help, We will be glad to help.