import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from email_bot_database import EmailBotDatabase
import os

# Page configuration
st.set_page_config(
    page_title="Email Understanding & Action Bot",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = EmailBotDatabase()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    .email-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-success { background-color: #d1fae5; color: #065f46; }
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .status-error { background-color: #fee2e2; color: #991b1b; }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state"""
    if 'api_base_url' not in st.session_state:
        st.session_state.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')

def make_api_request(endpoint, method='GET', data=None):
    """Make API request"""
    try:
        url = f"{st.session_state.api_base_url}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def dashboard_tab():
    """Dashboard tab"""
    st.markdown('<h2 class="section-header">Dashboard</h2>', unsafe_allow_html=True)
    
    # Get statistics
    stats = db.get_statistics()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", stats.get('total_emails', 0))
    
    with col2:
        st.metric("Processed", stats.get('processed_emails', 0))
    
    with col3:
        st.metric("Classifications", stats.get('total_classifications', 0))
    
    with col4:
        st.metric("Actions", stats.get('total_actions', 0))
    
    st.markdown("---")
    
    # Actions by status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Actions by Status")
        actions_by_status = stats.get('actions_by_status', {})
        if actions_by_status:
            df_status = pd.DataFrame(list(actions_by_status.items()), columns=['Status', 'Count'])
            st.bar_chart(df_status.set_index('Status'))
        else:
            st.info("No actions yet")
    
    with col2:
        st.subheader("Classifications by Category")
        classifications_by_category = stats.get('classifications_by_category', {})
        if classifications_by_category:
            df_cat = pd.DataFrame(list(classifications_by_category.items()), columns=['Category', 'Count'])
            st.bar_chart(df_cat.set_index('Category'))
        else:
            st.info("No classifications yet")

def emails_tab():
    """Emails tab"""
    st.markdown('<h2 class="section-header">Emails</h2>', unsafe_allow_html=True)
    
    # Process new emails button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Process Unread Emails", type="primary"):
            with st.spinner("Processing emails..."):
                result = make_api_request("/emails/process", method='POST', data={"auto_execute": False})
                if result:
                    st.success(f"Processed {len(result.get('results', []))} emails")
                    st.rerun()
    
    st.markdown("---")
    
    # Get emails
    emails = db.get_emails_with_classifications(limit=50)
    
    if not emails:
        st.info("No emails processed yet. Click 'Process Unread Emails' to start.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set([e.get('category_name', '') for e in emails if e.get('category_name')])))
    with col2:
        filter_status = st.selectbox("Filter by Action Status", ["All", "pending", "success", "error"])
    with col3:
        search_term = st.text_input("Search", placeholder="Search subject or sender...")
    
    # Filter emails
    filtered_emails = emails
    if filter_category != "All":
        filtered_emails = [e for e in filtered_emails if e.get('category_name') == filter_category]
    if filter_status != "All":
        filtered_emails = [e for e in filtered_emails if e.get('action_status') == filter_status]
    if search_term:
        filtered_emails = [e for e in filtered_emails 
                          if search_term.lower() in e.get('subject', '').lower() 
                          or search_term.lower() in e.get('sender', '').lower()]
    
    st.markdown(f"**Showing {len(filtered_emails)} of {len(emails)} emails**")
    st.markdown("---")
    
    # Display emails
    for email in filtered_emails:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {email.get('subject', 'No Subject')}")
                st.markdown(f"**From:** {email.get('sender', 'Unknown')} | **Date:** {email.get('received_at', 'N/A')[:19]}")
                
                if email.get('category_name'):
                    st.markdown(f"**Category:** {email.get('category_name')} (Confidence: {email.get('confidence', 0):.1%})")
                    st.markdown(f"**Justification:** {email.get('justification', 'N/A')}")
                
                # Show body preview
                body = email.get('body', '')
                if body:
                    with st.expander("View Email Body"):
                        st.text(body[:500] + "..." if len(body) > 500 else body)
            
            with col2:
                action_status = email.get('action_status', 'pending')
                status_color = {
                    'success': 'status-success',
                    'pending': 'status-pending',
                    'error': 'status-error'
                }.get(action_status, 'status-pending')
                
                st.markdown(f'<span class="status-badge {status_color}">{action_status.upper()}</span>', unsafe_allow_html=True)
                
                if action_status == 'pending' and email.get('id'):
                    if st.button("Execute Action", key=f"execute_{email.get('id')}"):
                        # Get action ID
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('SELECT id FROM actions WHERE email_id = ? AND status = ?', 
                                     (email.get('id'), 'pending'))
                        action_row = cursor.fetchone()
                        conn.close()
                        
                        if action_row:
                            action_id = action_row[0]
                            with st.spinner("Executing action..."):
                                result = make_api_request(f"/actions/{action_id}/execute", method='POST')
                                if result:
                                    st.success("Action executed successfully!")
                                    st.rerun()
            
            st.markdown("---")

def actions_tab():
    """Actions tab"""
    st.markdown('<h2 class="section-header">Actions</h2>', unsafe_allow_html=True)
    
    # Get actions
    result = make_api_request("/actions?limit=100")
    if not result:
        st.error("Failed to load actions")
        return
    
    actions = result.get('actions', [])
    
    if not actions:
        st.info("No actions yet")
        return
    
    # Filter by status
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "success", "error", "executing"])
    
    filtered_actions = actions
    if status_filter != "All":
        filtered_actions = [a for a in actions if a.get('status') == status_filter]
    
    st.markdown(f"**Showing {len(filtered_actions)} of {len(actions)} actions**")
    st.markdown("---")
    
    # Display actions
    for action in filtered_actions:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {action.get('action_name', 'Unknown Action')}")
                st.markdown(f"**Email:** {action.get('subject', 'N/A')}")
                st.markdown(f"**Type:** {action.get('action_type', 'N/A')} | **Target:** {action.get('target', 'N/A')}")
            
            with col2:
                status = action.get('status', 'pending')
                status_color = {
                    'success': 'status-success',
                    'pending': 'status-pending',
                    'error': 'status-error',
                    'executing': 'status-pending'
                }.get(status, 'status-pending')
                
                st.markdown(f'<span class="status-badge {status_color}">{status.upper()}</span>', unsafe_allow_html=True)
            
            with col3:
                if status == 'pending':
                    if st.button("Execute", key=f"exec_{action.get('id')}"):
                        with st.spinner("Executing..."):
                            result = make_api_request(f"/actions/{action.get('id')}/execute", method='POST')
                            if result:
                                st.success("Action executed!")
                                st.rerun()
            
            if action.get('result'):
                st.info(f"**Result:** {action.get('result')}")
            if action.get('error_message'):
                st.error(f"**Error:** {action.get('error_message')}")
            
            st.markdown("---")

def categories_tab():
    """Categories tab"""
    st.markdown('<h2 class="section-header">Categories</h2>', unsafe_allow_html=True)
    
    # Get categories
    categories = db.get_all_categories()
    
    # Display categories
    for category in categories:
        with st.expander(f"{category['name']} - {category['action_type']}"):
            st.markdown(f"**Description:** {category.get('description', 'N/A')}")
            st.markdown(f"**Keywords:** {category.get('keywords', 'N/A')}")
            st.markdown(f"**Action Type:** {category.get('action_type', 'N/A')}")
            st.markdown(f"**Target:** {category.get('target', 'N/A')}")
            st.markdown(f"**Active:** {'Yes' if category.get('is_active') else 'No'}")
    
    st.markdown("---")
    
    # Add new category
    st.subheader("Add New Category")
    with st.form("new_category_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Category Name")
            new_description = st.text_area("Description")
            new_keywords = st.text_input("Keywords (comma-separated)")
        with col2:
            new_action_type = st.selectbox("Action Type", 
                ["forward", "update_hr", "add_calendar", "create_ticket", "auto_reply", "notify_slack", "log_to_sheets"])
            new_target = st.text_input("Target")
            new_active = st.checkbox("Active", value=True)
        
        if st.form_submit_button("Create Category"):
            if new_name and new_action_type:
                result = make_api_request("/categories", method='POST', data={
                    "name": new_name,
                    "description": new_description,
                    "keywords": new_keywords,
                    "action_type": new_action_type,
                    "target": new_target,
                    "is_active": new_active
                })
                if result:
                    st.success("Category created successfully!")
                    st.rerun()
            else:
                st.error("Please fill in required fields")

def settings_tab():
    """Settings tab"""
    st.markdown('<h2 class="section-header">Settings</h2>', unsafe_allow_html=True)
    
    # API Configuration
    st.subheader("API Configuration")
    api_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
    if st.button("Save API URL"):
        st.session_state.api_base_url = api_url
        st.success("API URL saved")
    
    st.markdown("---")
    
    # OpenAI Configuration
    st.subheader("OpenAI Configuration")
    openai_key = st.text_input("OpenAI API Key", value=st.session_state.openai_api_key, type="password")
    if st.button("Save OpenAI Key"):
        st.session_state.openai_api_key = openai_key
        os.environ['OPENAI_API_KEY'] = openai_key
        st.success("OpenAI API key saved")
    
    st.markdown("---")
    
    # Gmail Configuration
    st.subheader("Gmail Configuration")
    st.info("To use Gmail integration, you need to:")
    st.markdown("""
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select existing one
    3. Enable Gmail API
    4. Create OAuth 2.0 credentials
    5. Download credentials.json and place it in the project root
    """)
    
    st.markdown("---")
    
    # Slack Configuration
    st.subheader("Slack Configuration")
    slack_webhook = st.text_input("Slack Webhook URL", value=db.get_config('slack_webhook_url') or '')
    if st.button("Save Slack Webhook"):
        db.set_config('slack_webhook_url', slack_webhook)
        st.success("Slack webhook saved")
    
    st.markdown("---")
    
    # Google Sheets Configuration
    st.subheader("Google Sheets Configuration")
    sheets_id = st.text_input("Google Sheets Spreadsheet ID", value=db.get_config('sheets_spreadsheet_id') or '')
    if st.button("Save Sheets ID"):
        db.set_config('sheets_spreadsheet_id', sheets_id)
        st.success("Sheets ID saved")
    
    st.markdown("---")
    
    # Processing Settings
    st.subheader("Processing Settings")
    auto_execute = st.checkbox("Auto-execute actions", value=False)
    poll_interval = st.number_input("Polling Interval (seconds)", min_value=60, value=300, step=60)
    
    if st.button("Save Processing Settings"):
        db.set_config('auto_execute_actions', str(auto_execute))
        db.set_config('gmail_poll_interval', str(poll_interval))
        st.success("Settings saved")

def main():
    init_session_state()
    
    st.markdown('<h1 class="main-header">📧 Email Understanding & Action Bot</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select Page", 
            ["Dashboard", "Emails", "Actions", "Categories", "Settings"],
            label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        stats = db.get_statistics()
        st.metric("Total Emails", stats.get('total_emails', 0))
        st.metric("Pending Actions", stats.get('actions_by_status', {}).get('pending', 0))
    
    # Route to appropriate page
    if page == "Dashboard":
        dashboard_tab()
    elif page == "Emails":
        emails_tab()
    elif page == "Actions":
        actions_tab()
    elif page == "Categories":
        categories_tab()
    elif page == "Settings":
        settings_tab()

if __name__ == "__main__":
    main()

