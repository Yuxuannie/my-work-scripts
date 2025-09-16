 
# Source the configuration file
source config.tcl
 
# Procedure to extract the official library name from the .lib file
proc extract_official_lib_name {lib_file} {
    set official_name ""
    set f [open $lib_file r]
    while {[gets $f line] != -1} {
        if {[regexp {^\s*library\s*\((.*?)\)} $line -> name]} {
            set official_name [string trim $name "\""]
            break
        }
    }
    close $f
    return $official_name
}
 
# Process each library
foreach lib_name $lib_list {
    set base_name [file rootname $lib_name]
    set full_lib_path [file join $lib_path $lib_name]
   
    puts "####################################################################################"
    puts "\nProcessing library file: $full_lib_path"
    puts "Base name: $base_name"
   
    # Extract the official library name
    set official_lib_name [extract_official_lib_name $full_lib_path]
   
    if {$official_lib_name eq ""} {
        puts "Error: Could not extract official library name from $full_lib_path"
        continue
    }
   
    puts "Official library name: $official_lib_name"
   
    # Check if library-specific settings file exists and source it if it does
    if {[file exists ${base_name}_settings.tcl]} {
        source ${base_name}_settings.tcl
    }
   
    # Process the lib
 
    set_host_options -max_cores 8
    set lc_ccsn_max_steps 2500000
 
    # Read the library
 
    puts "Reading library..."
    if {[catch {read_lib $full_lib_path > ${base_name}_read.log} errorMsg]} {
        puts "Error reading library: $errorMsg"
        exit
    }
 
    puts "Writing library to DB format..."
    if {[catch {write_lib $official_lib_name -format db -output $base_name.db} errorMsg]} {
        puts "Error writing library to DB: $errorMsg"
        exit
    }
 
 
    puts "Processing complete for $lib_name. Output: ${base_name}.db"
}
 
puts "\nAll libraries processed."
 
