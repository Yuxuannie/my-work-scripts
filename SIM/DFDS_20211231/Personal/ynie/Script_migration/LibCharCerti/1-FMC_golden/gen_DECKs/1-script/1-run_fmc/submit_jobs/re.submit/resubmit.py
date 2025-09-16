import subprocess
import time
import os
import argparse
 
def check_stop_condition(resubmit_path):
    result = subprocess.run(
        f"grep -l 'No valid spice folders found' {resubmit_path}/*.log",
        shell=True,
        capture_output=True,
        text=True
    )
    return bool(result.stdout)
 
def main(working_path, resubmit_path, corners):
    with open('resubmit.log', 'w') as log_file:
        while True:
            #log_file.write("Waiting for 1 hour...\n")
            log_file.flush()
            time.sleep(6)  # Wait for 1 hour
 
            # Run gen_submission.csh with arguments
            for corner in corners:
                log_file.write(f"Running gen_submission.csh for {corner}\n")
                log_file.flush()
                subprocess.run(
                    f"csh {resubmit_path}/gen_submission.csh {corner} {working_path}",
                    shell=True
                )
 
            # Check for stopping condition
            if check_stop_condition(resubmit_path):
                log_file.write("Stopping loop due to condition met.\n")
                log_file.flush()
                break
 
            for corner in corners:
                script_file = os.path.join(resubmit_path, f"submit_all_jobs_hold_{corner}.sh")
                if os.path.exists(script_file):
                    log_file.write(f"Sourcing {script_file}\n")
                    log_file.flush()
                    subprocess.run(f"/bin/csh {script_file}", shell=True)
                else:
                    log_file.write(f"Script {script_file} not found.\n")
                    log_file.flush()
 
            log_file.write("Waiting for 2 hours...\n")
            log_file.flush()
            time.sleep(7200)  # Wait for 2 hours
 
            if check_stop_condition(resubmit_path):
                log_file.write("Stopping loop due to condition met.\n")
                log_file.flush()
                break
 
        log_file.write("Script completed.\n")
        log_file.flush()
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process job submission.')
    parser.add_argument('--working_path', type=str, required=True, help='The working path')
    parser.add_argument('--resubmit_path', type=str, required=True, help='The resubmit path')
    parser.add_argument('--corners', type=str, nargs='+', required=True, help='List of corners')
 
    args = parser.parse_args()
    main(args.working_path, args.resubmit_path, args.corners)
 
