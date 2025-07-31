import os
import sys
import zipfile
import numpy as np
import subprocess
np.set_printoptions(suppress=True)

# Parameter options
sqrts = [1, 3, 7, 20, 50, 100, 300, 1000]
channels = ["LO", "NLO", "NNLO"]
runtimes = [86400,432000,1209600]
cpus = [10,10,16]
start_dir = os.getcwd()

# PDF dictionaries: channel -> [(PDF string, tag), ...]
pdf_dict = {
    "LO": [
        ("NNPDF40_lo_as_01180[0]", "NNPDF40"),
        ("MSHT20lo_as130[0]",      "MSHT20"),
        ("CT18LO[0]",              "CT18"),
    ],
    "NLO": [
        ("NNPDF40_nlo_as_01180[0]", "NNPDF40"),
        ("MSHT20nlo_as118[0]",      "MSHT20"),
        ("CT18NLO[0]",              "CT18"),
    ],
    "NNLO": [
        ("NNPDF40_nnlo_as_01180[0]", "NNPDF40"),
        ("MSHT20nnlo_as118[0]",      "MSHT20"),
        ("CT18NNLO[0]",              "CT18"),
    ]
}

# Template with placeholders
template = """PROCESS  JJ
  collider = pp  
  sqrts = {sqrts}000
  jet = antikt[0.7]  
  jet_exclusive = .false.  
  jet_recomb = V4
END_PROCESS

RUN  {run_name}
  PDF = {pdf}
  tcut = 1d-8
  lips_reduce = .true. 
  multi_channel = -3
  warmup = 140000000[10]!please keep this line as it is
END_RUN

PARAMETERS
END_PARAMETERS

SELECTORS
  select njets min = 1
  select jets_pt min = 1
  select jets_abs_y max = 5.0
END_SELECTORS

HISTOGRAMS

  cross > cross_1GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 1
  END_HISTOGRAM_SELECTORS

  cross > cross_2GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 2
  END_HISTOGRAM_SELECTORS

  cross > cross_5GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 5
  END_HISTOGRAM_SELECTORS

  cross > cross_10GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 10
  END_HISTOGRAM_SELECTORS

  cross > cross_20GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 20
  END_HISTOGRAM_SELECTORS

  cross > cross_35GeV
  HISTOGRAM_SELECTORS
    select ptj1 min = 35
  END_HISTOGRAM_SELECTORS

END_HISTOGRAMS

SCALES
  mur = 1.0 * ht_part    muf = 1.0 * ht_part
  mur = 0.5 * ht_part    muf = 0.5 * ht_part
  mur = 2.0 * ht_part    muf = 2.0 * ht_part
  mur = 0.5 * ht_part    muf = 1.0 * ht_part
  mur = 2.0 * ht_part    muf = 1.0 * ht_part
  mur = 1.0 * ht_part    muf = 0.5 * ht_part
  mur = 1.0 * ht_part    muf = 2.0 * ht_part
END_SCALES

CHANNELS 
  {channel}
END_CHANNELS

REWEIGHT ptj1**6
"""

# Output directory
runcard_dir = "output"
os.makedirs(runcard_dir, exist_ok=True)

for channel in channels:
    for pdf, pdf_tag in pdf_dict[channel]:
        folder_path = os.path.join(runcard_dir, channel, pdf_tag,"runcard")
        os.makedirs(folder_path, exist_ok=True)
        for s in sqrts:
            filename = f"sqrts={s}TeV_{channel}_{pdf_tag}.run"
            run_name = filename[:-4]  # Remove the .run extension
            file_content = template.format(
                sqrts=s,
                pdf=pdf,
                channel=channel,
                run_name=run_name,
            )
            with open(os.path.join(folder_path, filename), "w") as f:
                f.write(file_content)

os.chdir(start_dir)

# Create the shell script content
script_content = """#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 {channel} {pdf} {sqrts}"
    exit 1
fi

# Assign input arguments to variables
channel=$1
pdf=$2
sqrts=$3

# Run the nnlojet command
nnlojet-run submit "sqrts=${sqrts}TeV_${channel}_${pdf}"

# Change to the specified directory
cd "sqrts=${sqrts}TeV_${channel}_${pdf}" || { echo "Directory not found"; exit 1; }

# Rename directories for transferring output
mv "raw" "raw_sqrts=${sqrts}TeV"
mv "result" "result_sqrts=${sqrts}TeV"
"""

# Create the submission file content
submit_content = """universe = vanilla
executable = run_nnlojet.sh
arguments = "{channel} {pdf_tag} {s}"
getenv = True
transfer_input_files = sqrts={s}TeV_{channel}_{pdf_tag}
transfer_output_files = sqrts={s}TeV_{channel}_{pdf_tag}/result_sqrts={s}TeV
+MaxRuntime = {runtime} 
log = sqrts={s}TeV_{channel}_{pdf_tag}/{job_name}.log
output = sqrts={s}TeV_{channel}_{pdf_tag}/{job_name}.out
error = sqrts={s}TeV_{channel}_{pdf_tag}/{job_name}.err   
request_cpus={cpu}
queue

"""


for channel,runtime,cpu in zip(channels,runtimes,cpus):
    for pdf, pdf_tag in pdf_dict[channel]:
        # Define the path for the shell script
        target_dir = f"{start_dir}/output/{channel}/{pdf_tag}"
        script_path = f"{target_dir}/run_nnlojet.sh"
        submission_file_path = f"{target_dir}/submit.sub"

        # Write the script to the file
        with open(script_path, 'w') as script_file:
            script_file.write(script_content)
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        with open(submission_file_path, 'w') as f:
            for s in sqrts:
                job_name = f"job_{s}TeV"
                submission = submit_content.format(
                    channel=channel,
                    pdf_tag=pdf_tag,
                    s=s,
                    runtime=runtime,
                    job_name=job_name,
                    cpu = cpu
                )
                f.write(submission)

print(f"All directories, runcards, scripts and submission files have been generated in '{start_dir}'.")

os.chdir(start_dir)
