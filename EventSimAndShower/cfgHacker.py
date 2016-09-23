import sys
import os

########################################
# Main
########################################

def main():

    # Lines to be inserted in cfg
    insertion = [
        " \n",
        "# THIS PART WAS AUTOMATICALLY INSERTED \n"
        "from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper \n",
        "randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService) \n",
        "randSvc.populate() \n",
        " \n",
        " \n",
        ]

    cfg_file = sys.argv[1]

    # Read unedited cfg file
    with open( cfg_file, 'r' ) as cfg_fp:
        cfg_lines = cfg_fp.readlines()

    # Find the insertion point
    for i_line, line in enumerate(cfg_lines):
        if "# Input source" in line:
            insert_line = i_line
            break

    # Do the insertion
    edited_cfg_lines = cfg_lines[:insert_line] + insertion + cfg_lines[insert_line:]
    edited_cfg_text = ''.join(edited_cfg_lines)

    # Save the changes
    with open( cfg_file, 'w' ) as cfg_fp:
        cfg_fp.write( edited_cfg_text )


#######################################
# End of Main
########################################
if __name__ == "__main__":
    main()