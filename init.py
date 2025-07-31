import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('channel', choices=["LO", "NLO", "NNLO"], help='Channel to process')
parser.add_argument('pdf', choices=["CT18", "MSHT20", "NNPDF40"], help='PDF to process')
parser.add_argument('policy', choices=["local", "htcondor"], help='submission policy')
args = parser.parse_args()

channel = args.channel
pdf = args.pdf
policy = args.policy

#channel = input("Channel(LO,NLO,NNLO)")
#pdf = input("pdf(CT18,MSHT20,NNPDF40)")

ch = channel.lower()
if channel == "LO":
    maxjob = 100
    maxCjob = 13
elif channel == "NLO":
    maxjob = 1000
    maxCjob = 39
elif channel == "NNLO":
    maxjob = 10000
    maxCjob = 91

sqrts = [1, 3, 7, 20, 50, 100, 300, 1000]
start_dir = os.getcwd()

target_dir = f"output/{channel}/{pdf}"
# Step 1: Change to the target directory
os.chdir(target_dir)

for s in sqrts:
    # Step 2: Prepare the command
    command = [
        "nnlojet-run",
        "init",
        f"runcard/sqrts={s}TeV_{channel}_{pdf}.run"
    ]

    # Step 3: Prepare the responses as a single string, each followed by a newline
    
    if policy == "local":
        responses = "\n".join([
            "y",
            "local",
            f"{ch}",
            "0.05",
            "3600",
            "n",
            f"{maxjob}",
            "10"
        ]) + "\n"
    
    elif policy == "htcondor":
        responses = "\n".join([
            "y",
            "htcondor",
            f"{ch}",
            "0.05",
            "3600",
            "n",
            f"{maxjob}",
            f"{maxCjob}",
            "60",
            "1"
        ]) + "\n"

    # Step 4: Run the command and pass responses
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # Use text mode for easy string handling (Python 3.7+)
    )

    stdout, stderr = process.communicate(input=responses)

print(f"runs for {pdf} at {channel} have been initialised.")

if policy == "local":
    print(f"Use 'condor_submit submit.sub' to submit all the runs.")

elif policy == "htcondor":    
    print(f"Use 'nnlojet-run submit sqrts='s'TeV_{channel}_{pdf}' to submit each sqrt(s) run replacing s by the number.")

