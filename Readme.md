# Big Data or grah frameworks on PBS

## Introduction

This projects contains tooling and documentation for launching Spark, Flink or Dask on a PBS cluster with 
a shared repository.

The mechanisms are always the same : 
 1. qsub a PBS job which takes sevral chunks using select option
 2. Use pbs-dsh command to start scheduler and workers on reserved chunks
 3. Either wait for qdel or submit a given application to the newly started cluster.

## Spark usage

### Overview

This projects contains tooling and documentation for launching a Spark cluster and Application on PBS Pro.
By default, it works as follows:  
 1. qsub the python script pbs-spark-launcher,  
 2. A Spark standalone master is started on the MOM (Parent) PBS node,  
 3. Using pbsdsh (or ssh), Spark standalone slaves are started on every node requested to PBS,  
 4. A time wait is performed in order to wait for all slaves to be up,
 5. Two possiblities:  
   a. Either a Spark application is launched, and at its end the Spark cluster is killed,  
   b. Either the cluster stays alive waiting for applications, until wall time is reached or qdel is invoked.

### Project organisation

Some pbs examples in src/test/pbs-batch folder. This scripts uses the python spark launcher in src/main/python folder.
It needs to have Spark binaries deployed on GPFS or shared file system.
A module is described in src/main/module, with a readme on its install procedure.

## How to use it

### With the module

Prepare a pbs script file as presented in src/test/pbs-batch/.  
In this script file, after the #PBS directives, you must have at leat the following lines:   
```bash
module load spark-on-pbs/2.0.2
pbs-spark-launcher --cores XX --memory YYmb ZZ
```

Either you don have an application to launch yet, so ZZ is empty. It will thus launch a cluster waiting 
for an application to be run.
Either you have, put it in the place of ZZ with all arguments, the cluster will start launch the application, 
and shutdown on the end, saving cluster cpu time.

It is mandatory to repeat the reserved resources both in PBS directive and to the pbs-spark-launcher script.

### Without the module

You need to have a java JRE installed (at least version 1.7), Spark binaries in a shared space (eg. GPFS), and to download the
pbs-spark-launcher script. Then, configure your spark binaries java home corrcetly, and instead of loading module, just
define SPARK_HOME inside your pbs script file, as in src/test/pbs-batch/spark-mywordcount.pbs  
Then you just have to call the downloaded script like above. So this gives:  
```bash
SPARK_HOME=/work/myuser/mysparkhome
./pbs-spark-launcher --cores XX --memory YYmb ZZ
```

### Other tools

For seeing historycal job, you can also start the spark history server using $SPARK_HOME/sbin/start-history-server.sh. 
Do not forget to load spark module first.
