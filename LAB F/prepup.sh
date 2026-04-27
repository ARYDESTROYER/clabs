#!/bin/bash
# LAB F prepup -- build per-activity tarballs ready for BodhiLabs upload.
#
# Run from the LAB F root:
#   bash prepup.sh           # all activities
#   bash prepup.sh 2         # just Activity 2
#
# Produces inside each activity folder:
#   client_evaluation.tgz   (the .evaluationScripts archive)
#   student_directory.tgz   (the labDirectory archive)

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=(1 2 3)

OS="$(uname -s)"

clean_apple_metadata() {
    local dir="$1"
    [ -d "$dir" ] || return 0
    find "$dir" \( -name '._*' -o -name '.DS_Store' \) -type f -delete 2>/dev/null || true
    find "$dir" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    if [ "$OS" = "Darwin" ] && command -v xattr >/dev/null 2>&1; then
        xattr -cr "$dir" 2>/dev/null || true
    fi
}

pack() {
    local activity="$1"
    local dir="$ROOT/Activity $activity"
    if [ ! -d "$dir" ]; then
        echo "[!] Skipping Activity $activity -- folder not found." >&2
        return
    fi
    echo "==> Activity $activity"
    clean_apple_metadata "$dir/.evaluationScripts"
    clean_apple_metadata "$dir/labDirectory"

    cd "$dir" || return

    rm -f client_evaluation.tgz student_directory.tgz

    if [ "$OS" = "Darwin" ]; then
        COPYFILE_DISABLE=1 tar --no-mac-metadata -czf client_evaluation.tgz .evaluationScripts
        COPYFILE_DISABLE=1 tar --no-mac-metadata -czf student_directory.tgz labDirectory
    else
        tar -czf client_evaluation.tgz .evaluationScripts
        tar -czf student_directory.tgz labDirectory
    fi

    echo "    client_evaluation.tgz  $(du -h client_evaluation.tgz | cut -f1)"
    echo "    student_directory.tgz  $(du -h student_directory.tgz | cut -f1)"

    if tar -tzf client_evaluation.tgz | grep -qE '(^|/)\._|(^|/)\.DS_Store'; then
        echo "    [!] WARNING: AppleDouble metadata leaked into client_evaluation.tgz" >&2
    fi

    cd "$ROOT" || return
}

for a in "${TARGETS[@]}"; do
    pack "$a"
done

echo
echo "Done. Upload each Activity's two .tgz files in the BodhiLabs Container C section."
echo "Mount path for both archives: /home"
echo "Evaluate script path: /home/.evaluationScripts/evaluate.sh"
