import streamlit as st


pages = {
    "Home": [
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/HomeBar/Home.py", title= "Home"),
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/HomeBar/About.py", title= "About"),
    ],
    "Requirements": [
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/Requirements/RequirementsMgmt.py", title= "Requirements Management"),
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/Requirements/RequirementsView.py", title= "View Requirements")        
    ],
    "Test": [
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/Test/RunTest.py", title= "Run Tests"),
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/Test/ReviewTest.py", title= "Review Tests")
    ],
    "Issues": [
        st.Page("/home/myintsai/Documents/syseng-toolkit/src/Issues/IssuesMgmt.py", title= "Issue Management"),
    ],
}

pg =st.navigation(pages,position="top")
pg.run()