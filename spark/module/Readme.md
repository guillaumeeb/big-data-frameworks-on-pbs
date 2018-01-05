# Module installation instructions

## Software required:

- A Java Virtual Machine: **JDK or JRE**, **1.8** Version is prefered, but 1.7 is OK.
- Python version **2.7**.
- A Spark version packaged for Hadoop 2.7, see http://spark.apache.org/downloads.html. 1.6.x and **2.0.y** are OK.

## Installation

1. Deploy (untar) Spark binaries on a disstributed file system (e.G. GPFS /work). Currently deployed in /work/hpc/modules/install.
2. Configure JAVA_HOME in $SPARJ_HOME/conf/spark-env.sh. (Copy the file from the template provided by spark).
3. Configure job-history folder and activation in spark-default.conf if needed. (Copy again the template provided).
4. Copy in another folder the python script pbs-spark-launcher from this project.

##Module configuration

Module must provide the following things:
- Define SPARK_HOME to the installation folder of Spark.
- Give access to $SPARK_HOME/bin in the PATH.
- Give access to pbs-spark-launcher in the PATH.
