#!/bin/bash
#PBS -N dask-wordcount
#PBS -l select=6:ncpus=4:mem=20G
#PBS -l walltime=01:00:00

# Qsub example for CNES HAL

#Environment sourcing
module load python/3.5.2
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

