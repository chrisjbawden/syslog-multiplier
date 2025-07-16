__version__ = "1.0.1"

import streamlit as st
import os
import re
import time
import shutil
import subprocess
from datetime import datetime
import streamlit.components.v1 as components

# ---- Version Check Widget ----
CURRENT_APP_PATH = os.path.abspath(__file__)
NEW_APP_PATH = "/opt/syslog-multiplier/new/app.py"  # Path to the new version to check against

def extract_version(filepath):
    """
    Extracts __version__ = "x.y.z" from a Python file.
    """
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        for line in f:
            m = re.match(r"__version__\s*=\s*['\"](.+?)['\"]", line.strip())
            if m:
                return m.group(1)
    return None

def compare_versions(v1, v2):
    # Returns True if v2 > v1 (semantic version, ignores extra labels)
    def parse(v):
        return [int(x) for x in v.split(".")]
    return parse(v2) > parse(v1)

current_version = __version__
new_version = extract_version(NEW_APP_PATH)

if new_version and compare_versions(current_version, new_version):
    info_col, update_col = st.columns([4,1])
    with info_col:
        st.info(f"**A newer version is available: {new_version}** (current: {current_version})")
    with update_col:
        if st.button("Update with newer"):
            try:
                # Back up current app.py
                backup_path = CURRENT_APP_PATH + f".bak_{current_version}"
                shutil.copy(CURRENT_APP_PATH, backup_path)
                # Replace with new version
                shutil.copy(NEW_APP_PATH, CURRENT_APP_PATH)
                st.success(f"App updated to {new_version} and backed up as {os.path.basename(backup_path)}. Please restart the app.")
            except Exception as e:
                st.error(f"Update failed: {e}")

# Hardcoded locations for the configuration and passcode files
LOGSTASH_CONF_PATH = "/opt/syslog-multiplier/logstash.conf"
PASSCODE_FILE = "/opt/syslog-multiplier/passcode.txt"
DEFAULT_PASSCODE = "1234"

# ----------- Logstash Status Utilities -----------
def get_logstash_status():
    try:
        output = subprocess.check_output(['pgrep', '-f', 'logstash'], text=True)
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def restart_logstash():
    """
    Finds and kills all logstash processes, then runs the launch.sh script.
    Returns (success, message).
    """
    try:
        # Find PIDs of logstash processes
        find_proc = subprocess.run(
            ["pgrep", "-f", "logstash"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        pids = [pid for pid in find_proc.stdout.strip().split('\n') if pid.strip().isdigit()]

        # Kill all logstash PIDs
        if pids:
            kill_cmd = ["kill", "-9"] + pids
            kill_proc = subprocess.run(
                kill_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            time.sleep(1)  # Give a moment for processes to die

        # Run the launch script
        launch_script = "/opt/syslog-multiplier/start-logstash.sh"
        run_script = subprocess.run(
            [launch_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        time.sleep(2)  # Give time for logstash to start

        # Check if Logstash is running
        if get_logstash_status():
            return True, "Logstash was killed and restarted successfully."
        else:
            return False, f"Tried to restart, but Logstash is still not running. Script output: {run_script.stdout.strip()} Error: {run_script.stderr.strip()}"

    except Exception as e:
        return False, f"Exception while restarting: {e}"

# Function to get or initialize the passcode from file
def get_passcode():
    if not os.path.exists(PASSCODE_FILE):
        with open(PASSCODE_FILE, "w") as f:
            f.write(DEFAULT_PASSCODE)
        return DEFAULT_PASSCODE
    else:
        with open(PASSCODE_FILE, "r") as f:
            return f.read().strip()

# ------------------------------- Authentication Section -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<div style='margin-top: 45%;'></div>", unsafe_allow_html=True)
    code = st.text_input("Enter passcode to access configuration", type="password")
    if code:
        stored_code = get_passcode()
        if code == stored_code:
            st.session_state["authenticated"] = True
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Incorrect passcode")
    st.stop()

# ------------------------------- Logstash Status Section -------------------------------
with st.container():
    status_col, button_col = st.columns([3, 1])
    is_running = get_logstash_status()
    if not is_running:
        with status_col:
            st.warning("⚠️ Logstash is **not running**! The configuration editor will not have any effect until Logstash is restarted.")
        with button_col:
            if st.button("Restart Logstash"):
                success, msg = restart_logstash()
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()

# ------------------------------- Main App: Raw Configuration Editor -------------------------------

def load_config():
    """Load the configuration from file, or return a default string."""
    if os.path.exists(LOGSTASH_CONF_PATH):
        with open(LOGSTASH_CONF_PATH, "r") as f:
            return f.read()
    return "# Enter configuration here..."

# Initialise session state values if they don't exist
if "raw_config" not in st.session_state:
    st.session_state["raw_config"] = load_config()
if "raw_config_refresh_key" not in st.session_state:
    st.session_state["raw_config_refresh_key"] = 0

# Create a placeholder for the text area
config_placeholder = st.empty()

def render_text_area():
    """Render the configuration text area with a unique key."""
    unique_key = f"raw_config_area_{st.session_state['raw_config_refresh_key']}"
    return config_placeholder.text_area(
        "Edit Logstash Configuration",
        value=st.session_state["raw_config"],
        height=400,
        key=unique_key
    )

# Render the initial text area
raw_config = render_text_area()

col1, col2, col3 = st.columns([3, 2, 2])
with col2:
    if st.button("Save Configuration"):
        try:
            with open(LOGSTASH_CONF_PATH, "w") as f:
                f.write(raw_config)
            st.success("Configuration saved!")
        except Exception as e:
            st.error(f"Failed to save configuration: {e}")

with col3:
    if st.button("Reload Configuration"):
        # Reload the file and update session state
        st.session_state["raw_config"] = load_config()
        # Increment the refresh counter to force a new unique key
        st.session_state["raw_config_refresh_key"] += 1
        # Clear the placeholder and re-render the text area
        config_placeholder.empty()
        render_text_area()

# ------------------------------- Backup & Restore Expander -------------------------------
with st.expander("Backup & Restore"):

    col1, col2, col3 = st.columns([3, 2, 2])

    with col1:
        st.empty()

    with col2:
        if st.button("Create Backup"):
            if os.path.exists(LOGSTASH_CONF_PATH):
                backup_dir = os.path.dirname(LOGSTASH_CONF_PATH)
                # Include a timestamp in the file name
                date_str = datetime.now().strftime("%d-%m-%Y_%H-%M")
                backup_filename = os.path.join(backup_dir, f"{date_str}.conf")
                counter = 1
                # If a backup with this timestamp exists, append a counter
                while os.path.exists(backup_filename):
                    backup_filename = os.path.join(backup_dir, f"{date_str}_{counter}.conf")
                    counter += 1
                try:
                    shutil.copy(LOGSTASH_CONF_PATH, backup_filename)
                    st.success(f"Backup created: {os.path.basename(backup_filename)}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating backup: {e}")
            else:
                st.error("No configuration file to backup.")
    with col3:
        st.download_button("Download Current Config", raw_config, file_name="logstash.conf")

    st.markdown('---')

    def extract_datetime(filename):
        # Matches filenames like 25-03-2025_15-30.conf or 25-03-2025_15-30_1.conf
        m = re.match(r"^(\d{2}-\d{2}-\d{4}_[0-9]{2}-[0-9]{2})(?:_\d+)?\.conf$", filename)
        if m:
            dt_str = m.group(1)
            return datetime.strptime(dt_str, "%d-%m-%Y_%H-%M")
        # Return a very old date if no match (ensures these files appear at the end)
        return datetime.min

    st.markdown("#### Existing Backups")
    backup_dir = os.path.dirname(LOGSTASH_CONF_PATH)
    backup_files = [f for f in os.listdir(backup_dir) if re.match(r"^\d{2}-\d{2}-\d{4}_[0-9]{2}-[0-9]{2}(_\d+)?\.conf$", f)]
    backup_files = sorted(backup_files, key=lambda f: extract_datetime(f), reverse=True)

    if backup_files:
        for backup in backup_files:
            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.write(backup)
            with cols[1]:
                backup_path = os.path.join(backup_dir, backup)
                try:
                    with open(backup_path, "r") as f:
                        backup_content = f.read()
                    st.download_button("Download", backup_content, file_name=backup)
                except Exception as e:
                    st.error(f"Error reading backup: {e}")
            with cols[2]:
                if st.button("Restore", key=f"restore_{backup}"):
                    try:
                        with open(backup_path, 'r') as f:
                            content = f.read()
                        with open(LOGSTASH_CONF_PATH, 'w') as f:
                            f.write(content)
                        st.success(f"Restored backup: {backup}")
                        if "raw_config" in st.session_state:
                            del st.session_state["raw_config"]
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to restore backup: {e}")
            with cols[3]:
                if st.button("Delete", key=f"delete_{backup}"):
                    try:
                        os.remove(backup_path)
                        st.success(f"Deleted backup: {backup}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete backup: {e}")
    else:
        st.info("No backups found.")

    st.markdown('---')

    st.markdown("#### Upload Backup File")
    with st.form(clear_on_submit=True, key="upload_form"):
        uploaded_backup = st.file_uploader("Upload a backup file", type=["conf", "txt"])
        submit_upload = st.form_submit_button("Upload Backup")

    if submit_upload:
        if uploaded_backup is not None:
            backup_content = uploaded_backup.getvalue().decode("utf-8")
            backup_name = uploaded_backup.name
            backup_save_path = os.path.join(backup_dir, backup_name)
            try:
                with open(backup_save_path, "w") as f:
                    f.write(backup_content)
                st.success(f"Backup file {backup_name} uploaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving uploaded backup: {e}")
        else:
            st.error("No file uploaded.")

# ------------------------------- Passcode Management Section -------------------------------
with st.expander("Access"):
    new_code = st.text_input("Enter new passcode", type="password", key="new_passcode")
    if st.button("Update Passcode"):
        if new_code:
            try:
                with open(PASSCODE_FILE, "w") as f:
                    f.write(new_code)
                st.success("Passcode updated successfully!")
            except Exception as e:
                st.error(f"Error updating passcode: {e}")
        else:
            st.error("Please enter a new passcode.")

# JavaScript code that resets a timer on user activity and refreshes the page after 30 minutes of inactivity.
js_code = """
<script>
  // Set inactivity timeout period in milliseconds (30 minutes = 1800000 ms)
  var inactivityTime = 180000;
  var timeout;

  function resetTimer() {
      clearTimeout(timeout);
      timeout = setTimeout(function(){ window.top.location.reload(); }, inactivityTime);
  }

  // List of events to listen for user activity.
  window.onload = resetTimer;
  document.onmousemove = resetTimer;
  document.onkeypress = resetTimer;
  document.onclick = resetTimer;
  document.onscroll = resetTimer;
</script>
"""

components.html(js_code, height=0)

# -------------------------------
# Restart Logstash Button (Bottom)
# -------------------------------
st.markdown("---")
bottom_col1, bottom_col2, bottom_col3 = st.columns([3, 2, 2])
with bottom_col2:
    if st.button("Restart Logstash", key="bottom_restart"):
        success, msg = restart_logstash()
        if success:
            st.success(msg)
        else:
            st.error(msg)
        st.rerun()
