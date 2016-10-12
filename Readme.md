===========================================================
Spark on PBS
==========================================================

Some pbd examples in src/test/pbs-batch folder. This scripts uses the python spark launcher in src/main/python folder.
They also need to have Spark binaries deployed on GPFS or shared file system.

For seeing historycal job, you can also start the spark history server using $SPARK_HOME/sbin/start-history-server.sh. 
Don't forget to load the jdk 8 module first: module load jdk/1.8.0_74.
