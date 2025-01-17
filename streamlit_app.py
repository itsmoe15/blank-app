import streamlit as st
import pandas as pd
import requests
import base64
from streamlit_autorefresh import st_autorefresh

# Initialize session state for login and solved tracking
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_solved' not in st.session_state:
    st.session_state.current_solved = set()

# Login Page
if not st.session_state.logged_in:
    st.title("Login")
    handle_input = st.text_input("Enter your Codeforces handle:")
    if st.button("Login"):
        user_url = f"https://codeforces.com/api/user.info?handles={handle_input}"
        resp = requests.get(user_url)
        if resp.ok and resp.json().get("status") == "OK":
            st.session_state.logged_in = True
            st.session_state.handle = handle_input
            st.session_state.user_info = resp.json()["result"][0]
            st.success("Logged in successfully!")
        else:
            st.error("Handle not found. Please try again.")
    
    # Only stop if still not logged in
    if not st.session_state.logged_in:
        st.stop()

# Second Page: After login
user_info = st.session_state.user_info
st.title(f"Welcome, {user_info.get('firstName', user_info.get('handle', ''))}! 💙")

col1, col2 = st.columns([1, 3])
with col1:
    # Display profile picture if available
    if user_info.get("titlePhoto"):
        st.image(f"{user_info.get('titlePhoto')}", width=500)

with col2:
    st.write(f"**Country:** {user_info.get('country', 'N/A')}")
    st.write(f"**City:** {user_info.get('city', 'N/A')}")
    st.write(f"**Organization:** {user_info.get('organization', 'N/A')}")
    st.write(f"**Rating:** {user_info.get('rating', 'N/A')}")
    st.write(f"**Rank:** {user_info.get('rank', 'N/A')}")

# Set up periodic refresh every 60 seconds for dynamic updates
st_autorefresh(interval=60000, key="refresh")

# Load problems data
df = pd.read_csv('problems.csv')
if 'tags' not in df.columns:
    df['tags'] = ""

# Extract unique tags from the CSV for filtering options
all_tags = set()
for tags in df['tags'].dropna():
    for tag in tags.split(','):
        cleaned_tag = tag.strip()
        if cleaned_tag:
            all_tags.add(cleaned_tag)
all_tags = sorted(list(all_tags))

# Multiselect widget for tag selection
selected_tags = st.multiselect(
    "Select tags to filter problems:",
    all_tags,
    default=all_tags
)

# Filter problems based on selected tags
if selected_tags:
    def has_selected_tags(row_tags):
        row_tags_list = [t.strip() for t in str(row_tags).split(',') if t.strip()]
        return any(tag in row_tags_list for tag in selected_tags)
    filtered_df = df[df['tags'].apply(has_selected_tags)]
else:
    filtered_df = df.copy()

# Use the filtered DataFrame for further operations
df_to_use = filtered_df.copy()

# Fetch user submissions from Codeforces API
handle = st.session_state.handle
url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=100000"
response = requests.get(url)
solved = set()
attempted = set()

if response.ok:
    submissions = response.json().get('result', [])
    for submission in submissions:
        problem = submission.get('problem', {})
        contestId = problem.get('contestId')
        index = problem.get('index')
        if contestId and index:
            key = (contestId, index)
            attempted.add(key)
            if submission.get('verdict') == 'OK':
                solved.add(key)
else:
    st.error("Failed to fetch data from Codeforces API")

latest_solved = solved.copy()
new_solves = latest_solved - st.session_state.current_solved

# Filter new solves to those within the filtered problem list
df_keys = set(zip(df_to_use['contestId'], df_to_use['index']))
new_site_solves = new_solves.intersection(df_keys)

for contestId, index in new_site_solves:
    matching = df_to_use[(df_to_use['contestId'] == contestId) & (df_to_use['index'] == index)]
    problem_title = matching.iloc[0]['title'] if not matching.empty else f"{contestId}-{index}"
    st.balloons()
    try:
        with open('celebration.mp3', "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode()
        audio_tag = f"""
        <audio autoplay style="display:none">
            <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_tag, unsafe_allow_html=True)
    except Exception:
        st.warning("Audio file not found or failed to play.")
    try:
        st.toast(f"Well done on solving problem {problem_title} :D keep it up")
    except Exception:
        st.success(f"Well done on solving problem {problem_title} :D keep it up")

st.session_state.current_solved = latest_solved

st.write(f"Problems List for user: {handle}")

# Table headers
header_cols = st.columns([0.5, 0.5, 3, 1, 1])
header_cols[0].markdown("**#**")
header_cols[1].markdown("**Status**")
header_cols[2].markdown("**Title**")
header_cols[3].markdown("**Problem Level**")
header_cols[4].markdown("**Problem Difficulty**")

# Display each problem row
for idx, (_, row) in enumerate(df_to_use.iterrows(), start=1):
    contestId = row['contestId']
    index_val = row['index']
    title = row['title']
    level = row['problem level']
    difficulty = row['problem difficulty']

    key = (contestId, index_val)

    # Determine status emoji
    if key in solved:
        emoji = "✅"
    elif key in attempted:
        emoji = "❌"
    else:
        emoji = "⚪"

    cols = st.columns([0.5, 0.5, 3, 1, 1])
    cols[0].write(idx)
    cols[1].write(emoji)

    # Hyperlink for problem title, highlighted if solved
    problem_url = f"https://codeforces.com/contest/{contestId}/problem/{index_val}"
    if key in solved:
        title_markdown = f"<span style='color:green'><a href='{problem_url}' target='_blank'>{title}</a></span>"
    else:
        title_markdown = f"<a href='{problem_url}' target='_blank'>{title}</a>"
    cols[2].markdown(title_markdown, unsafe_allow_html=True)

    if key in solved:
        cols[3].markdown(f"<span style='color:green'>{level}</span>", unsafe_allow_html=True)
        cols[4].markdown(f"<span style='color:green'>{difficulty}</span>", unsafe_allow_html=True)
    else:
        cols[3].write(level)
        cols[4].write(difficulty)
