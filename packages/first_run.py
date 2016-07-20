
import os
from shutil import copyfile, copytree
import traceback


def files_copy(mypath, success):
    """
    Copy input .dat files to root folder.
    """
    print("- Copy input .dat files to the root folder.\n")
    # Check if the input .dat files already exist.
    for i_f in ['params', 'semi']:
        i_f_path = mypath + i_f + '_input.dat'
        o_f_path = mypath + i_f + '_input_OLD.dat'
        n_f_path = mypath + 'packages/defvals/' + i_f + '_input.dat'
        # First, check if the file exists in packages/
        if os.path.isfile(n_f_path):
            # Now check if it exists in the root folder.
            if os.path.isfile(i_f_path):
                # File exist in root folder. Rename it.
                print("File {} already present in root folder.".format(
                    i_f + '_input.dat'))
                print("Rename to {}".format(i_f + '_input_OLD.dat'))
                os.rename(i_f_path, o_f_path)
            # Copy into root folder.
            print("Copy {} to root folder.\n".format(i_f + '_input.dat'))
            copyfile(n_f_path, i_f_path)
            success += 1
        else:
            print("WARNING: file {}\nis not present.\n".format(n_f_path))

    return success


def folder_copy(mypath, success):
    """
    Copy data folders to root folder.
    """
    print("- Copy data folders to the root folder.\n")
    for i_fo in ['isochrones', 'input']:
        i_fo_path = mypath + i_fo + '/'
        o_fo_path = mypath + i_fo + '_OLD/'
        n_fo_path = mypath + 'packages/defvals/' + i_fo + '/'
        # First, check if the folder exists in packages/
        if os.path.isdir(n_fo_path):
            # Now, check if the folder exists in the root.
            if os.path.isdir(i_fo_path):
                print("Folder {}/ already present in root folder.".format(
                    i_fo))
                print("Rename to {}".format(i_fo + '_OLD/'))
                os.rename(i_fo_path, o_fo_path)
            # Copy into root folder.
            print("Copy {}/ to root folder.\n".format(i_fo))
            copytree(n_fo_path, i_fo_path)
            success += 1
        else:
            print("WARNING: folder {}\nis not present.\n".format(n_fo_path))

    return success


def check_1strun(mypath):
    """
    Check if this is the first run of the code or not. If it is, attempt to
    copy input .dat files from packages/ folder into root folder.
    """

    try:
        fr_file = mypath + 'packages/.first_run'
        if os.path.isfile(fr_file):

            success = 0
            with open(fr_file) as f:
                N = str(f.read())
                if N == '0':
                    print("* First run of the code detected *\n")
                    success = files_copy(mypath, success)
                    success = folder_copy(mypath, success)

                elif N in ['1', '2', '3']:
                    print("First run copy process was left incomplete. Check\n"
                          "that all necessary folders and input files are\n"
                          "present in the root folder.\n")

            # After both input .dat files, and both the isochrones/ and input/
            # folders could be copied to the root folder, change the
            # .first_run file so this won't be done again.
            if success == 4:
                with open(fr_file, 'w') as fw:
                    fw.write("4")
        else:
            print("ERROR: No 'packages/.first_run' file present.\n")
    except:
        print("ERROR: Could not check/copy input .dat files\n"
              "to root folder.\n")
        print(traceback.format_exc())