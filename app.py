# #1. 라이브러리 가져오기
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
# gspread 라이브러리로 교체
import gspread

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

SPREADSHEET_ID = "1sX9l76LK_PT_NIRyhaGQLvo_RrJASFfquIfR684II2s" 

try:
    # 링크 공유된 시트에 익명으로 접근하는 설정
    gc = gspread.public_api()
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.get_worksheet(0) # 첫 번째 탭 선택
    
    # 데이터 읽어오기 (첫 번째 줄 데이터)
    # 구글 시트 구조: A1:추워요, B1:적당해요, C1:더워요 / A2:숫자, B2:숫자, C2:숫자
    cold_votes = int(worksheet.acell('A2').value or 0)
    decent_votes = int(worksheet.acell('B2').value or 0)
    hot_votes = int(worksheet.acell('C2').value or 0)
except Exception as e:
    st.error(f"구글 시트 연결 실패: {e}")
    cold_votes, decent_votes, hot_votes = 0, 0, 0

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

# #6. 가로 배치 버튼 및 클릭 시 구글 시트에 즉시 반영
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("추워요", use_container_width=True, disabled=is_disabled):
        worksheet.update_acell('A2', cold_votes + 1) # A2 칸을 기존 값 + 1로 업데이트
        st.query_params["last_vote_time"] = datetime.now().isoformat()
        st.success("투표가 완료되었습니다.")
        st.rerun()

with col2:
    if st.button("적당해요", use_container_width=True, disabled=is_disabled):
        worksheet.update_acell('B2', decent_votes + 1) # B2 칸 업데이트
        st.query_params["last_vote_time"] = datetime.now().isoformat()
        st.success("투표가 완료되었습니다.")
        st.rerun()

with col3:
    if st.button("더워요", use_container_width=True, disabled=is_disabled):
        worksheet.update_acell('C2', hot_votes + 1) # C2 칸 업데이트
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
    showlegend=True
)

st.plotly_chart(fig)
