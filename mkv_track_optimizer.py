import os
import subprocess
import json
from datetime import datetime
from tqdm import tqdm

# Configuration (Customizable section)
DRY_RUN = True  # Set to True for dry-run mode
INPUT_DIRECTORY = "/path/to/input/directory"  # Define your input directory
LOG_DIRECTORY = "/path/to/log/directory"  # Define your log directory
LOG_FILE = os.path.join(LOG_DIRECTORY, "mkv_optimizer.log")  # Log file path
PROCESSED_LOG = os.path.join(LOG_DIRECTORY, "processed_files.log")  # Processed files log path

# Customizable settings
AUDIO_PREFERRED_LANGUAGES = ["jpn", "kor", "tgl"]  # Ranked list of preferred audio languages (in order)
SUBTITLE_PREFERRED_LANGUAGES = ["eng", "und", "rus"]  # Ranked list of preferred subtitle languages (in order)
EXCLUDED_SUBTITLE_KEYWORDS = ["sign", "signs", "song", "songs"]  # Keywords to exclude from default subtitles
PREFERRED_SUBTITLE_KEYWORDS = ["dialogue", "dialog"]  # Keywords to prefer in subtitle tracks

# Make sure the log directory exists
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Logging utility
def log(message):
	"""Log messages to both console and a log file."""
	with open(LOG_FILE, "a") as log_file:
		log_file.write(f"{datetime.now()}: {message}\n")
	print(message)

# Processed files utility
def is_processed(file_path):
	"""Check if a file has already been processed."""
	if not os.path.exists(PROCESSED_LOG):
		return False
	with open(PROCESSED_LOG, "r") as log_file:
		processed_files = log_file.read().splitlines()
	return file_path in processed_files

def mark_as_processed(file_path):
	"""Mark a file as processed."""
	with open(PROCESSED_LOG, "a") as log_file:
		log_file.write(file_path + "\n")

# MKVMerge utility
def get_tracks_with_mkvmerge(file_path):
	"""Retrieve track information using mkvmerge."""
	try:
		result = subprocess.run(
			["mkvmerge", "--identify", "--identification-format", "json", file_path],
			capture_output=True,
			text=True,
			check=True
		)
		return json.loads(result.stdout).get("tracks", [])
	except subprocess.CalledProcessError as e:
		log(f"Error getting track info for {file_path}: {e.stderr}")
		return []
	except Exception as e:
		log(f"Unexpected error getting track info for {file_path}: {e}")
		return []

def find_best_audio_track(tracks, preferred_languages):
	"""Find the best audio track based on the preferred language list."""
	for lang in preferred_languages:
		for track in tracks:
			if track["type"] == "audio" and track.get("properties", {}).get("language", "").lower() == lang:
				return track
	return None

def find_best_subtitle_track(tracks, preferred_languages, excluded_keywords, preferred_keywords):
	"""Find the best subtitle track based on the preferred language list and keywords."""
	for lang in preferred_languages:
		for track in tracks:
			if track["type"] == "subtitles" and track.get("properties", {}).get("language", "").lower() == lang:
				track_name = track.get("properties", {}).get("track_name", "").lower()
				if any(keyword in track_name for keyword in preferred_keywords):
					return track
				if not any(keyword in track_name for keyword in excluded_keywords):
					return track
	return None

def adjust_tracks(file_path, dry_run=False):
	"""Adjust tracks based on specified rules."""
	tracks = get_tracks_with_mkvmerge(file_path)
	if not tracks:
		log(f"No tracks found for file: {file_path}")
		return False

	# Check if file already meets preferences
	default_audio = next((track for track in tracks if track["type"] == "audio" and track.get("properties", {}).get("default_track", 0) == 1), None)
	default_subtitle = next((track for track in tracks if track["type"] == "subtitles" and track.get("properties", {}).get("default_track", 0) == 1), None)

	best_audio_track = find_best_audio_track(tracks, AUDIO_PREFERRED_LANGUAGES)
	best_subtitle_track = find_best_subtitle_track(tracks, SUBTITLE_PREFERRED_LANGUAGES, EXCLUDED_SUBTITLE_KEYWORDS, PREFERRED_SUBTITLE_KEYWORDS)

	if (default_audio and best_audio_track and default_audio["id"] == best_audio_track["id"] and
		default_subtitle and best_subtitle_track and default_subtitle["id"] == best_subtitle_track["id"]):
		log(f"File will be skipped because both audio and subtitle tracks already meet preferences: {file_path}")
		return False

	commands = ["mkvmerge", "-o", f"{file_path}.temp.mkv"]

	audio_changed = False
	subtitle_changed = False

	# Handle audio tracks: Set the preferred one as default, others as not default
	for track in tracks:
		if track["type"] == "audio":
			track_id = track["id"]
			if best_audio_track and track_id == best_audio_track["id"]:
				if dry_run:
					log(f"Audio Track {track_id} would be set as default.")
				else:
					commands.extend(["--default-track", f"{track_id}:1"])
				audio_changed = True
			else:
				if dry_run:
					log(f"Audio Track {track_id} would be unset as default.")
				else:
					commands.extend(["--default-track", f"{track_id}:0"])

	# Handle subtitle tracks: Set the preferred one as default, others as not default
	for track in tracks:
		if track["type"] == "subtitles":
			track_id = track["id"]
			track_name = track.get("properties", {}).get("track_name", "").lower()
			if best_subtitle_track and track_id == best_subtitle_track["id"]:
				if dry_run:
					log(f"Subtitle Track {track_id} would be set as default.")
				else:
					commands.extend(["--default-track", f"{track_id}:1"])
				subtitle_changed = True
			else:
				if any(keyword in track_name for keyword in EXCLUDED_SUBTITLE_KEYWORDS):
					if dry_run:
						log(f"Subtitle Track {track_id} contains excluded keywords and would not be default.")
					else:
						commands.extend(["--default-track", f"{track_id}:0"])
				else:
					if dry_run:
						log(f"Subtitle Track {track_id} would be unset as default.")
					else:
						commands.extend(["--default-track", f"{track_id}:0"])

	# Append the input file path
	commands.append(file_path)

	# Execute or simulate the command
	if dry_run:
		log(f"Dry-run: Would execute: {' '.join(commands)}")
	else:
		try:
			log(f"Executing command: {' '.join(commands)}")
			subprocess.run(commands, check=True)
			os.replace(f"{file_path}.temp.mkv", file_path)
			mark_as_processed(file_path)
			log(f"Adjusted file: {file_path}")
		except subprocess.CalledProcessError as e:
			log(f"Error adjusting file {file_path}: {e}")
			log(f"STDERR: {e.stderr}")
			if os.path.exists(f"{file_path}.temp.mkv"):
				os.remove(f"{file_path}.temp.mkv")  # Clean up temp file
			return False

	return (file_path, audio_changed, subtitle_changed)

def process_directory(directory_path, dry_run=False):
	"""Recursively process files in a directory with progress bar."""
	files_adjusted = 0
	files_skipped = 0
	
	files = [os.path.join(root, file) for root, _, files in os.walk(directory_path) for file in files if file.endswith(".mkv")]
	
	for file_path in tqdm(files, desc="Processing Files", unit="file"):
		if is_processed(file_path):
			log(f"Skipping already processed file: {file_path}")
			files_skipped += 1
			continue
			
		# Process the file
		result = adjust_tracks(file_path, dry_run)
		if result:
			_, audio_changed, subtitle_changed = result
			if not audio_changed and not subtitle_changed:
				log(f"File will be skipped because both audio and subtitle tracks already meet preferences: {file_path}")
				files_skipped += 1
			else:
				files_adjusted += 1
		else:
			files_skipped += 1
	
	# Differentiate the messages based on dry-run vs. full-run mode
	if dry_run:
		log(f"Processing complete. Files that would be adjusted: {files_adjusted}, Files that would be skipped: {files_skipped}")
	else:
		log(f"Processing complete. Files adjusted: {files_adjusted}, Files skipped: {files_skipped}")


			
if __name__ == "__main__":
	mode = "DRY-RUN" if DRY_RUN else "FULL RUN"
	log(f"Starting MKV Optimizer in {mode} mode.")
	process_directory(INPUT_DIRECTORY, DRY_RUN)
	log("MKV Optimizer finished.")

		   
