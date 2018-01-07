# Spark on PBS

## Overview

This directory contains tooling for launching a Spark cluster and Application on PBS Pro. This readme is considered as
the associated documentation.

How this works:
 1. Prerequisite: Java and Spark must be installed on a shared folder (GPFS or equivalent),
   * For Spark, you just need to download a precompiled version on the download page at http://spark.apache.org/downloads.html
 2. Chunk servers are booked using PBS qsub command.
 3. Using pbsdsh, Spark standalone master and slaves are started on every node requested to PBS,

The work here is inspired both from the work on Dask (see dask folder of the repository) and at the beginning by what
has been done here: https://www.osc.edu/~troy/pbstools/man/pbs-spark-submit.

## Project organisation

Some pbs examples are in the _examples_ folder. they provide different ways of starting a cluster and launching
an app: using directly the installation PATH, with an lmod based module, with an intermediate script (see below).
The lmod module file is provided in module directory.
In the current directory, the pbs-launch-spark shell script simplifies the PBS script.

## How to use it

### Functionnality

Two main possibilities are given to the user:
* Just start a Spark cluster using PBS, and then use it from an interactive terminal using spark-submit or other commands,
* Start a cluster and submit right after an application using spark-submit, this should be the production use of this tool.

### How this works

This paragraph shows how the spark cluster is started on PBS using just a standalone PBS script
(given that Java and Spark binaries are already available somewhere). This is mostly for explanation purpose as using
the pbs-launch-spark script (see below) is much simpler.

Three main part are perfomed to correctly start Spark
#### Prepare environment variables:

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
It tells where are installed Java and Spark, to not demonize spark (useful later for pbsdsh commands, and then prepare
a source command to use in ``pbsdsh`` (which launch commands without standard user env).
We then also position the number of cores and memory to use per Spark slaves.

#### Start Spark using pbsdsh and correct options

````bash
# Run Spark Master
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

#### Either wait or launch an application

````bash
echo "*** Submitting app ***"
spark-submit --master $SPARK_MASTER $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````
The spark-submit command can be used directly in the script, or you can also just wait in it, and use spark-submit or
even spark-shell mutliple times from a terminal (see below).
````bash
echo "*** Spark cluster is starting ***"
sleep 3600
````

### Plain PBS script
So this gives us the following example PBS script, which can be used as is:
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

# Run Spark Master
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

### Using intermediate script

In order to simplify the use of Spark, a bash script has been developed: pbs-launch-spark. Its usage is the
following:
````
./pbs-launch-spark -n ncpus -m memory [-p properties-file] [sparkapp]
  ncpus: number of cpus per spark slave
  memory: memory heap of spark slave
  properties-file: spark properties file
  sparkapp: spark opitions and/or applications args
````

It must be launched inside a PBS script, as demonstrated below.
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
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY="18000M"

$PBS_O_WORKDIR/pbs-launch-spark -n $NCPUS -m $MEMORY $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````

This way, the PBS script is much shorter, and pbs-launch-spark also gives the possibility to provide a properties-file
for giving additional options like storing history of apps.

### Using a module (lmod here)

For still more simplicity, it is possible to use a predefined module on a cluster. An example is provided (in _module_ directory) for lmod.
Once this module is deployed in your environment, launching a cluster is as simple as that:

````bash
#!/bin/bash
#PBS -N spark-cluster-path
#PBS -l select=9:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub template for CNES HAL
# Scheduler: PBS

module load spark
pbs-launch-spark -n 4 -m "18000M"
````

### Using a started cluster
If you've only started a cluster (with no app inside the PBS script), you can then launch spark commands from outside.
You've just got to know the spark master host, which can be done (for example) using qstat comand:
````bash
$ qstat -n1 2244744.admin01

admin01:
                                                            Req'd  Req'd   Elap
Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
2244744.admin01 eynardbg qt1h     spark-clus   3133   9  36  180gb 01:00 R 00:00 node065/0*4+node065/1*4+node065/2*4+node065/3*4+node065/4*4+node065/5*4+node066/0*4+node066/1*4+node066/2*4
````

Spark Master is started on the first node, node065 here.
Then, just issue a spark-submit:
````bash
$ export SPARK_HOME=/work/logiciels/rhall/spark/2.2.1/
$ $SPARK_HOME/bin/spark-submit --master spark://node065:7077 $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````

You can also use spark-shell:
````bash
$ $SPARK_HOME/bin/spark-shell --master spark://node065:7077
Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
18/01/07 16:19:23 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Spark context Web UI available at http://xx.yy.zz.21:4040
Spark context available as 'sc' (master = spark://node065:7077, app id = app-20180107161924-0002).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.2.1
      /_/

Using Scala version 2.11.8 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_112)
Type in expressions to have them evaluated.
Type :help for more information.

scala>
````

Et voilà!

### Spark UI

Spark UI is started along the master process, on port 8080 by default.

So the only thing to do next is to open a browser on the Master
UI URL:
````bash
firefox http://node065:8080
````

### Spark history server

If you want to enable history of Spark applications in order to be able to take a look at the execution stats and informations
after the app is over, you've got to enable the write of history file. This can be done by modifying the following properties of
the application execution:
````bash
spark.eventLog.enabled           true
spark.eventLog.dir               file:///work/ADM/hpc/eynardbg/BigData/spark/history
spark.history.fs.logDirectory    file:///work/ADM/hpc/eynardbg/BigData/spark/history
````

If you've got your own installation of Spark, just modify the spark-defaults.conf in the $SPARK_HOME/conf folder.
If not, you can still create a properties file in a custom directory, and use it. Then, just use the pbs-launch-spark
script with the -p argument:
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
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY="18000M"

$PBS_O_WORKDIR/pbs-launch-spark -n $NCPUS -m $MEMORY -p $PBS_O_WORKDIR/spark-defaults.conf $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````
Or if you've started a independant cluster, use --properties-file with spark-submit:
````bash
$SPARK_HOME/bin/spark-submit --master spark://node029:7077 --properties-file spark-defaults.conf $SPARK_HOME/examples/src/main/python/wordcount.py $SPARK_HOME/conf/
````

To visualize the history, you must then start the history server, this can be done this way:
````bash
export SPARK_LOG_DIR=spark-logs; $SPARK_HOME/sbin/start-history-server.sh --properties-file spark-defaults.conf
````

It is important to position SPARK_LOG_DIR to a (existing) directory you own.

Then, if you've not modified the history server port, just open firefox to http://yourhost:18080.

### Improvements/to do
Currently, the started cluster does not use a provided InfinityBand or other High speed network if provided. It only use
standard ethernet network. This can be an issue when moving arround big volumes.
