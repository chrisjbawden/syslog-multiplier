import streamlit as st
import os
import re

# Hardcoded location for the logstash.conf file
LOGSTASH_CONF_PATH = "/etc/logstash/logstash.conf"

# CSS for styling and vertically aligning the buttons
st.markdown(
    """
    <style>
    .stColumn .stButton > button {
        width: 100%;
        margin-top: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to parse existing logstash.conf file
def parse_logstash_config():
    outputs = []
    
    # Check if the file exists
    if os.path.exists(LOGSTASH_CONF_PATH):
        with open(LOGSTASH_CONF_PATH, 'r') as file:
            content = file.read()

        # Split the configuration into blocks by 'syslog {'
        syslog_blocks = re.split(r'syslog\s*{', content)

        # Iterate through blocks and extract host, port, and protocol
        for block in syslog_blocks[1:]:  # Skip the first split part, it's not a syslog block
            # Extract host
            host_match = re.search(r'host\s*=>\s*"(.*?)"', block)
            port_match = re.search(r'port\s*=>\s*(\d+)', block)
            protocol_match = re.search(r'protocol\s*=>\s*"(.*?)"', block)

            # If host, port, and protocol are found, add them to outputs
            if host_match and port_match and protocol_match:
                outputs.append({
                    'host': host_match.group(1),
                    'port': port_match.group(1),
                    'protocol': protocol_match.group(1)
                })
    
    return outputs

# Initialize session state with existing outputs from config
if 'outputs' not in st.session_state:
    st.session_state['outputs'] = parse_logstash_config()

# Function to render output row
def render_output(index, output):
    # Columns layout
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        # Editable fields: host, port, and protocol
        host = st.text_input(f"Host (Output {index+1})", output.get('host', ''), key=f"host_{index}")
        port = st.text_input(f"Port (Output {index+1})", output.get('port', ''), key=f"port_{index}")
        protocol = st.selectbox(f"Protocol (Output {index+1})", ["udp", "tcp"], index=0 if output.get('protocol', 'udp') == 'udp' else 1, key=f"protocol_{index}")

    with col2:
        # Save button to save changes
        if st.button(f"Save", key=f"save_{index}"):
            # Update the output configuration
            st.session_state['outputs'][index] = {
                'host': host,
                'port': port,
                'protocol': protocol
            }
            st.success(f"Output {index+1} updated!")

    with col3:
        # X button to remove an output
        if st.button(f"Remove", key=f"remove_{index}"):
            del st.session_state['outputs'][index]
            st.rerun()  # Rerun to update UI

# Title
#st.title("Logstash Output Configuration")

# Display each output row
for index, output in enumerate(st.session_state['outputs']):
    render_output(index, output)

# Add new output section
if st.button("Add New Output"):
    # Add a blank template for a new output
    st.session_state['outputs'].append({'host': '', 'port': '', 'protocol': 'udp'})
    st.rerun()

# Display and save final configuration
st.subheader("Current Logstash Configuration")

# Generate a sample logstash config output for syslog
config_text = "output {\n"
for i, output in enumerate(st.session_state['outputs']):
    config_text += f"  syslog {{\n"
    config_text += f"    host => \"{output['host']}\"\n"
    config_text += f"    port => {output['port']}\n"
    config_text += f"    protocol => \"{output['protocol']}\"\n"
    config_text += "  }\n"
config_text += "}\n"

# Display the generated config file
st.code(config_text, language="bash")

# Save configuration to the hardcoded path
if st.button("Save Configuration"):
    try:
        with open(LOGSTASH_CONF_PATH, 'w') as file:
            file.write(config_text)
        st.success(f"Configuration saved to {LOGSTASH_CONF_PATH}")
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")
