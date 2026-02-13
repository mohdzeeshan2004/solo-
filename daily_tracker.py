import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import math

# Set page config
st.set_page_config(
    page_title="Daily Tracker - Leveling System",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .level-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .rank-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .season-container {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 5px 0;
    }
    .task-completed {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .task-pending {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "current_season": 1,
        "level": 1,
        "experience": 0,
        "exp_needed": 100,
        "rank": "BRONZE",
        "rank_points": 0,
        "daily_tasks": [
            {"id": 1, "name": "Morning Exercise", "difficulty": "common", "exp": 10},
            {"id": 2, "name": "Read Book", "difficulty": "common", "exp": 10},
            {"id": 3, "name": "Meditate", "difficulty": "common", "exp": 15},
            {"id": 4, "name": "Complete Project", "difficulty": "rare", "exp": 50},
            {"id": 5, "name": "Learn New Skill", "difficulty": "epic", "exp": 75},
        ],
        "completion_history": {}
    }

# Rank system (similar to PUBG)
RANK_SYSTEM = [
    {"rank": "BRONZE", "min_points": 0, "color": "#CD7F32"},
    {"rank": "SILVER", "min_points": 100, "color": "#C0C0C0"},
    {"rank": "GOLD", "min_points": 250, "color": "#FFD700"},
    {"rank": "PLATINUM", "min_points": 500, "color": "#E5E4E2"},
    {"rank": "DIAMOND", "min_points": 1000, "color": "#B9F2FF"},
    {"rank": "MASTER", "min_points": 2000, "color": "#8B0000"},
    {"rank": "GRANDMASTER", "min_points": 3500, "color": "#FFD700"},
    {"rank": "LEGEND", "min_points": 5000, "color": "#FF6347"},
]

DIFFICULTY_COLORS = {
    "common": "#95a5a6",
    "rare": "#3498db",
    "epic": "#9b59b6",
    "legendary": "#f39c12"
}

DIFFICULTY_EXP = {
    "common": 1,
    "rare": 1.5,
    "epic": 2.5,
    "legendary": 5
}

# Season info
SEASONS = {
    1: {"name": "The Awakening", "start_date": "Jan 1", "end_date": "Mar 31"},
    2: {"name": "Rise of Power", "start_date": "Apr 1", "end_date": "Jun 30"},
    3: {"name": "Dark Shadow", "start_date": "Jul 1", "end_date": "Sep 30"},
    4: {"name": "Eternal Destiny", "start_date": "Oct 1", "end_date": "Dec 31"},
}

def get_current_rank(rank_points):
    """Get current rank based on rank points"""
    for i in range(len(RANK_SYSTEM) - 1, -1, -1):
        if rank_points >= RANK_SYSTEM[i]["min_points"]:
            return RANK_SYSTEM[i]
    return RANK_SYSTEM[0]

def get_exp_needed_for_level(level):
    """Calculate EXP needed to reach next level (scales with level)"""
    return 100 + (level - 1) * 50

def add_experience(exp_amount):
    """Add experience and handle level up"""
    user = st.session_state.user_data
    user["experience"] += exp_amount
    
    while user["experience"] >= user["exp_needed"]:
        user["experience"] -= user["exp_needed"]
        user["level"] += 1
        user["rank_points"] += 10  # Bonus rank points per level up
        user["exp_needed"] = get_exp_needed_for_level(user["level"])
    
    # Update rank
    new_rank = get_current_rank(user["rank_points"])
    user["rank"] = new_rank["rank"]

def get_today_key():
    """Get today's date as key"""
    return datetime.now().strftime("%Y-%m-%d")

def mark_task_complete(task_id):
    """Mark a task as complete for today"""
    today = get_today_key()
    
    if today not in st.session_state.user_data["completion_history"]:
        st.session_state.user_data["completion_history"][today] = []
    
    # Find task and add experience
    for task in st.session_state.user_data["daily_tasks"]:
        if task["id"] == task_id:
            exp_earned = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
            add_experience(int(exp_earned))
            st.session_state.user_data["completion_history"][today].append(task_id)
            st.session_state.user_data["rank_points"] += 5
            break

def get_today_completed():
    """Get completed tasks for today"""
    today = get_today_key()
    return st.session_state.user_data["completion_history"].get(today, [])

def get_completion_streak():
    """Calculate current completion streak"""
    today = datetime.now()
    streak = 0
    
    for i in range(100):
        check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if check_date in st.session_state.user_data["completion_history"]:
            if len(st.session_state.user_data["completion_history"][check_date]) > 0:
                streak += 1
            else:
                break
        else:
            break
    
    return streak

# Sidebar Navigation
st.sidebar.title("⚔️ Daily Tracker")
page = st.sidebar.radio("Navigation", ["Dashboard", "Daily Quests", "Statistics", "Settings"])

# Main Header
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.markdown(f"""
    <div class='level-container'>
        <h2>⚔️ LEVEL {st.session_state.user_data['level']}</h2>
        <p>Experience: {st.session_state.user_data['experience']}/{st.session_state.user_data['exp_needed']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # EXP Progress Bar
    progress = st.session_state.user_data['experience'] / st.session_state.user_data['exp_needed']
    st.progress(min(progress, 1.0))

with col2:
    rank_info = get_current_rank(st.session_state.user_data['rank_points'])
    st.markdown(f"""
    <div class='rank-container'>
        <h2>{rank_info['rank']}</h2>
        <p>Rank Points: {st.session_state.user_data['rank_points']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    season = SEASONS[st.session_state.user_data['current_season']]
    st.markdown(f"""
    <div class='season-container'>
        <h4>Season {st.session_state.user_data['current_season']}</h4>
        <p style='margin: 5px 0;'>{season['name']}</p>
        <small>{season['start_date']} - {season['end_date']}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# PAGE: Dashboard
if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Tasks", len(st.session_state.user_data["daily_tasks"]))
    
    with col2:
        today_completed = len(get_today_completed())
        st.metric("✅ Today Completed", f"{today_completed}/{len(st.session_state.user_data['daily_tasks'])}")
    
    with col3:
        streak = get_completion_streak()
        st.metric("🔥 Streak", f"{streak} days")
    
    with col4:
        next_rank_idx = next((i for i, r in enumerate(RANK_SYSTEM) if r["rank"] == st.session_state.user_data['rank']), 0)
        if next_rank_idx < len(RANK_SYSTEM) - 1:
            pts_to_next = RANK_SYSTEM[next_rank_idx + 1]["min_points"] - st.session_state.user_data['rank_points']
            st.metric("🎯 Next Rank", f"{pts_to_next} pts")
        else:
            st.metric("🎯 Next Rank", "MAX")
    
    st.divider()
    
    # Today's Tasks Preview
    st.subheader("📋 Today's Quests")
    today_tasks = get_today_completed()
    
    for task in st.session_state.user_data["daily_tasks"]:
        is_completed = task["id"] in today_tasks
        color = "task-completed" if is_completed else "task-pending"
        status = "✅" if is_completed else "⭕"
        exp_amount = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
        
        st.markdown(f"""
        <div class='{color}'>
            <b>{status} {task['name']}</b> - {int(exp_amount)} EXP [{task['difficulty'].upper()}]
        </div>
        """, unsafe_allow_html=True)
    
    # Level Progress Chart
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Level Progress")
        fig = go.Figure(data=[
            go.Bar(
                x=["Current", "Needed"],
                y=[st.session_state.user_data['experience'], st.session_state.user_data['exp_needed']],
                marker_color=['#667eea', '#764ba2']
            )
        ])
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Rank Progression")
        rank_data = []
        for rank in RANK_SYSTEM:
            rank_data.append({
                "Rank": rank["rank"],
                "Points": rank["min_points"],
                "Current": st.session_state.user_data['rank_points'] >= rank["min_points"]
            })
        
        df_ranks = pd.DataFrame(rank_data)
        fig = px.bar(
            df_ranks,
            x="Rank",
            y="Points",
            color="Current",
            color_discrete_map={True: '#FF6347', False: '#95a5a6'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# PAGE: Daily Quests
elif page == "Daily Quests":
    st.subheader("⚔️ Daily Quests")
    st.write(f"**Current Date:** {datetime.now().strftime('%A, %B %d, %Y')}")
    
    today_completed = get_today_completed()
    col1, col2 = st.columns([3, 1])
    
    with col2:
        completion_rate = (len(today_completed) / len(st.session_state.user_data["daily_tasks"])) * 100
        st.metric("Completion", f"{completion_rate:.0f}%")
    
    st.divider()
    
    # Display tasks with completion buttons
    for task in st.session_state.user_data["daily_tasks"]:
        is_completed = task["id"] in today_completed
        exp_amount = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
        
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            difficulty_color = DIFFICULTY_COLORS.get(task["difficulty"], "#95a5a6")
            status_icon = "✅" if is_completed else "⭕"
            st.markdown(f"""
            **{status_icon} {task['name']}**  
            <span style='color: {difficulty_color}; font-weight: bold;'>[{task['difficulty'].upper()}]</span> - {int(exp_amount)} EXP
            """, unsafe_allow_html=True)
        
        with col2:
            st.write(f"🎯 +{int(exp_amount)} EXP" if not is_completed else "✨ Completed")
        
        with col3:
            if not is_completed:
                if st.button("✓", key=f"task_{task['id']}", help="Complete this task"):
                    mark_task_complete(task['id'])
                    st.success("Quest completed! 🎉")
                    st.rerun()
            else:
                st.write("✅")
    
    st.divider()
    
    # Add new task
    st.subheader("➕ Add New Quest")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_task_name = st.text_input("Quest Name")
    
    with col2:
        new_difficulty = st.selectbox("Difficulty", ["common", "rare", "epic", "legendary"])
    
    with col3:
        new_exp = st.number_input("Base EXP", min_value=5, max_value=200, value=10, step=5)
    
    if st.button("Add Quest", type="primary"):
        if new_task_name:
            new_id = max([t["id"] for t in st.session_state.user_data["daily_tasks"]], default=0) + 1
            st.session_state.user_data["daily_tasks"].append({
                "id": new_id,
                "name": new_task_name,
                "difficulty": new_difficulty,
                "exp": new_exp
            })
            st.success("Quest added! ⚔️")
            st.rerun()

# PAGE: Statistics
elif page == "Statistics":
    st.subheader("📊 Statistics & History")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_days = len(st.session_state.user_data["completion_history"])
        st.metric("📅 Active Days", total_days)
    
    with col2:
        total_tasks_completed = sum(len(tasks) for tasks in st.session_state.user_data["completion_history"].values())
        st.metric("✅ Total Tasks Completed", total_tasks_completed)
    
    with col3:
        avg_per_day = total_tasks_completed / total_days if total_days > 0 else 0
        st.metric("📈 Avg Tasks/Day", f"{avg_per_day:.1f}")
    
    st.divider()
    
    # Completion heatmap data
    if st.session_state.user_data["completion_history"]:
        st.subheader("📅 Last 30 Days Activity")
        
        # Create heatmap data
        today = datetime.now()
        heatmap_data = []
        
        for i in range(29, -1, -1):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            completed = len(st.session_state.user_data["completion_history"].get(date, []))
            heatmap_data.append({
                "Date": date,
                "Tasks": completed,
                "Week": (today - timedelta(days=i)).strftime("%U")
            })
        
        df_heatmap = pd.DataFrame(heatmap_data)
        
        fig = px.bar(
            df_heatmap,
            x="Date",
            y="Tasks",
            color="Tasks",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Task completion stats
    st.subheader("🎯 Task Statistics")
    
    task_completion = defaultdict(int)
    for date, task_ids in st.session_state.user_data["completion_history"].items():
        for task_id in task_ids:
            task_completion[task_id] += 1
    
    if task_completion:
        stats_data = []
        for task in st.session_state.user_data["daily_tasks"]:
            completed = task_completion.get(task["id"], 0)
            stats_data.append({
                "Quest": task["name"],
                "Completed": completed,
                "Difficulty": task["difficulty"]
            })
        
        df_stats = pd.DataFrame(stats_data).sort_values("Completed", ascending=False)
        
        fig = px.bar(
            df_stats,
            x="Quest",
            y="Completed",
            color="Difficulty",
            color_discrete_map=DIFFICULTY_COLORS
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# PAGE: Settings
elif page == "Settings":
    st.subheader("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### User Profile")
        username = st.text_input("Username", value="Adventurer")
        
        if st.button("Reset Progress", type="secondary"):
            st.session_state.user_data = {
                "current_season": 1,
                "level": 1,
                "experience": 0,
                "exp_needed": 100,
                "rank": "BRONZE",
                "rank_points": 0,
                "daily_tasks": [
                    {"id": 1, "name": "Morning Exercise", "difficulty": "common", "exp": 10},
                    {"id": 2, "name": "Read Book", "difficulty": "common", "exp": 10},
                    {"id": 3, "name": "Meditate", "difficulty": "common", "exp": 15},
                    {"id": 4, "name": "Complete Project", "difficulty": "rare", "exp": 50},
                    {"id": 5, "name": "Learn New Skill", "difficulty": "epic", "exp": 75},
                ],
                "completion_history": {}
            }
            st.success("Progress reset!")
            st.rerun()
    
    with col2:
        st.write("### Season Management")
        new_season = st.selectbox("Change Season", list(SEASONS.keys()))
        
        if st.button("Start New Season", type="secondary"):
            st.session_state.user_data["current_season"] = new_season
            st.session_state.user_data["level"] = 1
            st.session_state.user_data["experience"] = 0
            st.session_state.user_data["rank_points"] = 0
            st.session_state.user_data["completion_history"] = {}
            st.success(f"Started Season {new_season}: {SEASONS[new_season]['name']}!")
            st.rerun()
    
    st.divider()
    
    st.write("### About")
    st.info("""
    **Daily Tracker - Leveling System**
    
    A gamified daily habit tracker inspired by:
    - PUBG Ranking System
    - Solo Leveling (Sung Jinwoo's Awakening System)
    
    Features:
    - 🎮 8-Tier Ranking System
    - ⚡ Level Up Progression
    - 🎯 Daily Quests with Multiple Difficulties
    - 📊 Statistics & Progress Tracking
    - 🔥 Streak Counter
    - 🏆 Season Rotation
    """)

st.sidebar.divider()
st.sidebar.write("**Made with ⚔️ for Daily Champions**")
