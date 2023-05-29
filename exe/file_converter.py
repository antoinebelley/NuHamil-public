#!/usr/bin/env python
#-*- coding:utf-8 -*-
# script to submit the job
# execute ./NuHamil.py $machinename
# $machinename is optional argument. If $machinename is not given, job will be submitted as interactive.
import os
import sys
import subprocess
from collections import OrderedDict
exe = 'NuHamil.exe'
account="rrg-holt"     # for cedar
account="rrg-navratil" # for cedar

def set_input(params):
    # basic parameters

    params["file_convert"] = True
    # NN file
    params['rank'] = 2
    params['emax'] = 14
    params['e2max'] = 28
    params["file_name_nn_original"]= '../mod_engel.op.gz'
    params["file_name_nn_converted"]="test.snt"

    # NNN file
    #params["file_convert"] = True
    #params['only_no2b_elements'] = True
    ##params['only_hf_monopole'] = True
    #params['rank'] = 3
    #params['emax'] = 6
    #params['e2max'] = 6
    #params['e3max'] = 6
    #params["file_name_3n_original"]="NO2B_ThBME_srg2.0_ramp6_N4LO_EMN500_c1_-0.73_c3_-3.38_c4_1.69_cD_-1.8_cE_-0.31_LNL2_650_500_IS_hw30_ms6_6_6.stream.bin"
    #params["file_name_3n_converted"]="NO2B_ThBME_srg2.0_ramp6_N4LO_EMN500_c1_-0.73_c3_-3.38_c4_1.69_cD_-1.8_cE_-0.31_LNL2_650_500_IS_hw30_ms6_6_6.me3j"

def gen_script(params, batch, machine):
    try:
        if( "file_name_nn_original" in params ): fbase = "Converter_A" + str(params["rank"]) + "_" + os.path.splitext(os.path.basename(params["file_name_nn_original"]))[0]
        if( "file_name_3n_original" in params ): fbase = "Converter_A" + str(params["rank"]) + "_" + os.path.splitext(os.path.basename(params["file_name_3n_original"]))[0]
    except:
        fbase = "Converter"
    file_input = "Input_" + fbase + ".dat"
    file_log   = "log_" + fbase + ".dat"
    fsh = "run_" + fbase + ".sh"
    prt = ""
    if(machine=="oak"):
        prt += "#!/bin/bash \n"
        prt += "#PBS -q oak \n"
        prt += "#PBS -l mem=128gb,nodes=1:ppn=32,walltime=072:00:00 \n"
        prt += "cd $PBS_O_WORKDIR\n"
    if(machine=="cedar"):
        header = "#!/bin/bash\n"
        header += "#SBATCH --account="+account+"\n"
        header += "#SBATCH --nodes=1\n"
        header += "#SBATCH --ntasks=1\n"
        header += "#SBATCH --cpus-per-task=1\n"
        header += "#SBATCH --mem=125G\n"
        header += "#SBATCH --time=3-00:00\n\n"

    prt += 'echo "run ' +fsh + '..."\n'
    prt += "cat > "+file_input + " <<EOF\n"
    prt += "&input\n"
    for key, value in params.items():
        if(isinstance(value, str)):
            prt += str(key) + '= "' + str(value) + '" \n'
            continue
        if(isinstance(value, list)):
            prt += str(key) + "= "
            for x in value[:-1]:
                prt += str(x) + ", "
            prt += str(value[-1]) + "\n"
            continue
        prt += str(key) + '=' + str(value) + '\n'
    prt += "&end\n"
    prt += "EOF\n"
    if(batch):
        prt += exe + " " + file_input + " > " + file_log + " 2>&1\n"
        prt += "rm " + file_input + "\n"
    if(not batch):
        prt += exe + " " + file_input + "\n"
        prt += "rm " + file_input + "\n"
    f = open(fsh, "w")
    f.write(prt)
    f.close()
    os.chmod(fsh, 0o755)
    return fsh

def main(machinename=None):
    if(machinename==None):
        batch = False
        machine = 'local'
    if(machinename!=None):
        batch=True
        if(machinename.lower() == "local"):
            machine = 'local'
        if(machinename.lower() == "oak"):
            machine = "oak"
        if(machinename.lower() =="cedar"):
            machine = "cedar"

    params = OrderedDict()
    set_input(params)
    fsh = gen_script(params, batch, machine)
    if(machine == 'local'):
        cmd = "./" + fsh
    if(machine=="oak"):
        cmd = "qsub " + fsh
    if(machine=="cedar"):
        cmd = "srun " + fsh
    subprocess.call(cmd,shell=True)

if(__name__ == "__main__"):
    if(len(sys.argv) == 1):
        main()
    if(len(sys.argv) > 1):
        main(sys.argv[1])

