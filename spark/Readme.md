# Spark on PBS

## Overview

This directory contains tooling for launching a Spark cluster and Application on PBS Pro. This readme is considered as
the associated documentation.

How this works:
 1. Prerequisite: Java and Spark must be installed on a shared folder (GPFS or equivalent),
   * For Spark, you just need to download a precompiled version on the download page at http://spark.apache.org/downloads.html
 2. Chunk servers are booked using PBS qsub command.
 3. Using pbsdsh, Spark standalone master and slaves are started on every node requested to PBS,

## Project organisation

Some pbs examples in the _examples_ folder. This scripts provides different ways of starting a cluster and launching
an app: using directly the installation PATH, with an lmod based module, with an intermediate script (see below).
The lmod module file is provided in module directory.
In the current directory, the pbs-launch-spark shell script simplifies the PBS script.

## How to use it

### Functionnality

Two main possibilities are given to the user:
* Just start a Spark cluster using PBS, and then use it from an interactive terminal using spark-submot or other commands
* Start a cluster and submit right after an application using spark-submit, this should be the production use of this tool.

### How this works

This paragraph shows how the spark cluster is started on PBS using just a standalone PBS script
(given that Java and Spark binaries are already available somewhere). This is mostly for explanation purpose as using
the pbs-launch-spark script (see below) is much simpler.

Three main part are perfomed to correctly start Spark:
1. Prepare environment variables:
````bash
export JAVA_HOME=/work/logiciels/rhall/jdk/1.8.0_112
export SPARK_HOME=/work/logiciels/rhall/spark/2.2.1
export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH
export SPARK_NO_DAEMONIZE="True"
ENV_SOURCE="source ~/.bashrc; export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export SPARK_NO_DAEMONIZE=$SPARK_NO_DAEMONIZE; export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH"

#Options
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY="18000M"
````
It tells where are installed Java and Spark, to not demonize spark (useful later for pbsdsh commandsà, and then prepare
a source command to use in pbsdsh, which launch commands without standard user env.
We then also position the number of cores and memory to use per Spark slaves.

2. Start Spark using pbsdsh and correct options
````bash
# Run Spark Scheduler
echo "*** Launching Spark Master ***"
pbsdsh -n 0 -- /bin/bash -c "$ENV_SOURCE; $SPARK_HOME/sbin/start-master.sh > $PBS_O_WORKDIR/$PBS_JOBID-spark-master.log 2>&1;"&

SPARK_MASTER="spark://"`head -1 $PBS_NODEFILE`":7077"
#Number of chunks
nbNodes=`cat $PBS_NODEFILE | wc -l`

echo "*** Starting Workers on other $nbNodes Nodes ***"
for ((i=1; i<$nbNodes; i+=1)); do
    pbsdsh -n ${i} -- /bin/bash -c "$ENV_SOURCE; $SPARK_HOME/sbin/start-slave.sh --memory $MEMORY --cores $NCPUS --work-dir $TMPDIR $SPARK_MASTER;"&
done
````

The Spark master is launched on one of the chunks, and slaves on the others. What is important here is the use of PBS
TMPDIR env variable for storing data localy on the compute nodes.

3. Either wait or launch an application
````bash
echo "*** Submitting app ***"
spark-submit --master $SPARK_MASTER $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````
The spark-submit command can be used directly in the script, or you can also just wait in it, and use spark-submit or
even spark-shell mutliple times from a terminal.
````bash
echo "*** Spark cluster is starting ***"
sleep 3600
````

### Plain PBS script
So this gives us the following script, which can be used as is:
````bash
#!/bin/bash
#PBS -N spark-cluster-path
#PBS -l select=9:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub template for CNES HAL
# Scheduler: PBS

#Environment sourcing
export JAVA_HOME=/work/logiciels/rhall/jdk/1.8.0_112
export SPARK_HOME=/work/logiciels/rhall/spark/2.2.1
export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH
export SPARK_NO_DAEMONIZE="True"
ENV_SOURCE="source ~/.bashrc; export JAVA_HOME=$JAVA_HOME; export SPARK_HOME=$SPARK_HOME; export SPARK_NO_DAEMONIZE=$SPARK_NO_DAEMONIZE; export PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH"

#Options
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY="18000M"
INTERFACE="--interface ib0 "

# Run Spark Scheduler
echo "*** Launching Spark Master ***"
pbsdsh -n 0 -- /bin/bash -c "$ENV_SOURCE; $SPARK_HOME/sbin/start-master.sh > $PBS_O_WORKDIR/$PBS_JOBID-spark-master.log 2>&1;"&

SPARK_MASTER="spark://"`head -1 $PBS_NODEFILE`":7077"
#Number of chunks
nbNodes=`cat $PBS_NODEFILE | wc -l`

echo "*** Starting Workers on other $nbNodes Nodes ***"
for ((i=1; i<$nbNodes; i+=1)); do
    pbsdsh -n ${i} -- /bin/bash -c "$ENV_SOURCE; $SPARK_HOME/sbin/start-slave.sh --memory $MEMORY --cores $NCPUS --work-dir $TMPDIR $SPARK_MASTER;"&
done

echo "*** Spark cluster is starting ***"
sleep 3600
````
Prepare a pbs script file as presented in src/test/pbs-batch/.  
In this script file, after the #PBS directives, you must have at leat the following lines:   
```bash
module load spark-on-pbs/2.2.1
pbs-spark-launcher --cores XX --memory YYmb -- ZZ
```

Either you don have an application to launch yet, so -- ZZ is empty. It will thus launch a cluster waiting 
for an application to be run.
Either you have, put it in the place of ZZ with all arguments, the cluster will start launch the application, 
and shutdown on the end, saving cluster cpu time.

It is mandatory to repeat the reserved resources both in PBS directive and to the pbs-spark-launcher script.

### Without the module

You need to have a java JRE installed (at least version 1.7), Spark binaries in a shared space (eg. GPFS, Lustre or at least NFS), and to download the
pbs-spark-launcher script. Then, configure your spark binaries java home correctly, and instead of loading module, just
define SPARK_HOME inside your pbs script file, as in src/test/pbs-batch/spark-mywordcount.pbs  
Then you just have to call the downloaded script like above. So this gives:  
```bash
SPARK_HOME=/work/myuser/mysparkhome
./pbs-spark-launcher --cores XX --memory YYmb ZZ
```

### Other tools

For seeing historycal job, you can also start the spark history server using $SPARK_HOME/sbin/start-history-server.sh. 
Do not forget to load spark module first.
