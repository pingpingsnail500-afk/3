import streamlit as st

st.set_page_config(page_title="부경대 AI 웹 앱", layout="wide")

# 1. session_state에 API Key 초기화 및 저장
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

# 사이드바에서 API Key 입력 받기 (password 타입)
with st.sidebar:
    st.title("🔑 설정")
    api_key_input = st.text_input(
        "OpenAI API Key를 입력하세요",
        value=st.session_state["openai_api_key"],
        type="password",
        placeholder="sk-..."
    )
    # 입력값이 변경되면 session_state 업데이트
    if api_key_input != st.session_state["openai_api_key"]:
        st.session_state["openai_api_key"] = api_key_input

# 2. 다중 페이지 네비게이션 정의
pages = {
    "기능 실습": [
        st.Page("page1_llm.py", title="1. 기본 LLM 응답", icon="🤖"),
        st.Page("page2_chat.py", title="2. 일반 Chat 봇", icon="💬"),
        st.Page("page3_library.py", title="3. 부경대 도서관 챗봇", icon="📚"),
        st.Page("page4_chatpdf.py", title="4. ChatPDF (파일 검색)", icon="📄"),
    ]
}

pg = st.navigation(pages)
pg.run()