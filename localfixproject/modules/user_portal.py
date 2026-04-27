import streamlit as st

def show_landing_page():
    # 1. Enhanced CSS for the Dark Box and Clean Grid
    st.markdown("""
        <style>
        .big-title { font-size: 50px !important; font-weight: 800 !important; color: #1A1C1E; text-align: center; margin-bottom: 10px; }
        .sub-text { font-size: 18px !important; color: #5F6368; text-align: center; margin-bottom: 40px; }
        
        /* The Dark Technician Box */
        .tech-box {
            background-color: #2D3748;
            color: white;
            padding: 50px;
            border-radius: 20px;
            text-align: center;
            margin-top: 50px;
        }
        .tech-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.1);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin: 5px;
        }
        
        /* Service Card (No Button) */
        .service-card {
            background-color: white;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            transition: 0.3s;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Hero Section
    st.markdown('<p class="big-title">Find Reliable Local<br>Technicians Near You</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Connect with verified plumbers, electricians, and more.</p>', unsafe_allow_html=True)

    # 3. Services Grid (JUST VISUALS)
    st.markdown("<h2 style='text-align: center;'>Our Services</h2>", unsafe_allow_html=True)
    services = [
        {"name": "Plumbing", "icon": "💧"}, {"name": "Electrical", "icon": "⚡"},
        {"name": "AC Repair", "icon": "❄️"}, {"name": "Carpentry", "icon": "🔨"},
        {"name": "Painting", "icon": "🎨"}, {"name": "Cleaning", "icon": "✨"},
        {"name": "Appliance Repair", "icon": "⚙️"}, {"name": "Pest Control", "icon": "🕷️"}
    ]

    for i in range(0, len(services), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(services):
                s = services[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div class="service-card">
                            <div style="font-size: 40px;">{s['icon']}</div>
                            <div style="font-weight: 600; margin-top:10px;">{s['name']}</div>
                        </div>
                    """, unsafe_allow_html=True)

    # 4. The "Are You a Technician?" Section (Matching your Image)
    st.markdown("""
        <div class="tech-box">
            <h2 style="color: white;">Are You a Technician?</h2>
            <p style="color: #CBD5E0;">Join LocalFix to grow your business. Get discovered by customers in your area.</p>
            <div style="margin: 20px 0;">
                <span class="tech-badge">✅ Verified profile badge</span>
                <span class="tech-badge">✅ Direct customer messages</span>
                <span class="tech-badge">✅ Build your reputation</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    '''# Find the buttons at the bottom of show_landing_page()
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Register as Technician →", key="reg_tech_btn"):
            st.session_state['page'] = 'register'
            st.session_state['temp_role'] = 'technician'
            st.rerun()
    with btn_col2:
        if st.button("Register as User →", key="reg_user_btn"):
            st.session_state['page'] = 'register'
            st.session_state['temp_role'] = 'user'
            st.rerun()'''