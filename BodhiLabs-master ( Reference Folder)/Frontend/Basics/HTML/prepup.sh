#!/bin/bash

# Check if at least one argument (lab name) is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <Lab Name> [--no-cleanup | -nc]"
    exit 1
fi

lab=$1
fullLab="Table"
studentDirectory="$lab/studentDirectory"
cleanup=true

# Check for optional second argument for disabling cleanup
if [ "$2" == "--no-cleanup" ] || [ "$2" == "-nc" ]; then
    cleanup=false
fi

# Step 1: Copy the user's lab to .evaluationScripts (excluding node_modules and .solutions)
rsync -a \
    --exclude="node_modules" \
    --exclude=".solutions" \
    "$lab/" ".evaluationScripts/"

# Step 2: Copy only files from Table that are NOT in $lab, but skip studentDirectory if present in both
student_subdir="studentDirectory"
exclude_student_dir=""

if [ -d "$lab/$student_subdir" ] && [ -d "$fullLab/$student_subdir" ]; then
    exclude_student_dir="--exclude=$student_subdir"
fi

rsync -a \
    --exclude="node_modules" \
    --exclude=".solutions" \
    $exclude_student_dir \
    --ignore-existing \
    "$fullLab/" ".evaluationScripts/"

# Step 3: Create instructor archive
tar -czvf instructor.tgz .evaluationScripts

# Step 4: Copy studentDirectory to labDirectory
rsync -a --exclude="node_modules" "$studentDirectory/" "labDirectory/"

# Step 5: Create student archive
tar -czvf student.tgz labDirectory

# Step 6: Clean up unless cleanup is disabled
if [ "$cleanup" = true ]; then
    rm -rf .evaluationScripts labDirectory
else
    echo "Cleanup disabled. Skipping removal of temporary directories."
fi
