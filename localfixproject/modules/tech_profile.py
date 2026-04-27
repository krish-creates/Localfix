import streamlit as st
from database import get_connection

def show_profile(tech_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Technician and their REAL Ratings
    cursor.execute("SELECT * FROM technicians WHERE id = ?", (tech_id,))
    tech = cursor.fetchone()
    
    if not tech:
        st.error("Technician details not found.")
        return

    cursor.execute("SELECT AVG(rating), COUNT(id) FROM reviews WHERE tech_id = ?", (tech_id,))
    rating_data = cursor.fetchone()
    avg_rating = round(rating_data[0], 1) if rating_data[0] else 0.0
    review_count = rating_data[1]

    # --- CSS for the Header Strip and Profile Card ---
    st.markdown(f"""
        <style>
        .profile-banner {{ background-color: #E2E8F0; height: 100px; border-radius: 15px 15px 0 0; margin-bottom: -50px; }}
        .profile-main-card {{ background: white; border: 1px solid #E2E8F0; border-radius: 15px; padding: 30px; padding-top: 60px; position: relative; }}
        .floating-icon {{ background-color: white; width: 100px; height: 100px; border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: bold; color: #2D3748; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: absolute; top: -50px; left: 30px; border: 1px solid #E2E8F0; }}
        .review-item {{ border-bottom: 1px solid #EDF2F7; padding: 15px 0; }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="profile-banner"></div>', unsafe_allow_html=True)
    
    with st.container():
        # Using a fallback for bio to prevent "None" appearing
        bio_text = tech['bio'] if tech['bio'] else "No description provided by the technician."
        
        st.markdown(f'''
            <div class="profile-main-card">
                <div class="floating-icon">{tech['name'][0] if tech['name'] else "?"}</div>
                <h1 style="margin-bottom: 0;">{tech['name']}</h1>
                <p style="color: #ECC94B; font-size: 18px;">
                    {"⭐" * int(avg_rating)} <span style="color: #718096; font-size: 14px;">{avg_rating} ({review_count} reviews)</span>
                </p>
                <div style="color: #718096; font-size: 14px; margin-bottom: 20px;">
                    📍 {tech['location']} | 🕒 {tech['years_exp']} years exp | 💰 Rs. {tech['hourly_rate']}/hr
                </div>
                <p style="color: #4A5568;">{bio_text}</p>
            </div>
        ''', unsafe_allow_html=True)

        # --- THE MISSING BUTTONS SECTION ---
        st.markdown("<br>", unsafe_allow_html=True)
        user = st.session_state['user_info']

        # Only show action buttons to regular Users
        if user['role'] == 'user':
            col1, col2, _ = st.columns([1.5, 1.5, 4])
            with col1:
                if st.button("🚀 Request Service", use_container_width=True):
                    cursor.execute("INSERT INTO requests (user_id, tech_id, status) VALUES (?, ?, ?)", 
                                   (user['id'], tech['id'], 'requested'))
                    conn.commit()
                    st.success(f"Request sent to {tech['name']}!")
            with col2:
                if st.button("💬 Send Message", use_container_width=True):
                    # Start conversation with a default message
                    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
                                   (user['id'], tech['user_id'], f"Hi {tech['name']}, I'd like to discuss a job."))
                    conn.commit()
                    st.info("Message initiated! Go to 'Messages' tab to chat.")
        
        elif user['role'] == 'admin':
            st.info("💡 Viewing as Admin. Action buttons are disabled.")
        elif user['id'] == tech['user_id']:
            st.info("👤 This is your profile. Visit the Dashboard to manage your info.")

    # --- Reviews Section ---
    st.write("---")
    st.subheader(f"Reviews ({review_count})")
    
    # Users can only review if they aren't the technician themselves
    if user['id'] != tech['user_id']:
        with st.expander("✍️ Write a Review"):
            with st.form("review_form", clear_on_submit=True):
                score = st.slider("Rating", 1, 5, 5)
                text = st.text_area("Your feedback")
                if st.form_submit_button("Submit Review"):
                    if text.strip():
                        cursor.execute("INSERT INTO reviews (tech_id, user_id, rating, comment) VALUES (?,?,?,?)",
                                       (tech['id'], user['id'], score, text))
                        conn.commit()
                        st.success("Thanks for the review!")
                        st.rerun()
                    else:
                        st.warning("Please write a comment before submitting.")

    # Display Real Reviews
    cursor.execute("""
        SELECT r.*, u.username 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.tech_id = ? 
        ORDER BY r.timestamp DESC
    """, (tech['id'],))
    all_reviews = cursor.fetchall()
    
    if not all_reviews:
        st.markdown('<div style="color: #718096; padding: 20px; border: 1px dashed #E2E8F0; border-radius: 10px; text-align: center;">No reviews yet. Be the first to review!</div>', unsafe_allow_html=True)
    else:
        for r in all_reviews:
            st.markdown(f"""
                <div class="review-item">
                    <strong>{r['username']}</strong> <span style="color: #ECC94B;">{"★" * r['rating']}</span>
                    <p style="color: #4A5568; font-size: 14px; margin-top:5px;">{r['comment']}</p>
                    <small style="color: #A0AEC0;">{r['timestamp'][:10]}</small>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Technicians", use_container_width=True):
        st.session_state['selected_tech_id'] = None
        st.rerun()

    conn.close()