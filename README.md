**Customizable MKV audio and subtitle track selection with dry-run and full-run modes, comprehensive logging, and the ability to skip previously processed files on subsequent runs.**

---

## 1. Who This Script is Made For

Are you tired of switching audio or subtitle tracks every time you start a video because your preferred tracks aren’t set as default? If you have a large media collection with incorrectly flagged audio and subtitle tracks, this script is for you. It automates the process of setting your preferred tracks as default while ensuring other tracks are explicitly marked as not default, saving you time and effort.

---

## 2. What This Script Does

### **Core Features**

- **Audio Track Selection**:
    - Automatically selects the audio track that matches your preferred languages (ranked list).
    - Marks the selected audio track as `default`.
    - Ensures all other audio tracks are explicitly marked as `not default`.
- **Subtitle Track Selection**:
    - Automatically selects the best subtitle track based on your preferences:
        - A ranked list of subtitle languages.
        - Tracks with specific keywords (e.g., "dialogue") are prioritized.
        - Tracks with unwanted keywords (e.g., "signs", "songs") are excluded.
    - Marks the selected subtitle track as `default`.
    - Ensures all other subtitle tracks are explicitly marked as `not default`.
- **Dry-Run Mode**:
    - Simulates changes without modifying files.
    - Logs detailed information about what changes **would** be made.
- **Batch Processing**:
    - Processes all `.mkv` files in a given directory (recursively).
    - Skips files that have already been processed (tracked in a log file).
- **Comprehensive Logging**:
    - Logs all actions, including processed files, skipped files, and errors.
- **Error Handling**:
    - Cleans up temporary files in case of unexpected errors.

---

## 3. Disclaimer

I’m not a professional coder, and this script was written entirely using ChatGPT. I wanted to share it because it worked really well for me, and it might help others too — or at the very least serve as a base for your own modifications. Please note that I’ve successfully used it on over 3,500 anime episodes without issues, but I can’t guarantee flawless results for all use cases. Before running this script on your entire library, test it on a small set of files with varying configurations. I am not responsible for any issues, such as data loss or unintended changes. Always back up your media beforehand — this is a best practice for any automated batch processing. I’ll *maybe* consider handling issues or feature requests if I have the time or ChatGPT works well with me.

Feel free to fork, tweak, and improve this script as you see fit. Enjoy!

---

## 4. How to Install Dependencies

This script depends on **Python 3.6+** and `mkvmerge` (from MKVToolNix). Follow the instructions for your operating system below.

### **Windows**

1. **Install Python**:
    - Download and install Python 3.x from [python.org](https://www.python.org/).
    - During installation, check the box that says **“Add Python to PATH”**.
2. **Install MKVToolNix**:
    - Download the MKVToolNix installer from the [official MKVToolNix site](https://mkvtoolnix.download/).
    - Install and add the `mkvmerge` executable to your system PATH.
3. **Install `tqdm` (optional dependency for progress bars)**:
    - Open Command Prompt and run:
        
        ```bash
        pip install tqdm
        
        ```
        

---

### **macOS**

1. **Install Homebrew** (if not already installed):
    
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    ```
    
2. **Install Python and MKVToolNix**:
    
    ```bash
    brew install python mkvtoolnix
    
    ```
    
3. **Install `tqdm`**:
    
    ```bash
    pip3 install tqdm
    
    ```
    

---

### **Linux** (Ubuntu/Debian-based systems)

1. **Install Python**:
    
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    
    ```
    
2. **Install MKVToolNix**:
    
    ```bash
    sudo apt install mkvtoolnix
    
    ```
    
3. **Install `tqdm`**:
    
    ```bash
    pip3 install tqdm
    
    ```
    

---

## 5. How to Configure the Script

The script is customizable through several configuration options. Below is the complete breakdown:

### **General Configuration**

```python
DRY_RUN = True  # Set to True for dry-run mode (no changes made); False for full-run
INPUT_DIRECTORY = "/path/to/input/directory"  # Directory containing MKV files
LOG_DIRECTORY = "/path/to/log/directory"  # Directory for log files

```

- **`DRY_RUN`**: Set to `True` for testing without modifying files. Set to `False` for full execution.
- **`INPUT_DIRECTORY`**: The folder containing the `.mkv` files you want to process.
- **`LOG_DIRECTORY`**: Where logs (activity and processed files) will be stored.

---

### **Audio Preferences**

```python
AUDIO_PREFERRED_LANGUAGES = ["jpn", "kor", "tgl"]  # Ranked list of preferred audio languages

```

- Add your preferred audio languages in order of priority (use language codes like "eng", "jpn", etc.).
- Example: To prioritize Japanese audio, followed by Korean, then Tagalog, use the above setting.

---

### **Subtitle Preferences**

```python
SUBTITLE_PREFERRED_LANGUAGES = ["eng", "und", "rus"]  # Ranked list of subtitle languages
EXCLUDED_SUBTITLE_KEYWORDS = ["sign", "signs", "song", "songs"]  # Exclude tracks with these keywords
PREFERRED_SUBTITLE_KEYWORDS = ["dialogue", "dialog"]  # Prefer tracks with these keywords

```

- **`SUBTITLE_PREFERRED_LANGUAGES`**: Ranked list of your preferred subtitle languages.
- **`EXCLUDED_SUBTITLE_KEYWORDS`**: Tracks with these keywords in their titles will be ignored. Use `[]` if you have no exclusions.
- **`PREFERRED_SUBTITLE_KEYWORDS`**: Keywords that will prioritize a subtitle track. Use `[]` if you have no preferences.

---

## 6. Usage

### **Run the Script**

1. Open a terminal/command prompt.
2. Navigate to the directory containing the script:
    
    ```bash
    cd /path/to/script
    
    ```
    
3. Run the script:
    
    ```bash
    python3 mkv_track_optimizer.py
    
    ```
    

---

### **Dry-Run Example**

To preview the changes without modifying the files:

```python
DRY_RUN = True

```

**Output**:

```arduino
Dry-run: Audio Track 1 would be set as default.
Dry-run: Audio Track 2 would be unset as default.
Dry-run: Subtitle Track 3 would be set as default.
Dry-run: Subtitle Track 4 contains excluded keywords and would not be default.

```

---

### **Full Execution**

When you're ready to apply the changes:

```python
DRY_RUN = False

```

**Output**:

```vbnet
Processing: MyAnimeEpisode.mkv
Adjusting tracks...
Audio Track 1 set as default.
Audio Track 2 marked as not default.
Subtitle Track 3 set as default.
Subtitle Track 4 marked as not default.
Done:

```
