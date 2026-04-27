import streamlit as st
from database import get_connection
import datetime

def show_messages():
    st.title("💬 Messages")
    user_id = st.session_state['user_info']['id']
    
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Sidebar/List of Conversations
    # This finds everyone you have messaged or who has messaged you
    cursor.execute("""
        SELECT DISTINCT u.id, u.username 
        FROM users u
        JOIN messages m ON (u.id = m.sender_id OR u.id = m.receiver_id)
        WHERE (m.sender_id = ? OR m.receiver_id = ?) AND u.id != ?
    """, (user_id, user_id, user_id))
    contacts = cursor.fetchall()

    if not contacts:
        st.info("No conversations yet. Start a chat from a technician's profile!")
        return

    # Create a simple contact selector
    contact_names = {c['username']: c['id'] for c in contacts}
    selected_contact_name = st.selectbox("Select a conversation", list(contact_names.keys()))
    selected_contact_id = contact_names[selected_contact_name]

    # 2. The Chat History (CSS Styling)
    st.markdown("""
        <style>
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 70%;
            font-size: 14px;
        }
        .sent {
            background-color: #2D3748;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 2px;
        }
        .received {
            background-color: #E2E8F0;
            color: #2D3748;
            margin-right: auto;
            border-bottom-left-radius: 2px;
        }
        .timestamp {
            font-size: 10px;
            color: #A0AEC0;
            margin-top: 5px;
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    # Fetch messages between these two people
    cursor.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
        OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (user_id, selected_contact_id, selected_contact_id, user_id))
    chat_history = cursor.fetchall()

    # Display Chat
    chat_container = st.container(height=400)
    with chat_container:
        for msg in chat_history:
            msg_class = "sent" if msg['sender_id'] == user_id else "received"
            st.markdown(f"""
                <div class="chat-bubble {msg_class}">
                    {msg['content']}
                    <span class="timestamp">{msg['timestamp']}</span>
                </div>
            """, unsafe_allow_html=True)

    # 3. Send Message Input
    with st.form("send_msg", clear_on_submit=True):
        new_msg = st.text_input("Type your message...", placeholder=f"Chatting with {selected_contact_name}")
        if st.form_submit_button("Send ✈️"):
            if new_msg:
                cursor.execute("""
                    INSERT INTO messages (sender_id, receiver_id, content) 
                    VALUES (?, ?, ?)
                """, (user_id, selected_contact_id, new_msg))
                conn.commit()
                st.rerun()

    conn.close()