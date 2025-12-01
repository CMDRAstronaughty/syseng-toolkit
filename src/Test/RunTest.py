import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# Configure page
st.set_page_config(page_title="Run System Tests", layout="wide")
st.title("🧪 Run System Tests")

# Initialize session state for test execution tracking
if "test_steps" not in st.session_state:
    st.session_state.test_steps = {
        "TEST-001": {
            "name": "User Login Verification",
            "description": "Verify that users can successfully log in with valid credentials",
            "expected_result": "User is authenticated and redirected to dashboard",
            "completed": False,
            "status": "Not Started",
            "issue_found": False,
            "issue_description": ""
        },
        "TEST-002": {
            "name": "Password Reset Flow",
            "description": "Verify the password reset functionality works correctly",
            "expected_result": "User receives reset email and can set new password",
            "completed": False,
            "status": "Not Started",
            "issue_found": False,
            "issue_description": ""
        },
        "TEST-003": {
            "name": "Data Validation",
            "description": "Verify that form inputs are properly validated",
            "expected_result": "Invalid data is rejected with appropriate error messages",
            "completed": False,
            "status": "Not Started",
            "issue_found": False,
            "issue_description": ""
        },
        "TEST-004": {
            "name": "API Response Time",
            "description": "Verify that API endpoints respond within SLA requirements",
            "expected_result": "All endpoints respond within 500ms",
            "completed": False,
            "status": "Not Started",
            "issue_found": False,
            "issue_description": ""
        },
        "TEST-005": {
            "name": "Database Integrity",
            "description": "Verify database constraints and data integrity",
            "expected_result": "No data corruption, all constraints enforced",
            "completed": False,
            "status": "Not Started",
            "issue_found": False,
            "issue_description": ""
        }
    }

if "created_issues" not in st.session_state:
    st.session_state.created_issues = []

# Sidebar statistics
st.sidebar.header("Test Execution Summary")
total_tests = len(st.session_state.test_steps)
completed_tests = sum(1 for step in st.session_state.test_steps.values() if step["completed"])
failed_tests = sum(1 for step in st.session_state.test_steps.values() if step["issue_found"])

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.metric("Total Tests", total_tests)
with col2:
    st.metric("Completed", completed_tests)
with col3:
    st.metric("Failed", failed_tests)

# Progress bar
progress = completed_tests / total_tests if total_tests > 0 else 0
st.sidebar.progress(progress, text=f"{int(progress*100)}% Complete")

st.sidebar.divider()

# Filter options
st.sidebar.header("Filters")
filter_status = st.sidebar.selectbox(
    "Filter by Status",
    ["All", "Not Started", "In Progress", "Completed", "Failed"]
)

# Tab layout
tab1, tab2, tab3 = st.tabs(["Execute Tests", "Test Results", "Created Issues"])

# ============== TAB 1: EXECUTE TESTS ==============
with tab1:
    st.subheader("Test Execution Steps")
    
    # Filter tests
    filtered_tests = st.session_state.test_steps.copy()
    if filter_status != "All":
        if filter_status == "Failed":
            filtered_tests = {k: v for k, v in filtered_tests.items() if v["issue_found"]}
        else:
            filtered_tests = {k: v for k, v in filtered_tests.items() if v["status"] == filter_status}
    
    if len(filtered_tests) == 0:
        st.info("No tests match the selected filter.")
    else:
        for test_id, test_data in filtered_tests.items():
            with st.expander(
                f"**{test_id}** - {test_data['name']} [{test_data['status']}]",
                expanded=False
            ):
                # Test details
                st.write("**Description:**")
                st.write(test_data['description'])
                
                st.write("**Expected Result:**")
                st.write(test_data['expected_result'])
                
                st.divider()
                
                # Test execution controls
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Status dropdown
                    status_options = ["Not Started", "In Progress", "Completed", "Failed"]
                    new_status = st.selectbox(
                        "Test Status",
                        status_options,
                        index=status_options.index(test_data["status"]),
                        key=f"status_{test_id}"
                    )
                    if new_status != test_data["status"]:
                        st.session_state.test_steps[test_id]["status"] = new_status
                        st.rerun()
                
                with col2:
                    # Completion checkbox
                    completed = st.checkbox(
                        "Mark Complete",
                        value=test_data["completed"],
                        key=f"complete_{test_id}"
                    )
                    if completed != test_data["completed"]:
                        st.session_state.test_steps[test_id]["completed"] = completed
                        st.rerun()
                
                with col3:
                    # Issue found checkbox
                    issue_found = st.checkbox(
                        "Issue Found",
                        value=test_data["issue_found"],
                        key=f"issue_{test_id}"
                    )
                    if issue_found != test_data["issue_found"]:
                        st.session_state.test_steps[test_id]["issue_found"] = issue_found
                        st.rerun()
                
                st.divider()
                
                # Issue description (if issue found)
                if test_data["issue_found"]:
                    st.warning("⚠️ Issue Detected")
                    issue_desc = st.text_area(
                        "Issue Description",
                        value=test_data.get("issue_description", ""),
                        key=f"issue_desc_{test_id}",
                        placeholder="Describe the issue found..."
                    )
                    if issue_desc != test_data.get("issue_description", ""):
                        st.session_state.test_steps[test_id]["issue_description"] = issue_desc
                    
                    st.divider()
                    
                    # Create issue button
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Create Issue from This Test", key=f"create_issue_{test_id}"):
                            # Create issue
                            issue = {
                                "issue_id": f"ISS-{len(st.session_state.created_issues) + 1:04d}",
                                "test_id": test_id,
                                "test_name": test_data["name"],
                                "title": f"Issue from {test_id}: {test_data['name']}",
                                "description": issue_desc or test_data.get("issue_description", ""),
                                "severity": "High",
                                "status": "Open",
                                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "assigned_to": ""
                            }
                            st.session_state.created_issues.append(issue)
                            st.success(f"✅ Issue {issue['issue_id']} created successfully!")
                            st.rerun()
                    
                    with col2:
                        severity = st.selectbox(
                            "Issue Severity",
                            ["Critical", "High", "Medium", "Low"],
                            index=1,
                            key=f"severity_{test_id}"
                        )
                
                # Test notes
                notes = st.text_area(
                    "Test Notes/Observations",
                    value=test_data.get("notes", ""),
                    key=f"notes_{test_id}",
                    placeholder="Add any notes or observations...",
                    height=80
                )
                if notes != test_data.get("notes", ""):
                    st.session_state.test_steps[test_id]["notes"] = notes

# ============== TAB 2: TEST RESULTS ==============
with tab2:
    st.subheader("Test Results Summary")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", total_tests)
    with col2:
        st.metric("Passed", completed_tests - failed_tests)
    with col3:
        st.metric("Failed", failed_tests)
    with col4:
        success_rate = ((completed_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.divider()
    
    # Results table
    st.subheader("Detailed Results")
    results_data = []
    for test_id, test_data in st.session_state.test_steps.items():
        results_data.append({
            "Test ID": test_id,
            "Name": test_data["name"],
            "Status": test_data["status"],
            "Completed": "✅" if test_data["completed"] else "❌",
            "Issue": "⚠️" if test_data["issue_found"] else "✓",
            "Last Updated": datetime.now().strftime("%Y-%m-%d")
        })
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Export test results
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export as CSV"):
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Export as JSON"):
            json_data = json.dumps(st.session_state.test_steps, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# ============== TAB 3: CREATED ISSUES ==============
with tab3:
    st.subheader("Issues Created from Tests")
    
    if len(st.session_state.created_issues) == 0:
        st.info("No issues created yet. Create issues from test failures in the 'Execute Tests' tab.")
    else:
        st.success(f"Total Issues Created: {len(st.session_state.created_issues)}")
        
        st.divider()
        
        # Display issues
        for idx, issue in enumerate(st.session_state.created_issues):
            with st.expander(
                f"**{issue['issue_id']}** - {issue['title']} [{issue['status']}]",
                expanded=False
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Severity:**", issue['severity'])
                with col2:
                    st.write("**Status:**", issue['status'])
                with col3:
                    st.write("**Created:**", issue['created_date'])
                
                st.write("**Related Test:**", f"{issue['test_id']} - {issue['test_name']}")
                
                st.write("**Description:**")
                st.write(issue['description'])
                
                st.divider()
                
                # Issue management
                col1, col2 = st.columns(2)
                
                with col1:
                    new_status = st.selectbox(
                        "Issue Status",
                        ["Open", "In Progress", "Resolved", "Closed"],
                        index=["Open", "In Progress", "Resolved", "Closed"].index(issue["status"]),
                        key=f"issue_status_{idx}"
                    )
                    if new_status != issue["status"]:
                        st.session_state.created_issues[idx]["status"] = new_status
                        st.rerun()
                
                with col2:
                    assigned_to = st.text_input(
                        "Assign To",
                        value=issue.get("assigned_to", ""),
                        key=f"assigned_{idx}"
                    )
                    if assigned_to != issue.get("assigned_to", ""):
                        st.session_state.created_issues[idx]["assigned_to"] = assigned_to
                
                # Delete issue button
                if st.button("🗑️ Delete Issue", key=f"delete_issue_{idx}"):
                    del st.session_state.created_issues[idx]
                    st.success("Issue deleted")
                    st.rerun()
        
        st.divider()
        
        # Export issues
        st.subheader("Export Issues")
        if st.button("📥 Export Issues as JSON"):
            json_data = json.dumps(st.session_state.created_issues, indent=2)
            st.download_button(
                label="Download Issues JSON",
                data=json_data,
                file_name=f"created_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
