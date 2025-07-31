#!/bin/bash

#Download and extract the tar files
cd get_tar

#comment out the section below if you are only updating nnlojet
cd lhapdf
wget -i list.txt
for f in *.tar.gz; do tar -xzvf "$f" -C ../../LHAPDFsets/; done
cd ..
#comment out the section above if you are only updating nnlojet

#If using other versions of nnlojet, remember to replace all "nnlojet-va.b.c" to the correct name
wget https://nnlojet.hepforge.org/nnlojet-v1.0.2.tar.gz
tar -xzvf nnlojet-v1.0.2.tar.gz -C ..
cd ..

#Install nnlojet
cd nnlojet-v1.0.2

#Replace dokan by directly from git
rm -rf dokan
git clone https://github.com/aykhuss/dokan.git

#ensure correct path to python and lhapdf
source .bashrc_nnlojet

#Copy the lines below in case of just updating of dokan only
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j8
make install
#Copy the lines above in case of just updating of dokan only

source .bashrc_nnlojet