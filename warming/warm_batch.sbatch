#!/bin/bash
#SBATCH --error=/home/abou/few-shot-NLP/ProtoNER/warming/error_%j.log
#SBATCH --output=/home/abou/few-shot-NLP/ProtoNER/warming/out_%j.log
#SBATCH --job-name=protoner-simple_base
#SBATCH --partition=gpu
#SBATCH -w node5
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
#SBATCH --ntasks-per-node=4

set -e          # exit on command errors
set -o pipefail # capture fail exit codes in piped commands
#set -u          # treat unset variables and parameters as an error when performing parameter expansion
#set -o xtrace

# $1: code directory
# $2: configuration file
# $3: result directory name
# $4: directory for saving results

CODE_DIR=$1
CONFIG_FILE=$2
RES_DIRNAME=$3
RES_SAV_DIR=$4

WRK_DIR=/scratch/abou/protoner
IN=$WRK_DIR/IN

mkdir -p $WRK_DIR
mkdir -p $IN
pushd $WRK_DIR
mkdir -p $RES_DIRNAME

echo "=== copy files"
scp -a bergamote2-ib:/home/abou/few-shot-NLP/ProtoNER/. $WRK_DIR

scp bergamote2-ib:/scratch_global/DATASETS/text-embeddings/glove/glove.6B.50d.txt.gz $IN
scp bergamote2-ib:/scratch_global/DATASETS/text-embeddings/elmo/original/elmo_2x4096_512_2048cnn_2xhighway_options.json $IN
scp bergamote2-ib:/scratch_global/DATASETS/text-embeddings/elmo/original/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5 $IN

echo "=== start"
date
echo "hostname $HOSTNAME"
echo "ppid     $PPID"
echo "cuda     $CUDA_VISIBLE_DEVICES"
module load cuda/10.1
source /home/abou/miniconda3/etc/profile.d/conda.sh
conda activate protoner
pushd $WRK_DIR/warming/
stdbuf -o0 -e0 python global_experiment.py
popd
date

echo "=== end"

echo "=== clean working directory and save results"
rm -f $IN/*
rmdir $IN
tar cvfj $RES_DIRNAME.tbz2 $RES_DIRNAME
scp $RES_DIRNAME.tbz2 bergamote2-ib:$RES_SAV_DIR
rm -fr $RES_DIRNAME
rm -f $RES_DIRNAME.tbz2
rmdir /scratch/abou/protoner
