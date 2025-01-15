import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------------------------
# Initialize Session State
# ------------------------------
if 'member_count' not in st.session_state:
    st.session_state.member_count = 0

# ------------------------------
# App Title and Description
# ------------------------------
st.title("🎉 Hackathon Team Registration")

st.write(
    """
    Welcome to the Hackathon! Please fill out the form below to register your team.
    For any queries, contact us at [email@example.com](mailto:email@example.com).
    """
)

# ------------------------------
# Define CSV File and Columns
# ------------------------------
REGISTRATIONS_FILE = "registrations.csv"

CSV_COLUMNS = [
    "Timestamp",
    "Team Name",
    "Team Leader Name",
    "Team Leader Email",
    "Team Leader Phone",
    "Team Leader Uni ID",
    "Member 1 Name",
    "Member 1 Phone",
    "Member 1 Uni ID",
    "Member 2 Name",
    "Member 2 Phone",
    "Member 2 Uni ID",
    "Member 3 Name",
    "Member 3 Phone",
    "Member 3 Uni ID",
    "Member 4 Name",
    "Member 4 Phone",
    "Member 4 Uni ID",
    "Member 5 Name",
    "Member 5 Phone",
    "Member 5 Uni ID",
]

# ------------------------------
# Function to Load Existing Registrations
# ------------------------------
def load_registrations(file_path):
    if os.path.exists(file_path):
        if os.path.getsize(file_path) > 0:
            try:
                return pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                st.warning("Registration file is empty. Initializing with headers.")
                return pd.DataFrame(columns=CSV_COLUMNS)
        else:
            st.info("Registration file is empty. Initializing with headers.")
            return pd.DataFrame(columns=CSV_COLUMNS)
    else:
        # If file doesn't exist, create it with headers
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(file_path, index=False)
        return df

# ------------------------------
# Function to Save Registration
# ------------------------------
def save_registration(file_path, data):
    new_entry = pd.DataFrame([data])
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            existing_df = pd.read_csv(file_path)
            # Concatenate the existing DataFrame with the new entry
            updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
        except pd.errors.EmptyDataError:
            st.warning("Registration file is empty. Initializing with headers.")
            updated_df = new_entry
    else:
        updated_df = new_entry
    
    # Save the updated DataFrame back to CSV
    updated_df.to_csv(file_path, index=False)

# ------------------------------
# Function to Add Team Member
# ------------------------------
def add_member():
    if st.session_state.member_count < 4:
        st.session_state.member_count += 1
    else:
        st.warning("Maximum of 5 team members reached.")

st.button("➕ Add Team Member", on_click=add_member)
# ------------------------------
# Registration Form
# ------------------------------
with st.form("registration_form"):
    st.header("Team Information")
    
    team_name = st.text_input("Team Name", max_chars=50)
    
    st.subheader("Team Leader Information")
    leader_name = st.text_input("Team Leader Name", max_chars=50)
    leader_email = st.text_input("Team Leader Email", max_chars=50)
    leader_phone = st.text_input("Team Leader Phone Number", max_chars=11)
    leader_uni_id = st.text_input("Team Leader University ID", max_chars=7)
    
    st.subheader("Team Members (Optional)")

    member_data = []
    for i in range(1, st.session_state.member_count +1):
        st.markdown(f"**Member {i}**")
        member_name = st.text_input(f"Member {i} Name", key=f"member_{i}_name", max_chars=50)
        member_phone = st.text_input(f"Member {i} Phone Number", key=f"member_{i}_phone", max_chars=11)
        member_uni_id = st.text_input(f"Member {i} University ID", key=f"member_{i}_uni_id", max_chars=7)
        member_data.append({
            f"Member {i} Name": member_name.strip(),
            f"Member {i} Phone": member_phone.strip(),
            f"Member {i} Uni ID": member_uni_id.strip(),
        })
        st.markdown("---")
    
    # "Register Team" button
    submitted = st.form_submit_button("Register Team")
    
    if submitted:
        # Input Validation
        if not team_name.strip():
            st.error("Please provide a Team Name.")
        elif not leader_name.strip():
            st.error("Please provide the Team Leader's Name.")
        elif not leader_email.strip():
            st.error("Please provide the Team Leader's Email.")
        elif not leader_phone.strip():
            st.error("Please provide the Team Leader's Phone Number.")
        elif not leader_uni_id.strip():
            st.error("Please provide the Team Leader's University ID.")
        else:
            # Check for unique team name
            registrations = load_registrations(REGISTRATIONS_FILE)
            if not registrations.empty and team_name.strip().lower() in registrations["Team Name"].str.lower().values:
                st.error("This Team Name is already taken. Please choose a different name.")
            else:
                # Prepare registration data
                registration_data = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Team Name": team_name.strip(),
                    "Team Leader Name": leader_name.strip(),
                    "Team Leader Email": leader_email.strip(),
                    "Team Leader Phone": leader_phone.strip(),
                    "Team Leader Uni ID": leader_uni_id.strip(),
                }
                
                # Add member data
                for member in member_data:
                    registration_data.update(member)
                
                # Fill empty member slots with empty strings
                for i in range(len(member_data)+1, 6):
                    registration_data[f"Member {i} Name"] = ""
                    registration_data[f"Member {i} Phone"] = ""
                    registration_data[f"Member {i} Uni ID"] = ""
                
                # Save to CSV
                save_registration(REGISTRATIONS_FILE, registration_data)
                st.success("Team registered successfully!")
                
                # Reset member_count
                st.session_state.member_count =0

# ------------------------------
# "Add Team Member" Button
# ------------------------------


# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.write("© 2025 Hackathon Committee. All rights reserved.")
