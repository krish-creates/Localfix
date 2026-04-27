import streamlit as st
import auth, database
import modules.user_portal as user_portal
import modules.admin_portal as admin_portal
import modules.tech_portal as tech_portal
import modules.search_page as search_page
import modules.tech_profile as tech_profile
import modules.messaging as messaging

# Set page to wide mode for a better "No Sidebar" look
st.set_page_config(page_title="LocalFix", page_icon="🛠️", layout="wide")

# Hide the sidebar entirely via CSS just in case
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.session_state['page'] = 'home'
    st.session_state['reg_step'] = 1 
    st.session_state['new_user_id'] = None

# --- NOT LOGGED IN AREA ---
if not st.session_state['logged_in']:
    
    if st.session_state['page'] == 'home':
        user_portal.show_landing_page()
        
        # Action Buttons at the Bottom
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Register as User", use_container_width=True):
                st.session_state['page'] = 'register_user'
                st.rerun()
        with c2:
            if st.button("Register as Technician", use_container_width=True):
                st.session_state['page'] = 'register_tech'
                st.session_state['reg_step'] = 1
                st.rerun()
        with c3:
            if st.button("Login", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()

    elif st.session_state['page'] == 'login':
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.title("🔑 Login")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sign In", use_container_width=True):
                user = auth.login_user(u, p)
                if user:
                    user_dict = dict(user) if not isinstance(user, dict) else user
                    
                    if user_dict['role'] == 'technician' and user_dict['status'] == 'pending':
                        st.error("Your profile is still being reviewed by Admin. Please check back later!")
                    else:
                        st.session_state['logged_in'] = True
                        st.session_state['user_info'] = user_dict
                        st.rerun()
                else:
                    st.error("Invalid credentials.")
            if st.button("← Back to Home"):
                st.session_state['page'] = 'home'
                st.rerun()

    elif st.session_state['page'] == 'register_tech':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state['reg_step'] == 1:
                st.title("🛠️ Tech Sign Up (Step 1/2)")
                u_reg = st.text_input("Pick Username")
                p_reg = st.text_input("Pick Password", type="password")
                
                if st.button("Next: Profile Details →", use_container_width=True):
                    # --- THE GUARD: Check if inputs are empty ---
                    if not u_reg.strip() or not p_reg.strip():
                        st.warning("Please enter both a username and a password to continue.")
                    else:
                        user_id = auth.register_user(u_reg, p_reg, 'technician')
                        if user_id:
                            st.session_state['new_user_id'] = user_id
                            st.session_state['reg_step'] = 2
                            st.rerun()
                        else:
                            st.error("This username is already taken. Please try another one.")
            
            elif st.session_state['reg_step'] == 2:
                st.title("📄 Complete Your Profile (Step 2/2)")
                st.info("Fill this info for Admin review.")
                with st.form("initial_profile"):
                    name = st.text_input("Full Name")
                    phone = st.text_input("Phone Number")
                    serv = st.selectbox("Service", ["Plumbing", "Electrical", "AC Repair", "Carpentry", "Painting", "Cleaning", "Appliance Repair", "Pest Control"])
                    loc = st.text_input("Location")
                    exp = st.number_input("Years of Exp", min_value=0)
                    rate = st.number_input("Hourly Rate ($)", min_value=0)
                    if st.form_submit_button("Submit for Admin Review"):
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO technicians (user_id, name, phone, service_type, location, years_exp, hourly_rate) VALUES (?,?,?,?,?,?,?)", 
                                       (st.session_state['new_user_id'], name, phone, serv, loc, exp, rate))
                        conn.commit()
                        conn.close()
                        st.success("✅ Profile submitted! Waiting for Admin approval.")
                
            if st.button("← Back to Home"):
                st.session_state['page'] = 'home'
                st.rerun()

    elif st.session_state['page'] == 'register_user':
        with st.columns([1, 1.5, 1])[1]:
            st.title("👤 User Sign Up")
            u_u = st.text_input("Username")
            p_u = st.text_input("Password", type="password")
            if st.button("Register & Go to Login", use_container_width=True):
                if auth.register_user(u_u, p_u, 'user'):
                    st.success("Account created! Please login.")
                    st.session_state['page'] = 'login'
                    st.rerun()
            if st.button("← Back to Home"):
                st.session_state['page'] = 'home'
                st.rerun()

# --- LOGGED IN AREA (No Sidebar) ---
else:
    user = st.session_state['user_info']
    
    # 1. TOP NAVIGATION BAR
    nav_col1, nav_col2, nav_col3 = st.columns([2, 6, 1.5])
    
    with nav_col1:
        st.markdown(f"### 🛠️ LocalFix")
    
    with nav_col2:
        # Define menu based on role
        if user['role'] == 'admin':
            menu_options = ["Admin Dashboard"]
        elif user['role'] == 'technician':
            menu_options = ["My Profile & Jobs", "Messages"]
        else: # Regular User
            menu_options = ["Find Technicians", "My Requests", "Messages"]
        
        # Horizontal Segmented Control for Navigation
        choice = st.segmented_control(
            "Navigation", 
            options=menu_options, 
            default=menu_options[0],
            label_visibility="collapsed"
        )
    
    with nav_col3:
        st.write(f"Hi, **{user['username']}**")
        if st.button("Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['page'] = 'home'
            st.rerun()

    st.markdown("---") 

    # 2. MAIN CONTENT ROUTER
    if choice == "Admin Dashboard":
        admin_portal.show_admin()
        
    elif choice == "My Profile & Jobs":
        tech_portal.show_tech_dashboard()
        
    elif choice == "Find Technicians":
        if st.session_state.get('selected_tech_id'):
            tech_profile.show_profile(st.session_state['selected_tech_id'])
        else:
            search_page.show_search()
        
    elif choice == "Messages":
        messaging.show_messages()

    elif choice == "My Requests":
        st.title("📋 My Service Requests")
        user_id = st.session_state['user_info']['id']
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # We join with technicians to see the name of who we booked
        cursor.execute("""
            SELECT r.*, t.name as tech_name, t.service_type 
            FROM requests r
            JOIN technicians t ON r.tech_id = t.id
            WHERE r.user_id = ?
            ORDER BY r.request_date DESC
        """, (user_id,))
        my_jobs = cursor.fetchall()
        
        if not my_jobs:
            st.info("You haven't requested any services yet.")
        else:
            for job in my_jobs:
                with st.container():
                    st.markdown(f"""
                        <div style="background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                            <span style="float: right; color: #3182CE; font-weight: bold;">{job['status'].upper()}</span>
                            <h4 style="margin:0;">{job['tech_name']}</h4>
                            <p style="color: #718096; font-size: 14px;">{job['service_type']} • Requested on {job['request_date'][:10]}</p>
                        </div>
                    """, unsafe_allow_html=True)
        conn.close()
