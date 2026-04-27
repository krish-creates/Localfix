import streamlit as st
from database import get_connection

def show_admin():
    st.title("👑 Admin Control Panel")
    st.markdown("<p style='color: #718096; margin-top:-15px;'>Verify and manage technician profiles</p>", unsafe_allow_html=True)
    
    conn = get_connection()
    cursor = conn.cursor()

    # --- TABS: PENDING VS APPROVED ---
    tab1, tab2 = st.tabs(["🕒 Pending Approvals", "✅ Approved Technicians"])

    with tab1:
        # 1. Fetch all 'pending' technicians
        cursor.execute("""
            SELECT u.id as user_id, t.id as tech_id, t.name, t.service_type, t.location, t.years_exp, t.hourly_rate, t.bio
            FROM users u 
            JOIN technicians t ON u.id = t.user_id 
            WHERE u.status = 'pending'
        """)
        pending_techs = cursor.fetchall()

        if not pending_techs:
            st.success("✅ All technicians are verified! No pending requests.")
        else:
            st.subheader(f"Pending Approvals ({len(pending_techs)})")
            
            for tech in pending_techs:
                with st.container():
                    # Your preferred "Old Style" Card
                    st.markdown(f"""
                        <div style="background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                            <h4 style="margin:0;">{tech['name']}</h4>
                            <p style="color: #4A5568; font-size: 14px; margin: 5px 0;">
                                <b>Service:</b> {tech['service_type']} | <b>Exp:</b> {tech['years_exp']} yrs | <b>Rate:</b> Rs. {tech['hourly_rate']}/hr | <b>Loc:</b> {tech['location']}
                            </p>
                            <p style="font-size: 13px; color: #718096; line-height:1.5;">{tech['bio']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    col1, col2, _ = st.columns([1, 1, 3])
                    
                    if col1.button("✅ Approve", key=f"app_{tech['user_id']}", use_container_width=True):
                        cursor.execute("UPDATE users SET status = 'approved' WHERE id = ?", (tech['user_id'],))
                        conn.commit()
                        st.success(f"{tech['name']} is now live!")
                        st.rerun()
                    
                    if col2.button("❌ Reject", key=f"rej_{tech['user_id']}", use_container_width=True):
                        cursor.execute("DELETE FROM technicians WHERE id = ?", (tech['tech_id'],))
                        cursor.execute("DELETE FROM users WHERE id = ?", (tech['user_id'],))
                        conn.commit()
                        st.warning(f"Profile for {tech['name']} removed.")
                        st.rerun()
                st.write("---")

    with tab2:
        # 2. Fetch all 'approved' technicians
        cursor.execute("""
            SELECT u.id as user_id, t.id as tech_id, t.name, t.service_type, t.location, t.phone, t.years_exp
            FROM users u 
            JOIN technicians t ON u.id = t.user_id 
            WHERE u.status = 'approved'
        """)
        approved_techs = cursor.fetchall()

        if not approved_techs:
            st.info("No technicians have been approved yet.")
        else:
            st.subheader(f"Manage Active Pros ({len(approved_techs)})")
            
            # We'll use a clean list with Expanders for the approved section
            for tech in approved_techs:
                with st.expander(f"👤 {tech['name']} ({tech['service_type']}) - {tech['location']}"):
                    st.write(f"**Phone:** {tech['phone']}")
                    st.write(f"**Experience:** {tech['years_exp']} Years")
                    st.write(f"**System IDs:** User:{tech['user_id']} | Tech:{tech['tech_id']}")
                    
                    # Ability to revoke approval if needed
                    if st.button(f"Revoke Approval for {tech['name']}", key=f"rev_{tech['user_id']}"):
                        cursor.execute("UPDATE users SET status = 'pending' WHERE id = ?", (tech['user_id'],))
                        conn.commit()
                        st.warning("Technician moved back to pending.")
                        st.rerun()

    conn.close()