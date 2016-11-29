# Spark on PBS

## Introduction

### Overview

This projects containes tooling and documentation for launching a Spark cluster and Application on PBS Pro.
By default, it works as follows:  
 1. qsub the python script pbs-spark-launcher,  
 2. A Spark standalone master is started on the MOM (Parent) PBS node,  
 3. Using pbsdsh (or ssh), Spark standalone slaves are started on every node requested to PBS,  
 4. A time wait is performed in order to have all slaves up,
 5. Two possiblities:  
   a. Either a Spark application is launched, and at its end the Spark cluster is killed,  
   b. Either the cluster stays alive waiting for applications, until wall time is reached or qdel is invoked.

### Project organisation

Some pbd examples in src/test/pbs-batch folder. This scripts uses the python spark launcher in src/main/python folder.
It needs to have Spark binaries deployed on GPFS or shared file system.
A module is described in src/main/module, with a readme on its install procedure.

## How to use it

### With the module

Prepare a pbs script file as presented in src/test/pbs-batch/.  
In this script file, after the #PBS directives, you must have at leat the following lines:   
module load spark-on-pbs/2.0.2
pbs-spark-launcher --cores XX --memory YYmb ZZ

Either you don have an application to launch yet, so ZZ is empty. It will thus launch a cluster waiting 
for an application to be run.
Either you have, put it in the place of ZZ with all arguments, the cluster will start launch the application, 
and shutdown on the end, saving cluster cpu time.

It is mandatory to repeat the reserved resources both in PBS directive and to the pbs-spark-launcher script.

### Without the module

You need to have a java JRE installed (at least version 1.7), Spark binaries in a shared space (eg. GPFS), and to download the
pbs-spark-launcher script. Then, configure your spark binaries java home right, and instead of loading module, just
define SPARK_HOME inside your pbs script file, as in src/test/pbs-batch/spark-mywordcount.pbs  
Then you just have to call the downloaded script like above.

### Other tools

For seeing historycal job, you can also start the spark history server using $SPARK_HOME/sbin/start-history-server.sh. 
Don't forget to load the jdk 8 module first: module load jdk/1.8.0_74.
