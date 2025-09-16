# Collateral Generation - Quick Guide
 
## What This Does
Takes SCLD collaterals and creates delivery packages for EDA vendors with proper voltage modifications and SNPS translation.
 
## Quick Start
```bash
chmod +x gen_collaterals.sh
./gen_collaterals.sh
```
 
## Setup Required
```
working_dir/0-from_SCLD/
â”œâ”€â”€ Netlist/     (ready to use)
â”œâ”€â”€ Template/    (ready to use) 
â”œâ”€â”€ Model/       (ready to use, optional)
â””â”€â”€ Char/        (contains reference corner files)
```
 
## Configuration
Edit `gen_collaterals.sh`:
```bash
working_dir="/your/path/here"
eda_vendor="CDNS"  # Always starts with CDNS
corners=("corner1" "corner2" "corner3")
lpe_type="cworst_CCworst_T"
```
 
## What You Get
 
### CDNS Only:
```
working_dir/1-for_CDNS/
â”œâ”€â”€ Netlist/     (copied from SCLD)
â”œâ”€â”€ Template/    (copied from SCLD)
â”œâ”€â”€ Model/       (copied from SCLD, if available)
â””â”€â”€ Char/
    â”œâ”€â”€ corner1/ (6 files with voltage replaced)
    â”œâ”€â”€ corner2/ (6 files with voltage replaced)
    â””â”€â”€ corner3/ (6 files with voltage replaced)
```
 
### CDNS + SNPS (if selected):
```
working_dir/
â”œâ”€â”€ 1-for_CDNS/  (as above + Template_sis/ preserved)
â””â”€â”€ 2-for_SNPS/
    â”œâ”€â”€ Netlist/ (copied from SCLD)
    â”œâ”€â”€ Model/   (copied from SCLD, if available)
    â”œâ”€â”€ Template/
    â”‚   â”œâ”€â”€ corner1/ (.sis and .slew_all files)
    â”‚   â”œâ”€â”€ corner2/ (.sis and .slew_all files)
    â”‚   â””â”€â”€ corner3/ (.sis and .slew_all files)
    â”œâ”€â”€ Char/
    â”‚   â”œâ”€â”€ corner1/ (.inc files only)
    â”‚   â”œâ”€â”€ corner2/ (.inc files only)
    â”‚   â””â”€â”€ corner3/ (.inc files only)
    â””â”€â”€ seed.lib (node-specific library for SNPS)
```
 
## Key Features
- **Auto-detects** reference corner from SCLD files
- **Replaces voltages**: `0p54v` â†’ `0p450v` and `0.54` â†’ `0.450`
- **SNPS translation**: Converts CDNS templates to SNPS .sis and .slew_all formats
- **File filtering**: SNPS gets only .inc files in Char (no .tcl files)
- **Interactive selection**: Choose CDNS only or CDNS + SNPS
- **Tar option**: Create delivery archives automatically
- **Template_sis preserved**: Translation folder kept intact in CDNS
- **Creates logs** in `working_dir/logs/`
- **Generates summaries** for both vendors
 
## Common Changes
 
### Different EDA Vendor (Always starts with CDNS)
```bash
# CDNS is always processed first
# SNPS is optional and selected interactively
```
 
### Different Corners
```bash
corners=("new_corner1" "new_corner2")  # Update array
```
 
### Different Working Directory
```bash
working_dir="/new/path"  # Update path
```
 
## SNPS Requirements
- **CDNS must be generated first** (SNPS translates from CDNS)
- **Translation scripts needed**:
  - `SNPS_translate/template_translator.sh`
  - `SNPS_translate/seed.lib`
- **Important**: seed.lib is node-specific
  - Confirm with Jia-wei (SCLD) before using
  - Wrong seed.lib will cause characterization errors
 
## SNPS File Filtering
- **Template**: Translated .sis and .slew_all files (separated by corner)
- **Char**: Only .inc files copied (no .tcl files for SNPS)
- **Netlist/Model**: Copied from SCLD same as CDNS
- **seed.lib**: Copied to SNPS delivery root (same level as folders)
- **Template_sis**: Preserved in CDNS folder (not cleaned up)
 
## Troubleshooting
 
| Problem | Solution |
|---------|----------|
| "SCLD directory not found" | Check `0-from_SCLD` folder exists |
| "No corner patterns found" | Check SCLD Char files have proper names |
| "Python script not found" | Update `python_script` path |
| "SNPS translator not found" | Check `SNPS_translate/` folder exists |
| "Translation script failed" | Check perl scripts and dependencies |
| Missing files | Check SCLD delivery, request missing files |
 
## Files Generated
 
### CDNS (per corner):
- **6 files per corner**: 2 tcl files + 4 inc files
- **Model folder**: If available in SCLD
- **Template_sis folder**: Created and preserved during SNPS translation
- **Summary report**: Details all changes made
- **Log files**: For debugging issues
 
### SNPS (per corner, if selected):
- **Template corner folders**: .sis and .slew_all files (translated from CDNS)
- **Char corner folders**: .inc files only (no .tcl files)
- **Model folder**: Same as CDNS
- **seed.lib**: Node-specific library at delivery root
- **SNPS summary report**: Translation details
- **Log files**: For debugging translation
 
## Next Step
Deliver the `1-for_CDNS` and/or `2-for_SNPS` folders to EDA vendors for characterization.# Collateral Generation - Quick Guide
 
## What This Does
Takes SCLD collaterals and creates delivery packages for EDA vendors with proper voltage modifications and SNPS translation.
 
## Quick Start
```bash
chmod +x gen_collaterals.sh
./gen_collaterals.sh
```
 
## Setup Required
```
working_dir/0-from_SCLD/
â”œâ”€â”€ Netlist/     (ready to use)
â”œâ”€â”€ Template/    (ready to use) 
â”œâ”€â”€ Model/       (ready to use, optional)
â””â”€â”€ Char/        (contains reference corner files)
```
 
## Configuration
Edit `gen_collaterals.sh`:
```bash
working_dir="/your/path/here"
eda_vendor="CDNS"  # Always starts with CDNS
corners=("corner1" "corner2" "corner3")
lpe_type="cworst_CCworst_T"
```
 
## What You Get
 
### CDNS Only:
```
working_dir/1-for_CDNS/
â”œâ”€â”€ Netlist/     (copied from SCLD)
â”œâ”€â”€ Template/    (copied from SCLD)
â”œâ”€â”€ Model/       (copied from SCLD, if available)
â””â”€â”€ Char/
    â”œâ”€â”€ corner1/ (6 files with voltage replaced)
    â”œâ”€â”€ corner2/ (6 files with voltage replaced)
    â””â”€â”€ corner3/ (6 files with voltage replaced)
```
 
### CDNS + SNPS (if selected):
```
working_dir/
â”œâ”€â”€ 1-for_CDNS/  (as above + Template_sis/ preserved)
â””â”€â”€ 2-for_SNPS/
    â”œâ”€â”€ Netlist/ (copied from SCLD)
    â”œâ”€â”€ Model/   (copied from SCLD, if available)
    â”œâ”€â”€ Template/
    â”‚   â”œâ”€â”€ corner1/ (.sis and .slew_all files)
    â”‚   â”œâ”€â”€ corner2/ (.sis and .slew_all files)
    â”‚   â””â”€â”€ corner3/ (.sis and .slew_all files)
    â”œâ”€â”€ Char/
    â”‚   â”œâ”€â”€ corner1/ (.inc files only)
    â”‚   â”œâ”€â”€ corner2/ (.inc files only)
    â”‚   â””â”€â”€ corner3/ (.inc files only)
    â””â”€â”€ seed.lib (node-specific library for SNPS)
```
 
## Key Features
- **Auto-detects** reference corner from SCLD files
- **Replaces voltages**: `0p54v` â†’ `0p450v` and `0.54` â†’ `0.450`
- **SNPS translation**: Converts CDNS templates to SNPS .sis and .slew_all formats
- **File filtering**: SNPS gets only .inc files in Char (no .tcl files)
- **Interactive selection**: Choose CDNS only or CDNS + SNPS
- **Tar option**: Create delivery archives automatically
- **Template_sis preserved**: Translation folder kept intact in CDNS
- **Creates logs** in `working_dir/logs/`
- **Generates summaries** for both vendors
 
## Common Changes
 
### Different EDA Vendor (Always starts with CDNS)
```bash
# CDNS is always processed first
# SNPS is optional and selected interactively
```
 
### Different Corners
```bash
corners=("new_corner1" "new_corner2")  # Update array
```
 
### Different Working Directory
```bash
working_dir="/new/path"  # Update path
```
 
## SNPS Requirements
- **CDNS must be generated first** (SNPS translates from CDNS)
- **Translation scripts needed**:
  - `SNPS_translate/template_translator.sh`
  - `SNPS_translate/seed.lib`
- **Important**: seed.lib is node-specific
  - Confirm with Jia-wei (SCLD) before using
  - Wrong seed.lib will cause characterization errors
 
## SNPS File Filtering
- **Template**: Translated .sis and .slew_all files (separated by corner)
- **Char**: Only .inc files copied (no .tcl files for SNPS)
- **Netlist/Model**: Copied from SCLD same as CDNS
- **seed.lib**: Copied to SNPS delivery root (same level as folders)
- **Template_sis**: Preserved in CDNS folder (not cleaned up)
 
## Troubleshooting
 
| Problem | Solution |
|---------|----------|
| "SCLD directory not found" | Check `0-from_SCLD` folder exists |
| "No corner patterns found" | Check SCLD Char files have proper names |
| "Python script not found" | Update `python_script` path |
| "SNPS translator not found" | Check `SNPS_translate/` folder exists |
| "Translation script failed" | Check perl scripts and dependencies |
| Missing files | Check SCLD delivery, request missing files |
 
## Files Generated
 
### CDNS (per corner):
- **6 files per corner**: 2 tcl files + 4 inc files
- **Model folder**: If available in SCLD
- **Template_sis folder**: Created and preserved during SNPS translation
- **Summary report**: Details all changes made
- **Log files**: For debugging issues
 
### SNPS (per corner, if selected):
- **Template corner folders**: .sis and .slew_all files (translated from CDNS)
- **Char corner folders**: .inc files only (no .tcl files)
- **Model folder**: Same as CDNS
- **seed.lib**: Node-specific library at delivery root
- **SNPS summary report**: Translation details
- **Log files**: For debugging translation
 
## Next Step
Deliver the `1-for_CDNS` and/or `2-for_SNPS` folders to EDA vendors for characterization.
 
