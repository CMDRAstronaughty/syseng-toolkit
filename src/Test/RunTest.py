import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import importlib.util
import sys

# Load persistence module by file path to avoid package import issues
_p_path = Path(__file__).parent / "persistence.py"
spec = importlib.util.spec_from_file_location("test_persistence", str(_p_path))
persistence = None
if spec and spec.loader:
    module = importlib.util.module_from_spec(spec)
    sys.modules["test_persistence"] = module
    spec.loader.exec_module(module)
    persistence = module
else:
    persistence = None

# Configure page
st.set_page_config(page_title="Run System Tests", layout="wide")
st.title("🧪 Run System Tests")

# Initialize session state for test execution tracking
if "test_events" not in st.session_state:
    # Default sample events: each event contains multiple test cases
    st.session_state.test_events = {
        "EVT-001": {
            "name": "Regression Suite - Release 1.0",
            "description": "Critical regression tests for release 1.0",
            "cases": {
                "TEST-001": {
                    "name": "User Login Verification",
                    "description": "Verify that users can successfully log in with valid credentials",
                    "expected_result": "User is authenticated and redirected to dashboard",
                    "completed": False,
                    "status": "Not Started",
                    "issue_found": False,
                    "issue_description": "",
                    "notes": "",
                    "steps": {
                        "S1": {"description": "Open login page", "completed": False},
                        "S2": {"description": "Enter valid credentials", "completed": False},
                        "S3": {"description": "Submit and verify redirect", "completed": False}
                    }
                },
                "TEST-002": {
                    "name": "Password Reset Flow",
                    "description": "Verify the password reset functionality works correctly",
                    "expected_result": "User receives reset email and can set new password",
                    "completed": False,
                    "status": "Not Started",
                    "issue_found": False,
                    "issue_description": "",
                    "notes": "",
                    "steps": {
                        "S1": {"description": "Navigate to forgot password", "completed": False},
                        "S2": {"description": "Request reset and receive email", "completed": False},
                        "S3": {"description": "Set new password and login", "completed": False}
                    }
                }
            }
        },
        "EVT-002": {
            "name": "Performance Smoke Tests",
            "description": "Quick performance checks for core APIs",
            "cases": {
                "TEST-003": {
                    "name": "API Response Time",
                    "description": "Verify that API endpoints respond within SLA requirements",
                    "expected_result": "All endpoints respond within 500ms",
                    "completed": False,
                    "status": "Not Started",
                    "issue_found": False,
                    "issue_description": "",
                    "notes": "",
                    "steps": {
                        "S1": {"description": "Call /health endpoint", "completed": False},
                        "S2": {"description": "Call critical API and measure time", "completed": False}
                    }
                },
                "TEST-004": {
                    "name": "Database Integrity",
                    "description": "Verify database constraints and data integrity",
                    "expected_result": "No data corruption, all constraints enforced",
                    "completed": False,
                    "status": "Not Started",
                    "issue_found": False,
                    "issue_description": "",
                    "notes": "",
                    "steps": {
                        "S1": {"description": "Check referential integrity", "completed": False},
                        "S2": {"description": "Run sample transactions", "completed": False}
                    }
                }
            }
        }
    }

if "created_issues" not in st.session_state:
    st.session_state.created_issues = []

# Try to pre-load saved events and issues if available (non-destructive)
if persistence is not None:
    try:
        saved_events = persistence.load_events()
        if saved_events:
            # Only override if there is saved content
            st.session_state.test_events = saved_events
    except Exception:
        pass

    try:
        saved_issues = persistence.load_issues()
        if saved_issues:
            st.session_state.created_issues = saved_issues
    except Exception:
        pass

# Sidebar statistics
# Sidebar: select which event to work on
st.sidebar.header("Test Execution Summary")
event_keys = list(st.session_state.test_events.keys())
selected_event = st.sidebar.selectbox(
    "Select Test Event",
    event_keys,
    format_func=lambda k: f"{k} - {st.session_state.test_events[k]['name']}",
    key="selected_event"
)

# Compute stats for the selected event
selected_cases = st.session_state.test_events[selected_event]["cases"]
total_tests = len(selected_cases)
completed_tests = sum(1 for step in selected_cases.values() if step["completed"])
failed_tests = sum(1 for step in selected_cases.values() if step["issue_found"])

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.metric("Total Tests", total_tests)
with col2:
    st.metric("Completed", completed_tests)
with col3:
    st.metric("Failed", failed_tests)

# Progress bar
progress = completed_tests / total_tests if total_tests > 0 else 0
st.sidebar.progress(int(progress * 100))

st.sidebar.divider()

# Persistence controls
st.sidebar.header("Storage")
col_save, col_load = st.sidebar.columns(2)
with col_save:
    if st.button("Save Events", key="save_events"):
        try:
            path = persistence.save_events(st.session_state.test_events)
            st.success(f"Events saved to {path}")
        except Exception as e:
            st.error(f"Failed to save events: {e}")
    if st.button("Save Issues", key="save_issues"):
        try:
            path = persistence.save_issues(st.session_state.created_issues)
            st.success(f"Issues saved to {path}")
        except Exception as e:
            st.error(f"Failed to save issues: {e}")
with col_load:
    if st.button("Load Events", key="load_events"):
        try:
            loaded = persistence.load_events()
            if loaded:
                st.session_state.test_events = loaded
                st.success("Events loaded into session state")
                st.experimental_rerun()
            else:
                st.info("No saved events found")
        except Exception as e:
            st.error(f"Failed to load events: {e}")
    if st.button("Load Issues", key="load_issues"):
        try:
            loaded = persistence.load_issues()
            if loaded:
                st.session_state.created_issues = loaded
                st.success("Issues loaded into session state")
                st.experimental_rerun()
            else:
                st.info("No saved issues found")
        except Exception as e:
            st.error(f"Failed to load issues: {e}")

st.sidebar.caption("Requirements are stored in SQLite; tests and issues use JSON files.")

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
    
    # Work on the selected event's cases
    filtered_tests = selected_cases.copy()
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

                # Checklist steps (detailed test steps)
                steps = test_data.get("steps", {})
                if steps:
                    st.markdown("**Checklist:**")
                    for step_id, step in steps.items():
                        checked = st.checkbox(
                            f"{step_id} - {step['description']}",
                            value=step.get("completed", False),
                            key=f"{test_id}_step_{step_id}"
                        )
                        if checked != step.get("completed", False):
                            st.session_state.test_events[selected_event]["cases"][test_id]["steps"][step_id]["completed"] = checked
                            # update case-level completion/state after a step change
                            st.rerun()

                    # Re-evaluate completion of the case based on steps
                    current_steps = st.session_state.test_events[selected_event]["cases"][test_id].get("steps", {})
                    all_done = all(s.get("completed") for s in current_steps.values()) if current_steps else False
                    any_done = any(s.get("completed") for s in current_steps.values()) if current_steps else False
                    if all_done and not st.session_state.test_events[selected_event]["cases"][test_id].get("completed"):
                        st.session_state.test_events[selected_event]["cases"][test_id]["completed"] = True
                        st.session_state.test_events[selected_event]["cases"][test_id]["status"] = "Completed"
                    elif any_done and not all_done:
                        st.session_state.test_events[selected_event]["cases"][test_id]["status"] = "In Progress"
                    elif not any_done:
                        st.session_state.test_events[selected_event]["cases"][test_id]["status"] = st.session_state.test_events[selected_event]["cases"][test_id].get("status", "Not Started")

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
                        st.session_state.test_events[selected_event]["cases"][test_id]["status"] = new_status
                        st.rerun()

                with col2:
                    # Completion checkbox
                    completed = st.checkbox(
                        "Mark Complete",
                        value=test_data["completed"],
                        key=f"complete_{test_id}"
                    )
                    if completed != test_data["completed"]:
                        st.session_state.test_events[selected_event]["cases"][test_id]["completed"] = completed
                        st.rerun()

                with col3:
                    # Issue found checkbox
                    issue_found = st.checkbox(
                        "Issue Found",
                        value=test_data["issue_found"],
                        key=f"issue_{test_id}"
                    )
                    if issue_found != test_data["issue_found"]:
                        st.session_state.test_events[selected_event]["cases"][test_id]["issue_found"] = issue_found
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
                        st.session_state.test_events[selected_event]["cases"][test_id]["issue_description"] = issue_desc

                    st.divider()

                    # Create issue button
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Create Issue from This Test", key=f"create_issue_{test_id}"):
                            # Create issue
                            issue = {
                                "issue_id": f"ISS-{len(st.session_state.created_issues) + 1:04d}",
                                "event_id": selected_event,
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
                    st.session_state.test_events[selected_event]["cases"][test_id]["notes"] = notes

        # Bulk run controls for selected event
        st.divider()
        st.subheader("Run Test Cases")
        case_keys = list(filtered_tests.keys())
        to_run = st.multiselect("Select test cases to run", case_keys, default=case_keys)
        if st.button("▶️ Run Selected Tests"):
            for cid in to_run:
                st.session_state.test_events[selected_event]["cases"][cid]["status"] = "In Progress"
                # Simulate a run: mark completed unless an issue flag is set
                if st.session_state.test_events[selected_event]["cases"][cid].get("issue_found"):
                    st.session_state.test_events[selected_event]["cases"][cid]["status"] = "Failed"
                else:
                    st.session_state.test_events[selected_event]["cases"][cid]["status"] = "Completed"
                    st.session_state.test_events[selected_event]["cases"][cid]["completed"] = True
            st.success("Selected tests executed (status updated)")
            st.rerun()

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
    for test_id, test_data in selected_cases.items():
        results_data.append({
            "Test ID": test_id,
            "Name": test_data["name"],
            "Status": test_data["status"],
            "Completed": "✅" if test_data["completed"] else "❌",
            "Issue": "⚠️" if test_data["issue_found"] else "✓",
            "Last Updated": datetime.now().strftime("%Y-%m-%d")
        })

    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, width='stretch', hide_index=True)
    
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
            # Export data for selected event
            export_obj = { selected_event: selected_cases }
            json_data = json.dumps(export_obj, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"test_results_{selected_event}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
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
