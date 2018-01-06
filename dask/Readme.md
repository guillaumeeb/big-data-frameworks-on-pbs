# Overview

Dask is launched with an existing python environment available on a distributed storage space (either with conda or virtual env or plain python installation). The idea is to book several chunks using PBS qsub, and then to start a dask-scheduler on one chunk, and dask-workers on the others, using `pbsdsh` command. So once Dask is installed, the only thing to do is launch a PBS script with the right commands.

The only difficulty is to propagate correct ENV variables in this script with pbsdsh, thus the first lines with the exports. It is also very important to use PBS ENV variable $TMPDIR as Dask local storage.

This Readme and scripts provided are inspired by several sources:
* https://github.com/dask/distributed/issues/1260
* https://github.com/pangeo-data/pangeo/wiki/Getting-Started-with-Dask-on-Cheyenne
* http://dask.pydata.org/en/latest/examples/bag-word-count-hdfs.html

This readme presents the scripts (maybe more up to date) stored in the same directory.

# Starting a Dask cluster

Starting a cluster without runninga dask python script straight away is useful when experimenting or developing/debugging an app. It provides an available cluster on which testing heavy processing interactively. The idea is to start a cluster and then connect to it from a Jupyter Notebook or ipython console. For production applications, it is better not to use this cluster mode but to launch the app right after starting the cluster in the PBS script (see below).

Following script can be use to start a Dask cluster :
```shell
#!/bin/bash
#PBS -N dask-cluster-path
#PBS -l select=9:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub template for CNES HAL
# Scheduler: PBS

# This writes a scheduler.json file into your home directory
# You can then connect with the following Python code
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='scheduler.json')

#Environment sourcing
export PYTHONHOME=/work/logiciels/rh7/Python/3.5.2
export PATH=$PYTHONHOME/bin:$PATH
export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PAT
export PKG_CONFIG_PATH=$PYTHONHOME/lib/pkgconfig
ENV_SOURCE="source ~/.bashrc; export PYTHONHOME=$PYTHONHOME; export PATH=$PYTHONHOME/bin:$PATH; export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PATH; export PKG_CONFIG_PATH=$PYTHONHOME/lib/pkgconfig:$PKG_CONFIG_PATH"
rm -f $PBS_O_WORKDIR/scheduler.json

#Options
export OMP_NUM_THREADS=1
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY_LIMIT="18e9"
INTERFACE="--interface ib0 "

# Run Dask Scheduler
echo "*** Launching Dask Scheduler ***"
pbsdsh -n 0 -- /bin/bash -c "$ENV_SOURCE; dask-scheduler $INTERFACE --scheduler-file $PBS_O_WORKDIR/scheduler.json  > $PBS_O_WORKDIR/$PBS_JOBID-scheduler-$PBS_TASKNUM.log 2>&1;"&

#Number of chunks
nbNodes=`cat $PBS_NODEFILE | wc -l`

echo "*** Starting Workers on Other $nbNodes Nodes ***"
for ((i=1; i<$nbNodes; i+=1)); do
    pbsdsh -n ${i} -- /bin/bash -c "$ENV_SOURCE; dask-worker $INTERFACE --scheduler-file $PBS_O_WORKDIR/scheduler.json --nthreads $NCPUS --memory-limit $MEMORY_LIMIT --local-directory $TMPDIR --name worker-${i};"&
done

echo "*** Dask cluster is starting ***"
sleep 3600
```

# Using the started Dask cluster 
As indicated in the script provided in this folder, a scheduler.json file is created under the working directory when submitting the script. It is this way really simple to connect to the created dask cluster.

First, we need to load our python interpreter, and open an interactive python console:
````
ipython
````
Next, it is easy to connect to the cluster using Client API and apply operations:
```python
In [1]: from dask.distributed import Client
In [3]: client = Client(scheduler_file='scheduler.json')
In [4]: client
Out[4]: <Client: scheduler='tcp://10.120.40.54:8786' processes=8 cores=32>
In [17]: import dask.dataframe as dd
In [21]: ddf = dd.read_csv('/work/ADM/hpc/eynardbg/supportHPC/LUT_6SV_DESERT_SENTINEL2BMSIB_B12.txt', delim_whitespace=True, header=None)
In [25]: ddf.head()
Out[25]:
   0   1   2    3      4    5    6    7        8        9        10   11  \
0   0   0   0  0.1  940.0  0.1  0.0  0.2  0.98302  0.98302  0.96870  0.0
1   5   0   0  0.1  940.0  0.1  0.0  0.2  0.98296  0.98302  0.96864  0.0
2  10   0   0  0.1  940.0  0.1  0.0  0.2  0.98278  0.98302  0.96848  0.0
3  15   0   0  0.1  940.0  0.1  0.0  0.2  0.98247  0.98302  0.96821  0.0
4  20   0   0  0.1  940.0  0.1  0.0  0.2  0.98202  0.98302  0.96783  0.0

```

# The production way: start a cluster and launch a script right after
Once dask code is OK, just use the same script for starting a cluster but with a call to the python code instead of the sleep. It is as simple as that.
````
#!/bin/bash
#PBS -N dask-wordcount
#PBS -l select=9:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub template for CNES HAL
# Scheduler: PBS

# This writes a scheduler.json file into your home directory
# You can then connect with the following Python code
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='scheduler.json')

#Environment sourcing
export PYTHONHOME=/work/logiciels/rh7/Python/3.5.2
export PATH=$PYTHONHOME/bin:$PATH
export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PAT
export PKG_CONFIG_PATH=$PYTHONHOME/lib/pkgconfig
ENV_SOURCE="source ~/.bashrc; export PYTHONHOME=$PYTHONHOME; export PATH=$PYTHONHOME/bin:$PATH; export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PATH; export PKG_CONFIG_PATH=$PYTHONHOME/lib/pkgconfig:$PKG_CONFIG_PATH"
rm -f $PBS_O_WORKDIR/scheduler.json

#Options
export OMP_NUM_THREADS=1
NCPUS=4 #Bug in NCPUS variable in our PBS install
MEMORY_LIMIT="18e9"
INTERFACE="--interface ib0 "

# Run Dask Scheduler
echo "*** Launching Dask Scheduler ***"
pbsdsh -n 0 -- /bin/bash -c "$ENV_SOURCE; dask-scheduler $INTERFACE --scheduler-file $PBS_O_WORKDIR/scheduler.json  > $PBS_O_WORKDIR/$PBS_JOBID-scheduler-$PBS_TASKNUM.log 2>&1;"&

#Number of chunks
nbNodes=`cat $PBS_NODEFILE | wc -l`

echo "*** Starting Workers on Other $nbNodes Nodes ***"
for ((i=1; i<$nbNodes; i+=1)); do
    pbsdsh -n ${i} -- /bin/bash -c "$ENV_SOURCE; dask-worker $INTERFACE --scheduler-file $PBS_O_WORKDIR/scheduler.json --nthreads $NCPUS --memory-limit $MEMORY_LIMIT --local-directory $TMPDIR --name worker-${i};"&
done

echo "*** Launching wordcount ***"
cd $PBS_O_WORKDIR/
python dask-wordcount.py
````

# Dask Bokeh UI

In order to monitor applications executed on the cluster, you can use the Spark UI. We must first get the node on which dask-scheduler has been launched, using the following command:
````
$ cat scheduler.json
{
  "type": "Scheduler",
  "address": "tcp://10.135.36.50:8786",
  "workers": {},
  "services": {
    "http": 9786,
    "bokeh": 8787
  },
  "id": "Scheduler-14dafe2c-89bc-4a58-b637-d27a5eecf9e1"
}
````

We see here that the scheduler node is 10.135.36.50. We must thus connect to it.
Default UI port is 8787, so the URL to use is  http://$IP:8787/status, in our case: http://10.135.36.50:8787/status.
````
firefox http://10.135.36.50:8787/status
````
