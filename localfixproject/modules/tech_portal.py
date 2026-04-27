import streamlit as st
from database import get_connection

def show_tech_dashboard():
    user_id = st.session_state['user_info']['id']
    status = st.session_state['user_info']['status']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Technician Details
    cursor.execute("SELECT * FROM technicians WHERE user_id = ?", (user_id,))
    tech_data = cursor.fetchone() # Changed from tech_row to tech_data for consistency

    # 2. Initialize req_count so it doesn't crash for new users
    req_count = 0
    if tech_data:
        my_tech_id = tech_data['id']
        # COUNT USING THE TECH ID
        cursor.execute("SELECT COUNT(*) as count FROM requests WHERE tech_id = ?", (my_tech_id,))
        req_count = cursor.fetchone()['count']

    # --- CSS Styling ---
    st.markdown("""
        <style>
        .main-header { font-size: 32px; font-weight: 700; margin-bottom: 5px; }
        .sub-header { color: #666; margin-bottom: 20px; }
        .status-badge {
            background-color: #FEF3C7; color: #92400E;
            padding: 5px 12px; border-radius: 15px;
            font-size: 14px; font-weight: 600; float: right;
        }
        .profile-card {
            background: white; border: 1px solid #E2E8F0;
            border-radius: 15px; padding: 30px; margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        }
        .warning-box {
            background-color: #FFFBEB; border: 1px solid #FEF3C7;
            color: #92400E; padding: 15px; border-radius: 10px;
            margin-bottom: 25px; font-size: 14px; display: flex; align-items: center;
        }
        .request-item {
            border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Dashboard Header
    st.markdown(f'<span class="status-badge">🕒 {status.capitalize()}</span>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">Technician Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage your profile and service requests</div>', unsafe_allow_html=True)

    # TABS (Using the safe req_count)
    tab1, tab2 = st.tabs(["👤 My Profile", f"📋 Service Requests ({req_count})"])

    with tab1:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.subheader("Service Profile")
        
        if status == 'pending':
            st.markdown('<div class="warning-box">⚠️ Your profile is pending admin approval. Customers cannot see you yet.</div>', unsafe_allow_html=True)

        with st.form("tech_update_form"):
            col1, col2 = st.columns(2)
            # Use tech_data here
            name = col1.text_input("Full Name", value=tech_data['name'] if tech_data else "")
            phone = col2.text_input("Phone Number", value=tech_data['phone'] if tech_data else "")
            
            col3, col4 = st.columns(2)
            service_list = ["Plumbing", "Electrical", "AC Repair", "Carpentry", "Painting", "Cleaning", "Appliance Repair", "Pest Control"]
            current_service = tech_data['service_type'] if tech_data else "Plumbing"
            service = col3.selectbox("Service Type", service_list, index=service_list.index(current_service) if tech_data and current_service in service_list else 0)
            location = col4.text_input("Location (City/Area)", value=tech_data['location'] if tech_data else "")
            
            col5, col6 = st.columns(2)
            exp = col5.number_input("Years of Experience", min_value=0, step=1, value=int(tech_data['years_exp']) if tech_data and tech_data['years_exp'] else 0)
            rate = col6.number_input("Hourly Rate (Rs.)", min_value=0.0, step=1.0, value=float(tech_data['hourly_rate']) if tech_data and tech_data['hourly_rate'] else 0.0)
            
            desc = st.text_area("Description", value=tech_data['bio'] if tech_data else "", placeholder="Describe your services and expertise...")
            
            submitted = st.form_submit_button("💾 Update Profile")
            
            if submitted:
                if tech_data:
                    cursor.execute("""
                        UPDATE technicians 
                        SET name=?, phone=?, service_type=?, location=?, years_exp=?, hourly_rate=?, bio=? 
                        WHERE user_id=?
                    """, (name, phone, service, location, exp, rate, desc, user_id))
                else:
                    cursor.execute("""
                        INSERT INTO technicians (user_id, name, phone, service_type, location, years_exp, hourly_rate, bio) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, name, phone, service, location, exp, rate, desc))
                
                conn.commit()
                st.success("Profile saved!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Incoming Job Requests")
        if not tech_data:
            st.warning("Please complete your profile first.")
        else:
            cursor.execute("""
                SELECT r.*, u.username as customer_name 
                FROM requests r
                JOIN users u ON r.user_id = u.id
                WHERE r.tech_id = ?
                ORDER BY r.request_date DESC
            """, (tech_data['id'],))
            incoming = cursor.fetchall()

            if not incoming:
                st.info("No active service requests at the moment.")
            else:
                for req in incoming:
                    with st.container():
                        st.markdown(f"""
                            <div class="request-item">
                                <strong>Customer:</strong> {req['customer_name']}<br>
                                <strong>Status:</strong> {req['status'].upper()}<br>
                                <small>Requested on: {req['request_date']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if req['status'] == 'requested':
                            if st.button(f"Accept Request from {req['customer_name']}", key=f"acc_{req['id']}"):
                                cursor.execute("UPDATE requests SET status = 'accepted' WHERE id = ?", (req['id'],))
                                conn.commit()
                                st.success("Job Accepted!")
                                st.rerun()

    conn.close()