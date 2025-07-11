import streamlit as st
from src.workflow import Workflow
from src.models import ResearchState, CompanyInfo

st.set_page_config(page_title="DevTool Researcher", layout="wide")
st.title("🔍 Developer Tools Research Assistant")
st.markdown("""
This app lets you **query and analyze developer-focused tools** (e.g., Firebase alternatives).
Enter your use case or tool category below, and get an automated comparison.
""")

query = st.text_input("Enter your query (e.g. Firebase alternatives, best auth providers):")

if st.button("🔎 Run Analysis"):
    # Create placeholders for progress updates
    progress_container = st.container()
    with progress_container:
        st.subheader("🔄 Research Progress")
        
        # Create placeholders for each step
        step1_placeholder = st.empty()
        step2_placeholder = st.empty()
        step3_placeholder = st.empty()
        
        # Progress bar
        progress_bar = st.progress(0)
        
    # Create workflow instance
    workflow = Workflow()
    
    # Run workflow with progress updates
    with st.spinner("Running workflow, please wait..."):
        # Step 1: Extract tools
        step1_placeholder.info("🔍 Step 1: Finding articles and extracting tools...")
        progress_bar.progress(20)
        
        result = workflow.run(query, progress_callback={
            'step1': step1_placeholder,
            'step2': step2_placeholder, 
            'step3': step3_placeholder,
            'progress_bar': progress_bar
        })
        
        progress_bar.progress(100)
        step3_placeholder.success("✅ Analysis complete!")

    # Clear progress section after completion
    progress_container.empty()
    
    # Display results
    st.subheader("📊 Research Summary")

    num_tools = len(result.companies)
    num_open_source = sum(1 for c in result.companies if c.is_open_source)
    num_with_apis = sum(1 for c in result.companies if c.api_available)
    num_free = sum(1 for c in result.companies if c.pricing_model in ["Free", "Freemium"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tools Found", num_tools)
    col2.metric("Open Source", num_open_source)
    col3.metric("With APIs", num_with_apis)
    col4.metric("Free/Freemium", num_free)

    # Recommendation above
    st.subheader("🧠 Final Recommendation")
    st.markdown(result.analysis)

    # Detailed analysis
    st.subheader("📋 Detailed Tool Analysis")
    if result.companies:
        for company in result.companies:
            with st.expander(company.name):
                st.markdown(f"**Website:** [{company.website}]({company.website})")
                st.markdown(f"**Description:** {company.description}")
                st.markdown(f"**Pricing Model:** {company.pricing_model}")
                st.markdown(f"**Open Source:** {'✅' if company.is_open_source else '❌'}")
                st.markdown(f"**API Available:** {'✅' if company.api_available else '❌'}")
                st.markdown(f"**Tech Stack:** {', '.join(company.tech_stack)}")
                st.markdown(f"**Languages Supported:** {', '.join(company.language_support)}")
                st.markdown(f"**Integrations:** {', '.join(company.integration_capabilities)}")
else:
    st.info("Enter a developer-related query and click 'Run Analysis' to start.")