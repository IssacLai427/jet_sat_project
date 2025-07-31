This file will describe how to run the LO, NLO, and NNLO jobs in NNLOJET for the low-x jet saturation project.

When cloning this repository for the first time, please run setup.sh in the directory.\
The script downloads the tar for nnlojet in https://nnlojet.hepforge.org/releases.html in get_tar as well as the required PDF functions from https://lhapdfsets.web.cern.ch/current/.
The latter is then unzipped to the LHAPDFsets directory. After extracting nnlojet and before installation, the script will replace the dokan subdirectory with the one directly cloned from the repository https://github.com/aykhuss/dokan.git.

After logging into a lxplus host and before running any python scripts, remember to source .bashrc_nnlojet first. This is to ensure that nnlojet has the correct path to python packages and lhapdf datasets.

If you would like to update nnlojet in the future, edit the sh script according to the comments and recompile it. Then remove the entire old nnlojet directory and run setup.sh again.\
If it is only dokan that needs to be updated, go to nnlojet-va.b.c/dokan and execute the command "git pull", open setup.sh and copy the lines as indicated in the comments.\
Then, in the directory nnlojet-va.b.c/, remove nnlojet-va.b.c/build and run the copied lines.

For the detailed manual of nnlojet please refer to https://nnlojet.hepforge.org/manual.html.

There are 3 python scripts in this repository and shall be used in this order:\

pre-run.py\
This script contains the template for the runcards necessary for an nnlojet work submission, as well as the required shell script and condor submit file when the work is intended to execute with local policy and be submitted to condor manually.\
Running once will create the directory output, which includes all the above for all orders and PDFs.

init.py {channel} {pdf} {policy}\
This script initialises all the jobs with the same channel (LO/NLO/NNLO) and PDF (CT18/MSHT20/NNPDF40). The policy can be set to be either local or htcondor.\
Local policy corresponds to having a worker node in htcondor to run a complete job. The user will need to submit to condor by themselves.\
Htcondor policy will make the nnlojet framework handle the condor submissions. However, the job will be interrupted if an SSH disconnection is encountered.\
When the script completes, it will exit at the run directory and provide the shell command (different for the two policies) for job submission.

plot.py {channel} {pdf} {policy}\
This script is used after all the jobs with the same channel and PDF have finished. If they are run with local policy, there is an additional step done by the script to move the output files.\
It will produce a plot of cross-section vs. jet_pT_min for different sqrt(s) in the run directory.\
It will also append a curve to the plot jet_pT_min_at_NN vs. sqrt(s) located in output. The data is also stored in a .root file there.


