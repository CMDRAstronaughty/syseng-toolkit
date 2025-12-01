import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Configure page
st.set_page_config(page_title="Requirements Management", layout="wide")
st.title("Requirements Management")

# Load requirements data
@st.cache_data
def load_requirements():
    req_path = Path("/home/myintsai/Documents/syseng-toolkit/data/requirements/fun_requirements.json")
    with open(req_path, 'r') as f:
        data = json.load(f)
    
    # Flatten the nested structure
    requirements = []
    for item in data:
        for req_id, details in item.items():
            req_dict = {
                "ID": req_id,
                "Name": details.get("name", ""),
                "Description": details.get("description", ""),
                "Priority": details.get("priority", ""),
                "Status": details.get("status", ""),
                "Tags": ", ".join(details.get("tags", [])),
            }
            # Add manager info from closure details if available
            closure_details = details.get("Closure Details", [])
            if closure_details:
                req_dict["Closure Code"] = closure_details[-1].get("Closure Code", "")
                req_dict["Closure Comments"] = closure_details[-1].get("Closure Comments", "")
            requirements.append(req_dict)
    
    return requirements

# Load data
try:
    requirements = load_requirements()
    df = pd.DataFrame(requirements)
    
    # Create sidebar filters
    st.sidebar.header("Filters")
    
    # Filter by Status
    status_options = ["All"] + sorted(df["Status"].unique().tolist())
    selected_status = st.sidebar.selectbox(
        "Filter by Status",
        status_options,
        help="Select a requirement status to filter"
    )
    
    # Filter by Priority
    priority_options = ["All"] + sorted(df["Priority"].unique().tolist())
    selected_priority = st.sidebar.selectbox(
        "Filter by Priority",
        priority_options,
        help="Select a priority level to filter"
    )
    
    # Filter by Tags
    all_tags = []
    for tags_str in df["Tags"]:
        all_tags.extend([tag.strip() for tag in tags_str.split(",")])
    tag_options = ["All"] + sorted(set(all_tags))
    selected_tag = st.sidebar.selectbox(
        "Filter by Tag",
        tag_options,
        help="Select a tag to filter requirements"
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == selected_status]
    
    if selected_priority != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == selected_priority]
    
    if selected_tag != "All":
        filtered_df = filtered_df[
            filtered_df["Tags"].str.contains(selected_tag, na=False, case=False)
        ]
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requirements", len(df))
    with col2:
        st.metric("Filtered Results", len(filtered_df))
    with col3:
        open_count = len(df[df["Status"] == "Open"])
        st.metric("Open Requirements", open_count)
    with col4:
        high_priority = len(df[df["Priority"] == "High"])
        st.metric("High Priority", high_priority)
    
    st.divider()
    
    # Display requirements table
    st.subheader(f"Requirements ({len(filtered_df)} results)")
    
    if len(filtered_df) > 0:
        # Create expandable cards for each requirement
        for idx, row in filtered_df.iterrows():
            with st.expander(f"**{row['ID']}** - {row['Name']} [{row['Status']}]", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Priority:**", row['Priority'])
                with col2:
                    st.write("**Status:**", row['Status'])
                with col3:
                    st.write("**Tags:**", row['Tags'])
                
                st.write("**Description:**")
                st.write(row['Description'])
                
                if pd.notna(row.get('Closure Code')):
                    st.write("**Closure Code:**", row['Closure Code'])
                if pd.notna(row.get('Closure Comments')):
                    st.write("**Closure Comments:**", row['Closure Comments'])
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{row['ID']}"):
                        st.session_state[f"editing_{row['ID']}"] = True
                        st.rerun()
                with col2:
                    if st.button("📋 Update Status", key=f"status_{row['ID']}"):
                        st.session_state[f"status_update_{row['ID']}"] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{row['ID']}"):
                        st.warning(f"Delete confirmation for {row['ID']} would be implemented here")
    else:
        st.info("No requirements match the selected filters.")
    
    st.divider()
    
    # Add new requirement section
    st.subheader("Add New Requirement")
    with st.form("new_requirement_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Requirement ID (e.g., FUN-0005)")
            new_name = st.text_input("Requirement Name")
        with col2:
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            new_status = st.selectbox("Status", ["Open", "In Progress", "Closed", "Failed"])
        
        new_description = st.text_area("Description")
        new_tags = st.text_input("Tags (comma-separated)")
        
        submit = st.form_submit_button("➕ Add Requirement")
        if submit:
            if new_id and new_name and new_description:
                st.success(f"Requirement {new_id} would be added to the system")
            else:
                st.error("Please fill in all required fields")

except FileNotFoundError:
    st.error("Requirements data file not found. Please check the data path.")
except Exception as e:
    st.error(f"Error loading requirements: {str(e)}")

