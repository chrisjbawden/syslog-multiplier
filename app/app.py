import streamlit as st
import os
import re
import time
import shutil
from datetime import datetime

# Hardcoded locations for the configuration and passcode files
LOGSTASH_CONF_PATH = "/opt/syslog-multiplier/logstash.conf"
PASSCODE_FILE = "/opt/syslog-multiplier/passcode.txt"
DEFAULT_PASSCODE = "1234"

# Function to get or initialize the passcode from file
def get_passcode():
    if not os.path.exists(PASSCODE_FILE):
        with open(PASSCODE_FILE, "w") as f:
            f.write(DEFAULT_PASSCODE)
        return DEFAULT_PASSCODE
    else:
        with open(PASSCODE_FILE, "r") as f:
            return f.read().strip()

# -------------------------------
# Authentication Section
# -------------------------------
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

# -------------------------------
# Main App: Raw Configuration Editor
# -------------------------------

# Read current configuration from file (or set a default message)
if os.path.exists(LOGSTASH_CONF_PATH):
    with open(LOGSTASH_CONF_PATH, 'r') as f:
        config_text = f.read()
else:
    config_text = "# Enter configuration here..."

# To force the text area to load the file content on a fresh run (e.g. after a restore),
# we check if 'raw_config' is in session state. If not, we initialize it.
if "raw_config" not in st.session_state:
    st.session_state["raw_config"] = config_text

# Text area for editing the raw configuration
raw_config = st.text_area("Edit Logstash Configuration", value=st.session_state["raw_config"], height=400)


col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    st.empty()

with col2:
    # Save configuration button: writes the text area content back to file
    if st.button("Save Configuration"):
        try:
            with open(LOGSTASH_CONF_PATH, 'w') as f:
                f.write(raw_config)
            st.success("Configuration saved successfully!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save configuration: {e}")
with col3:
    # Refresh configuration button: re-read the file and refresh the app
    if st.button("Refresh Configuration"):
        if os.path.exists(LOGSTASH_CONF_PATH):
            with open(LOGSTASH_CONF_PATH, 'r') as f:
                config_text = f.read()
            # Remove the stored raw config so the text area updates with the latest file contents.
            if "raw_config" in st.session_state:
                del st.session_state["raw_config"]
            st.rerun()
        else:
            st.error("Configuration file not found.")

# -------------------------------
# Backup & Restore Expander
# -------------------------------
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


    st.markdown("#### Existing Backups")
    backup_dir = os.path.dirname(LOGSTASH_CONF_PATH)
    # Find backup files matching the pattern: dd-mm-yyyy or dd-mm-yyyy_counter.conf
    backup_files = [f for f in os.listdir(backup_dir) if re.match(r"^\d{2}-\d{2}-\d{4}_[0-9]{2}-[0-9]{2}(_\d+)?\.conf$", f)]
    backup_files = sorted(backup_files, key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)), reverse=True)
    if backup_files:
        for backup in backup_files:
            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.write(backup)
            with cols[1]:
                # Download backup file button
                backup_path = os.path.join(backup_dir, backup)
                try:
                    with open(backup_path, "r") as f:
                        backup_content = f.read()
                    st.download_button("Download", backup_content, file_name=backup)
                except Exception as e:
                    st.error(f"Error reading backup: {e}")
            with cols[2]:
                # Restore backup: copy backup file to main config file
                if st.button("Restore", key=f"restore_{backup}"):
                    try:
                        with open(backup_path, 'r') as f:
                            content = f.read()
                        with open(LOGSTASH_CONF_PATH, 'w') as f:
                            f.write(content)
                        st.success(f"Restored backup: {backup}")
                        # Clear stored raw config so that text area loads the restored file
                        if "raw_config" in st.session_state:
                            del st.session_state["raw_config"]
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to restore backup: {e}")
            with cols[3]:
                # Delete backup file button
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
                st.rerun()  # After submission, the form resets and uploader clears
            except Exception as e:
                st.error(f"Error saving uploaded backup: {e}")
        else:
            st.error("No file uploaded.")

# -------------------------------
# Download Current Configuration Button (Main Area)
# -------------------------------


# -------------------------------
# Passcode Management Section
# -------------------------------
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
