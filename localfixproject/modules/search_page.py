import streamlit as st
from database import get_connection

def show_search():
    # --- Professional CSS for Search Bar and Cards ---
    st.markdown("""
        <style>
        .search-container {
            background-color: white; padding: 25px; border-radius: 15px;
            border: 1px solid #E2E8F0; margin-bottom: 30px;
        }
        .tech-card {
            background: white; border: 1px solid #E2E8F0; border-radius: 15px;
            padding: 25px; margin-bottom: 20px;
        }
        .profile-icon {
            background-color: #F7FAFC; width: 60px; height: 60px;
            border-radius: 12px; display: flex; align-items: center;
            justify-content: center; font-size: 24px; font-weight: bold;
            color: #4A5568; float: left; margin-right: 20px; border: 1px solid #E2E8F0;
        }
        .service-badge {
            background-color: #EBF8FF; color: #3182CE;
            padding: 4px 12px; border-radius: 15px;
            font-size: 12px; font-weight: 600; float: right;
        }
        .stat-text { color: #718096; font-size: 14px; margin-right: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("Find Technicians")
    st.markdown("<p style='color: #718096; margin-top:-15px;'>Browse and connect with verified service professionals</p>", unsafe_allow_html=True)

    # --- THE SEARCH BAR ---
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2.5, 2.5, 2, 1])
        
        with c1:
            loc_query = st.text_input("Location", placeholder="Enter your city (e.g. Chennai)", label_visibility="collapsed")
        with c2:
            service_list = ["Plumbing", "Electrical", "AC Repair", "Carpentry", "Painting", "Cleaning", "Appliance Repair", "Pest Control"]
            serv_query = st.selectbox("Service type", service_list, label_visibility="collapsed")
        with c3:
            sort_query = st.selectbox("Sort By", ["Highest Rated", "Most Experienced", "Lowest Price"], label_visibility="collapsed")
        with c4:
            search_clicked = st.button("🔍 Search", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- DATABASE LOGIC ---
    conn = get_connection()
    cursor = conn.cursor()
    
    # Base query
    query = """
        SELECT t.*, u.status FROM technicians t 
        JOIN users u ON t.user_id = u.id 
        WHERE u.status = 'approved' AND t.service_type = ?
    """
    params = [serv_query]

    if loc_query:
        query += " AND t.location LIKE ?"
        params.append(f"%{loc_query}%")

    # Sorting
    if sort_query == "Highest Rated":
        # We join with the average of reviews for sorting
        query = f"""
            SELECT t.*, AVG(r.rating) as avg_r 
            FROM ({query}) t
            LEFT JOIN reviews r ON t.id = r.tech_id
            GROUP BY t.id
            ORDER BY avg_r DESC
        """
    elif sort_query == "Most Experienced":
        query += " ORDER BY t.years_exp DESC"
    else:
        query += " ORDER BY t.hourly_rate ASC"

    cursor.execute(query, params)
    techs = cursor.fetchall()

    st.markdown(f"**{len(techs)} technicians found**")
    st.write("---")

    # --- THE RESULTS ---
  # --- THE RESULTS ---
    if not techs:
        st.info("No approved technicians found matching your criteria.")
    else:
        for tech in techs:
            # 1. SAFETY CHECK: If bio is None, make it an empty string
            display_bio = tech['bio'] if tech['bio'] else "No description provided."
            # Now slice the display_bio instead of tech['bio']
            short_bio = display_bio[:150] + "..." if len(display_bio) > 150 else display_bio
            
            # 2. Fetch Dynamic Ratings (Keep your existing logic here)
            cursor.execute("SELECT AVG(rating), COUNT(id) FROM reviews WHERE tech_id = ?", (tech['id'],))
            rating_res = cursor.fetchone()
            avg_val = round(rating_res[0], 1) if rating_res[0] else 0.0
            count_val = rating_res[1]
            stars = "⭐" * int(avg_val) if avg_val > 0 else "No Ratings"
            
            initial = tech['name'][0] if tech['name'] else "?"
            
            # 3. Use 'short_bio' in the HTML below
            st.markdown(f"""
                <div class="tech-card">
                    <div class="service-badge">{tech['service_type']}</div>
                    <div class="profile-icon">{initial}</div>
                    <div style="margin-left: 80px;">
                        <h3 style="margin: 0;">{tech['name']}</h3>
                        <p style="color: #ECC94B; margin: 5px 0;">
                            {stars} <span style="color: #718096; font-size:12px;">{avg_val} ({count_val} reviews)</span>
                        </p>
                        <span class="stat-text">📍 {tech['location']}</span>
                        <span class="stat-text">🕒 {tech['years_exp']} yrs exp</span>
                        <span class="stat-text">💰 Rs. {tech['hourly_rate']}/hr</span>
                        <p style="color: #4A5568; font-size: 14px; margin-top: 10px;">{short_bio}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Full Profile of {tech['name']}", key=f"btn_{tech['id']}", use_container_width=True):
                st.session_state['selected_tech_id'] = tech['id']
                st.rerun()
    
    conn.close()