# Steganography & Forensics Lab

My friend has hidden six fragments in seemingly normal files as a challenge to me! Each fragment is meaningless on its own just a shard of an encoded message. But when you combine the fragments and decode them you will find the true message revealed!

## Challenge Description
A secret message has been split into 6 fragments and hidden across multiple files using various steganography techniques. Each fragment is a piece of an encoded string. You must:

1. Extract all 6 fragments from the provided files
2. Reconstruct the complete base64 string (order matters!)
3. Decode the string using appropriate decoding to reveal the secret message

## Objective
Multiple fragments of an encoded secret are hidden across various files using different steganography and forensics techniques. Extract all fragments, reconstruct the encoded string in the correct order, decode it, and submit the final answer.

## Files Provided
```
document.pdf       - Corporate document
password.jpg       - Hint or password source for another file
firmware.bin       - Binary blob for extraction and strings analysis
logo.png           - PNG steganography target
family_photo.jpg   - Image for metadata or embedded content checks
announcement.wav   - Audio clue file
vacation.jpg       - Image-based stego candidate
```

## Tools Required
- `exiftool` - Metadata analysis
- `binwalk` - Binary analysis and extraction
- `zsteg` - PNG steganography detection
- `steghide` - Steganography extraction
- `sox` - Audio analysis
- `strings` - Binary string extraction

## Getting Started
1. Examine each file type
2. Think about what steganography technique suits each format
3. Record each recovered fragment in `SUBMIT_FLAGS_HERE.txt` (or `SUBMIT_FLAG_HERE.txt` if that is what your LMS editor shows)
4. Combine the fragments in the correct order and decode the final message
5. Put the final decoded flag in the last line of the submission file

## Submission
`SUBMIT_FLAGS_HERE.txt` and `SUBMIT_FLAG_HERE.txt` are created automatically when the lab starts.
Use whichever one your LMS editor allows you to edit. The grader accepts both.
Fragment 4 is the password used to extract another hidden file. Fragment 5 is the extracted fragment value from that step.
Only enter the fragment values and final decoded flag after each label.

