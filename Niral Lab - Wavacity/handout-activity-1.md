Activity: Multi-Layer Steganography and Forensics Analysis

Objective
Understand how to detect and extract hidden data across a variety of file formats, combining basic forensics techniques with steganography extraction to reconstruct a fragmented secret.

Task
Analyze the provided files to sequentially recover six fragments. Fragment 4 acts as a specialized password required to extract Fragment 5. Once you have gathered all the pieces, combine the relevant base64-encoded fragments in order and decode them to reveal the final flag.

Guidance

Step 1 — Fragment 1: Metadata Exploration
Hidden data often hides in plain sight. Start by analyzing the metadata of the `vacation.jpg` image. Attackers often embed text in image attributes that normal viewers never see.
Use an inspection tool to view the file's metadata:
```bash
exiftool vacation.jpg | grep Comment
```
Look closely for unusual fields like `Comment` or `Description`. You should find your first fragment here.

Step 2 — Fragment 2: Document Inspection
PDFs can hide information within their complex internal structures or simply as unrendered text blocks. 
Analyze the `document.pdf` file. You can either extract its embedded contents or simply search for readable strings within the file:
```bash
binwalk -e document.pdf
```
Alternatively, try a direct string search:
```bash
strings document.pdf | grep Fragment
```

Step 3 — Fragment 3: PNG Steganography
The `logo.png` file is completely lossless, making it a prime candidate for Least Significant Bit (LSB) steganography.
Use a specialized tool designed to detect hidden data in PNG files:
```bash
zsteg logo.png
```
Review the results. Look specifically for payloads appearing in specific color channels, such as `b1,rgb,lsb,xy`. Note down this fragment.

Step 4 — Fragment 4: Audio Forensics (The Password)
Audio files can secretly carry visual data hidden within their acoustic frequencies. Your next target is `announcement.wav`.
This fragment is unique: it contains the **password** you will need for the next step.
To reveal the hidden text, you must view the audio's spectrogram. You have two options:
1. Open local Wavacity at `http://localhost:30000` (served inside the lab, no internet required), import `announcement.wav`, and change the track display to `Spectrogram`.
2. Or, use the `sox` utility in the terminal to generate an image of the spectrogram:
```bash
sox announcement.wav -n spectrogram -o spectrogram.png
```
Inspect the spectrogram visual to discover Fragment 4.

Step 5 — Fragment 5: Password-Protected Extraction
Now that you hold the password (Fragment 4), you can unlock the next layer. 
The image `family_photo.jpg` contains an embedded file protected by a steganography program. You could test the password against various files, but `family_photo.jpg` is the correct host.
Use `steghide` to extract the hidden data:
```bash
steghide extract -sf family_photo.jpg -p <password_from_fragment_4>
```
If successful, this will generate a new text file named `fragment5.txt`. Read its contents to claim Fragment 5:
```bash
cat fragment5.txt
```

Step 6 — Fragment 6: Binary Blob Analysis
Your final target is `firmware.bin`. Binary blobs often contain strings of text left behind during compilation or intentionally packed within the data.
Extract all printable characters and hunt for your final clue:
```bash
strings firmware.bin | grep Fragment
```
(Hint: You can also broaden your search with `strings firmware.bin | grep FLAG`).

Step 7 — Reconstruction and Decoding
You should now possess all 6 fragments. Notice that they consist of characters commonly used in Base64 encoding.
To reveal the final message, you must combine the fragments **in numerical order**. However, remember that Fragment 4 was just a password, not part of the encoded message. 
Concatenate Fragments 1, 2, 3, 5, and 6 together with absolutely **no whitespace** between them.
Decode the resulting large Base64 string:
```bash
echo "<combined_fragments>" | base64 -d
```
The result is your final decoded message. Ensure your final answer fits the standard `IITB{...}` format.

Submission
In your `labDirectory`, locate the submission template automatically generated for you. It will be named `SUBMIT_FLAGS_HERE.txt` (or `SUBMIT_FLAG_HERE.txt`, depending on your editor's view).
Enter the exact value you found for each fragment next to its label. Do not include extra quotes or formatting. Finally, submit your fully decoded message.
Click Evaluate to check the correctness of your findings.