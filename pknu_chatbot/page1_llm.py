import streamlit as st
from openai import OpenAI

st.title("🤖 1. 기본 LLM 응답 페이지")

api_key = st.session_state.get("openai_api_key", "")

# @st.cache_data 적용 (API Key와 질문이 같으면 캐시 데이터 반환)
@st.cache_data
def get_llm_response(api_key, query):
    if not api_key:
        return "API Key가 입력되지 않았습니다. 사이드바에서 입력해주세요."
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {e}"

if not api_key:
    st.warning("👈 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요!")
else:
    user_query = st.text_input("LLM에게 질문을 입력하세요:", placeholder="예: Streamlit이 뭐야?")
    
    if user_query:
        with st.spinner("답변 생성 중..."):
            answer = get_llm_response(api_key, user_query)
            st.markdown("### 📝 답변")
            st.write(answer)