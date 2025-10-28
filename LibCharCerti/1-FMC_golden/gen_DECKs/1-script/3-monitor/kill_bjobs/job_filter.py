#!/usr/bin/env python3
 
import subprocess
import sys
import argparse
import re
import fnmatch
from datetime import datetime, timedelta
 
def get_bjobs_output():
    """Get bjobs output"""
    try:
        result = subprocess.run(['bjobs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""
    except FileNotFoundError:
        print("Error: bjobs command not found", file=sys.stderr)
        sys.exit(1)
 
def get_bjobs_detailed(jobid):
    """Get detailed bjobs -l output for a specific job"""
    try:
        result = subprocess.run(['bjobs', '-l', str(jobid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""
 
def parse_bjobs(output):
    """Parse bjobs output into job dictionaries"""
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return []
   
    # Parse header to find column positions
    header = lines[0]
    positions = {}
   
    # Find column positions
    for field in ['JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME']:
        pos = header.find(field)
        if pos >= 0:
            positions[field] = pos
   
    print("Debug - Header: " + header, file=sys.stderr)
    print("Debug - Column positions: " + str(positions), file=sys.stderr)
   
    jobs = []
    for line in lines[1:]:
        if not line.strip():
            continue
           
        job = {}
        try:
            # Extract basic fields
            if 'JOBID' in positions:
                end_pos = positions.get('USER', positions['JOBID'] + 10)
                job['JOBID'] = line[positions['JOBID']:end_pos].strip()
           
            if 'USER' in positions:
                end_pos = positions.get('STAT', positions['USER'] + 10)
                job['USER'] = line[positions['USER']:end_pos].strip()
           
            if 'STAT' in positions:
                end_pos = positions.get('QUEUE', positions['STAT'] + 6)
                job['STAT'] = line[positions['STAT']:end_pos].strip()
           
            if 'QUEUE' in positions:
                end_pos = positions.get('FROM_HOST', positions['QUEUE'] + 12)
                job['QUEUE'] = line[positions['QUEUE']:end_pos].strip()
           
            if 'FROM_HOST' in positions:
                end_pos = positions.get('EXEC_HOST', positions['FROM_HOST'] + 15)
                job['FROM_HOST'] = line[positions['FROM_HOST']:end_pos].strip()
           
            if 'EXEC_HOST' in positions:
                end_pos = positions.get('JOB_NAME', positions['EXEC_HOST'] + 15)
                job['EXEC_HOST'] = line[positions['EXEC_HOST']:end_pos].strip()
           
            # Handle JOB_NAME and SUBMIT_TIME
            if 'JOB_NAME' in positions:
                if 'SUBMIT_TIME' in positions:
                    # Separate SUBMIT_TIME column exists
                    job['JOB_NAME'] = line[positions['JOB_NAME']:positions['SUBMIT_TIME']].strip()
                    job['SUBMIT_TIME'] = line[positions['SUBMIT_TIME']:].strip()
                else:
                    # SUBMIT_TIME is embedded in JOB_NAME field
                    full_info = line[positions['JOB_NAME']:].strip()
                   
                    # Look for time pattern at the end: "Jul  3 04:17"
                    time_pattern = r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2})\s*$'
                    match = re.search(time_pattern, full_info)
                   
                    if match:
                        job['SUBMIT_TIME'] = match.group(1)
                        job['JOB_NAME'] = full_info[:match.start()].strip()
                    else:
                        job['JOB_NAME'] = full_info
                        job['SUBMIT_TIME'] = ''
            else:
                job['JOB_NAME'] = ''
                job['SUBMIT_TIME'] = ''
           
            # Debug output
            jobid_str = job.get('JOBID', 'UNKNOWN')
            submit_time_str = job.get('SUBMIT_TIME', '')
            job_name_str = job.get('JOB_NAME', '')
            if len(job_name_str) > 30:
                job_name_str = job_name_str[:30] + "..."
           
            print("Debug - Job " + jobid_str + ": SUBMIT_TIME='" + submit_time_str + "', JOB_NAME='" + job_name_str + "'", file=sys.stderr)
           
            # Only add jobs with valid JOBID
            if job.get('JOBID', '').isdigit():
                jobs.append(job)
               
        except Exception as e:
            print("Debug - Failed to parse line: " + str(e), file=sys.stderr)
            continue
   
    return jobs
 
def parse_submit_time(submit_time_str):
    """Parse bjobs SUBMIT_TIME format like 'Jul  3 04:17' to datetime"""
    if not submit_time_str or submit_time_str.strip() == '':
        return None
   
    try:
        # Normalize spaces - convert multiple spaces to single space
        submit_time_str = re.sub(r'\s+', ' ', submit_time_str.strip())
       
        # Get current year
        current_year = datetime.now().year
       
        # Try different formats
        formats = [
            "%b %d %H:%M",   # Jul 3 04:17
            "%B %d %H:%M",   # July 3 04:17
            "%m/%d %H:%M",   # 7/3 04:17
        ]
       
        for fmt in formats:
            try:
                dt = datetime.strptime(submit_time_str, fmt)
                dt = dt.replace(year=current_year)
               
                # If date is far in future, it's probably from last year
                if dt > datetime.now() + timedelta(days=30):
                    dt = dt.replace(year=current_year - 1)
               
                return dt
            except ValueError:
                continue
       
        return None
       
    except Exception:
        return None
 
def parse_date_input(date_str):
    """Parse user input date formats"""
    if not date_str:
        return None
   
    try:
        current_year = datetime.now().year
        date_str = date_str.strip()
       
        formats = [
            "%Y-%m-%d",      # 2025-07-05
            "%m/%d/%Y",      # 07/05/2025
            "%m/%d",         # 07/05
            "%b %d",         # Jul 5
            "%B %d",         # July 5
            "%b %d %Y",      # Jul 5 2025
            "%B %d %Y",      # July 5 2025
        ]
       
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.year == 1900:
                    dt = dt.replace(year=current_year)
                return dt
            except ValueError:
                continue
       
        return None
    except Exception:
        return None
 
def matches_pattern(text, pattern):
    """Check if text matches pattern"""
    text = text.lower()
    pattern = pattern.lower()
   
    if '*' in pattern or '?' in pattern or '[' in pattern:
        return fnmatch.fnmatch(text, pattern)
    else:
        return pattern in text
 
def extract_job_details(detailed_output):
    """Extract key information from bjobs -l output"""
    if not detailed_output:
        return ""
   
    details = []
    lines = detailed_output.strip().split('\n')
   
    for line in lines:
        line = line.strip()
        if not line:
            continue
           
        if line.startswith('Job <') or line.startswith('---') or line.startswith('User '):
            continue
           
        keywords = ['job name', 'command', 'cwd', 'output', 'error', 'project',
                   'queue', 'execution', 'submitted', 'resource', 'working directory']
       
        if any(keyword in line.lower() for keyword in keywords):
            details.append(line)
        elif len(line) > 5 and not line.startswith(' ') and '=' not in line[:10]:
            details.append(line)
   
    return ' '.join(details)
 
def filter_jobs_standard(jobs, field, include_list, exclude_list, before_date=None, after_date=None):
    """Filter jobs based on standard bjobs output"""
    filtered = []
   
    for job in jobs:
        # Time-based filtering first
        if before_date or after_date:
            submit_time = parse_submit_time(job.get('SUBMIT_TIME', ''))
            print("Debug - Job " + job.get('JOBID', '') + " submit_time: " + str(submit_time) + " (before=" + str(before_date) + ")", file=sys.stderr)
           
            if submit_time:
                if before_date and submit_time >= before_date:
                    continue
                if after_date and submit_time <= after_date:
                    continue
            elif before_date or after_date:
                continue
       
        # Pattern-based filtering
        field_value = job.get(field, '')
       
        include_match = True
        if include_list:
            for inc in include_list:
                if not matches_pattern(field_value, inc):
                    include_match = False
                    break
       
        exclude_match = False
        if exclude_list:
            for exc in exclude_list:
                if matches_pattern(field_value, exc):
                    exclude_match = True
                    break
       
        if include_match and not exclude_match:
            filtered.append(job['JOBID'])
   
    return filtered
 
def filter_jobs_detailed(jobs, include_list, exclude_list, before_date=None, after_date=None):
    """Filter jobs based on detailed bjobs -l output"""
    filtered = []
    total_jobs = len(jobs)
   
    for i, job in enumerate(jobs):
        jobid = job['JOBID']
       
        if total_jobs > 10:
            progress_msg = "\rProcessing job " + str(i+1) + "/" + str(total_jobs) + "..."
            print(progress_msg, end='', file=sys.stderr)
       
        # Time-based filtering first
        if before_date or after_date:
            submit_time = parse_submit_time(job.get('SUBMIT_TIME', ''))
            if submit_time:
                if before_date and submit_time >= before_date:
                    continue
                if after_date and submit_time <= after_date:
                    continue
            elif before_date or after_date:
                continue
       
        # Get detailed information
        detailed_output = get_bjobs_detailed(jobid)
        if not detailed_output:
            continue
           
        job_details = extract_job_details(detailed_output)
        standard_info = job.get('JOB_NAME', '') + ' ' + job.get('QUEUE', '') + ' ' + job.get('USER', '') + ' ' + job.get('EXEC_HOST', '')
        full_content = job_details + ' ' + standard_info
       
        include_match = True
        if include_list:
            for inc in include_list:
                if not matches_pattern(full_content, inc):
                    include_match = False
                    break
       
        exclude_match = False
        if exclude_list:
            for exc in exclude_list:
                if matches_pattern(full_content, exc):
                    exclude_match = True
                    break
       
        if include_match and not exclude_match:
            filtered.append(jobid)
   
    if total_jobs > 10:
        print("\r" + " " * 50 + "\r", end='', file=sys.stderr)
   
    return filtered
 
def main():
    parser = argparse.ArgumentParser(description='Filter LSF jobs')
    parser.add_argument('--field', default='JOB_NAME', help='Field to filter on')
    parser.add_argument('--include', default='', help='Comma-separated include strings')
    parser.add_argument('--exclude', default='', help='Comma-separated exclude strings')
    parser.add_argument('--detailed', action='store_true', help='Use detailed bjobs -l search')
    parser.add_argument('--before', help='Jobs submitted before this date')
    parser.add_argument('--after', help='Jobs submitted after this date')
    parser.add_argument('--output', required=True, help='Output file for job IDs')
   
    args = parser.parse_args()
   
    # Parse include/exclude strings
    include_list = []
    if args.include:
        include_list = [s.strip() for s in args.include.split(',') if s.strip()]
   
    exclude_list = []
    if args.exclude:
        exclude_list = [s.strip() for s in args.exclude.split(',') if s.strip()]
   
    # Parse date inputs
    before_date = None
    after_date = None
   
    if args.before:
        before_date = parse_date_input(args.before)
        if not before_date:
            print("Error: Could not parse 'before' date: " + args.before, file=sys.stderr)
            print("Try formats like: 'Jul 5', 'July 5', '2025-07-05', '07/05'", file=sys.stderr)
            sys.exit(1)
        print("Debug - Parsed before_date: " + str(before_date), file=sys.stderr)
   
    if args.after:
        after_date = parse_date_input(args.after)
        if not after_date:
            print("Error: Could not parse 'after' date: " + args.after, file=sys.stderr)
            print("Try formats like: 'Jul 5', 'July 5', '2025-07-05', '07/05'", file=sys.stderr)
            sys.exit(1)
        print("Debug - Parsed after_date: " + str(after_date), file=sys.stderr)
   
    # Get and parse jobs
    output = get_bjobs_output()
    jobs = parse_bjobs(output)
   
    if not jobs:
        print("No jobs found", file=sys.stderr)
        with open(args.output, 'w') as f:
            pass
        return
   
    print("Debug - Found " + str(len(jobs)) + " total jobs", file=sys.stderr)
   
    # Filter jobs
    if args.detailed or args.field == 'DETAILED':
        print("Using detailed search mode for " + str(len(jobs)) + " jobs...", file=sys.stderr)
        filtered_ids = filter_jobs_detailed(jobs, include_list, exclude_list, before_date, after_date)
    else:
        filtered_ids = filter_jobs_standard(jobs, args.field, include_list, exclude_list, before_date, after_date)
   
    # Write results
    with open(args.output, 'w') as f:
        for job_id in filtered_ids:
            f.write(job_id + '\n')
   
    if args.detailed:
        msg = "Detailed search completed. Found " + str(len(filtered_ids)) + " matching jobs."
        print(msg, file=sys.stderr)
    elif before_date or after_date:
        msg = "Time-based filtering completed. Found " + str(len(filtered_ids)) + " matching jobs."
        print(msg, file=sys.stderr)
 
if __name__ == '__main__':
    main()
 
