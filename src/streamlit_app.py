import streamlit as st


pages = {
    "Home": [
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/HomeBar/Home.py", title= "Home"),
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/HomeBar/About.py", title= "About"),
    ],
    "Requirements": [
        st.Page("RequirementsMgmt.py", title= "Requirements Management"),
        st.Page("RequirementsView.py", title= "View Requirements")        
    ],
    "Test": [
        st.Page("RunTest.py", title= "Run Tests"),
        st.Page("ReviewTest.py", title= "Review Tests")
    ],
    "Issues": [
        st.Page("IssuesMgmt.py", title= "Issue Management"),
    ],
}

pg =st.navigation(pages,position="top")
pg.run()