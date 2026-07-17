# #1. 라이브러리 가져오기
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests  # 구글 시트 대신 인터넷 통신용 라이브러리 사용

# #2. 기본 테마 설정 및 디자인 적용
st.set_page_config(
    page_title="체온:On",
    layout="centered",
    initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght=700&family=Noto+Sans+KR:wght=700&display=swap');

.school-logo-title {
    font-family: 'Noto Serif KR', serif;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 5px;}
.school-logo-title img {
    height: 50px;}
.school-title-text {
    font-family: 'Noto Serif KR', serif;
    font-size: 40px;
    font-weight: 700;
    color: #1BD170;}
.school-subtitle {
    font-size: 16px;
    color: #666666;
    margin-bottom: 25px;}
</style>
""", unsafe_allow_html=True)

# 🌐 초간단 데이터 저장소 주소 (가입 불필요!)
# 이 주소에 투표 데이터가 실시간으로 계속 누적돼서 보관될 거야.
DB_URL = "https://api.jsonbin.io/v3/b/6697b0aae41b4d34e4130006"
# (혹시 데이터가 꼬이거나 초기화하고 싶을 때 쓸 헤더 정보)
HEADERS = {
    "X-Master-Key": "$2a$10$Wb3rMeeO7q6r87D5IeX7UeYk1vshUu5A3g.UoFymk1YQp77YdGxei",
    "Content-Type": "application/json"
}

# 실시간 투표 데이터를 읽어오는 함수
def load_vote_data():
    try:
        response = requests.get(DB_URL, headers={"X-Master-Key": HEADERS["X-Master-Key"]})
        data = response.json()["record"]
        return data["cold"], data["decent"], data["hot"]
    except:
        return 0, 0, 0

# 투표 데이터 업데이트 함수
def update_vote_data(cold, decent, hot):
    payload = {"cold": cold, "decent": decent, "hot": hot}
    requests.put(DB_URL, json=payload, headers=HEADERS)

# 실시간 데이터 로드
cold_votes, decent_votes, hot_votes = load_vote_data()

# #4. 실시간 남은 시간 타이머 경고창 설정
@st.fragment(run_every="1s")
def render_timer_warning():
    vote_time_param = st.query_params.get("last_vote_time")
    is_voted = False
    if vote_time_param is not None:
        vote_time = datetime.fromisoformat(vote_time_param)
        time_passed = datetime.now() - vote_time
        if time_passed < timedelta(hours=1):
            remaining = timedelta(hours=1) - time_passed
            minutes = int(remaining.total_seconds() / 60)
            seconds = int(remaining.total_seconds() % 60)
            st.warning(f"이미 투표하셨습니다. {minutes}분 {seconds}초 뒤에 다시 투표할 수 있습니다.")
            is_voted = True
    st.session_state["is_disabled_temp"] = is_voted

render_timer_warning()
is_disabled = st.session_state.get("is_disabled_temp", False)

# #5. 영신여고 로고 및 커스텀 타이틀 표시
st.markdown("""
<div class="school-logo-title">
    <img src="https://i.namu.wiki/i/ZG85HJ4CEdDBlFGtk14SJ7FWNsPomgxyXcdkAH5_Pq9x5u4F68t02Z3WBqUZaB6dEfGzKY_RSRUZk_qBTp82AdCfjMKrU44P5M-IT53fdBrKTGwKkA5YgADVC0U8YWom2Cf0MBgvCVWjKb8J6KZilQ.webp" alt="로고">
    <span class="school-title-text">체온:On</span>
</div>
<div class="school-subtitle">영신여자고등학교 스마트 온도투표소</div>
""", unsafe_allow_html=True)

# #6. 가로 배치 버튼 및 클릭 시 실시간 반영
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("추워요", use_container_width=True, disabled=is_disabled):
        update_vote_data(cold_votes + 1, decent_votes, hot_votes)
        st.query_params["last_vote_time"] = datetime.now().isoformat()
        st.success("투표가 완료되었습니다.")
        st.rerun()

with col2:
    if st.button("적당해요", use_container_width=True, disabled=is_disabled):
        update_vote_data(cold_votes, decent_votes + 1, hot_votes)
        st.query_params["last_vote_time"] = datetime.now().isoformat()
        st.success("투표가 완료되었습니다.")
        st.rerun()

with col3:
    if st.button("더워요", use_container_width=True, disabled=is_disabled):
        update_vote_data(cold_votes, decent_votes, hot_votes + 1)
        st.query_params["last_vote_time"] = datetime.now().isoformat()
        st.success("투표가 완료되었습니다.")
        st.rerun()

st.markdown("---")

# #7. 반원 그래프 그리기
total_votes = cold_votes + decent_votes + hot_votes

if total_votes > 0:
    labels = ["추워요", "적당해요", "더워요"]
    values = [cold_votes, decent_votes, hot_votes]
    colors = ['#33A2FF', '#1BD170', '#FF5733']
else:
    labels = ["아직 투표가 없습니다."]
    values = [1]
    colors = ["#BAB8B8"]

fig = go.Figure(data=[go.Pie(
    labels=labels, 
    values=values, 
    hole=0.5, 
    domain=dict(y=[0.5, 1]), 
    marker=dict(colors=colors))])

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#333333'),
    showlegend=True)
st.plotly_chart(fig)
