import streamlit as st
from openai import OpenAI

st.title("💬 2. 일반 Chat 페이지")

api_key = st.session_state.get("openai_api_key", "")

# 대화 기록 세션 초기화
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Clear 버튼 구현
if st.button("Clear (대화 초기화)"):
    st.session_state["chat_messages"] = []
    st.rerun()

# 기존 대화 내용 렌더링
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    if not api_key:
        st.error("OpenAI API Key가 필요합니다. 사이드바에 입력해주세요.")
    else:
        # 사용자 메시지 추가 및 표시
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # OpenAI 응답 생성
        client = OpenAI(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state["chat_messages"]
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    # 어시스턴트 답변 저장
                    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"오류 발생: {e}")