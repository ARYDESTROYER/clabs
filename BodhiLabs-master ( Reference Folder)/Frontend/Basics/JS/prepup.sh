#!/bin/bash

# Check if at least one argument (lab name) is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <Lab Name>"
    exit 1
fi

lab=$1

# Detect OS
OS=$(uname -s)

# Define paths for directories inside $lab
evaluationScripts="$lab/.evaluationScripts"
labDir="$lab/labDirectory"

# Step 1: Remove extended attributes (if running on macOS)
if [ "$OS" = "Darwin" ]; then
    xattr -cr "$evaluationScripts"
    xattr -cr "$labDir"
fi 

# Step 2: Change to the lab directory and create instructor archive, excluding .solutions
cd "$lab" || exit 1
if [ "$OS" = "Darwin" ]; then
    tar --no-mac-metadata --exclude=".solutions" -czvf ../instructor.tgz .evaluationScripts
else
    tar --exclude=".solutions" -czvf ../instructor.tgz .evaluationScripts
fi

# Step 3: Create student archive
if [ "$OS" = "Darwin" ]; then
    tar --no-mac-metadata -czvf ../student.tgz labDirectory
else
    tar -czvf ../student.tgz labDirectory
fi
cd - > /dev/null

# Step 4: OS-specific cleanup (remove any AppleDouble files on macOS)
if [ "$OS" = "Darwin" ]; then
    find "$lab" -name "._*" -delete
    echo "✅ Archives created: instructor.tgz and student.tgz (without macOS resource fork files)"
else
    echo "✅ Archives created: instructor.tgz and student.tgz"
fi
