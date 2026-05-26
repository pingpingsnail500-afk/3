import streamlit as st
from openai import OpenAI

st.title("📚 3. 국립부경대학교 도서관 챗봇")

api_key = st.session_state.get("openai_api_key", "")

# 국립부경대학교 도서관 규정 텍스트 (예시 데이터 수록, 실제 대량 복사 붙여넣기 가능)
LIBRARY_REGULATIONS = """
[국립부경대학교 도서관 규정]
제1조(목적) 이 규정은 국립부경대학교 도서관의 조직과 운영에 관한 사항을 규정함을 목적으로 한다.
제15조(휴관일) 
1. 도서관의 휴관일은 다음 각 호와 같다.
   - 관공서의 공휴일
   - 우리 대학교 개교기념일 (5월 10일)
   - 기타 관장이 필요하다고 인정하여 지정하는 날
2. 제1항에도 불구하고 열람실은 관장이 필요하다고 인정할 경우 개관할 수 있다.

제18조(대출 권수 및 기간)
1. 자료의 대출 권수 및 기간은 다음 각 호와 같다.
   - 전임교원: 30권, 90일
   - 대학원생: 15권, 30일
   - 학부생(재학생): 10권, 14일
   - 조교 및 직업원: 15권, 30일
2. 도서의 반납 예정일이 휴관일인 경우에는 그 다음 날을 반납일로 한다.
"""

if "lib_messages" not in st.session_state:
    st.session_state["lib_messages"] = []

if st.button("대화 초기화"):
    st.session_state["lib_messages"] = []
    st.rerun()

# 가이드 질문 예시 버튼
st.markdown("**🔍 자주 묻는 질문 예시:**")
col1, col2 = st.columns(2)
with col1:
    if st.button("📅 도서관 휴관일은 언제인가요?"):
        prompt_input = "도서관 휴관일은 언제인가요?"
        st.session_state["auto_prompt"] = prompt_input
with col2:
    if st.button("📖 학부생 책 대여 권수와 기간은?"):
        prompt_input = "학부생 책 대여 권수와 기간은 어떻게 되나요?"
        st.session_state["auto_prompt"] = prompt_input

# 채팅 기록 출력
for msg in st.session_state["lib_messages"]:
    if msg["role"] != "system": # 시스템 프롬프트는 제외하고 출력
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 자동 입력 혹은 사용자의 직접 입력 처리
chat_input_val = st.chat_input("도서관 규정에 대해 물어보세요...")
if "auto_prompt" in st.session_state:
    chat_input_val = st.session_state.pop("auto_prompt")

if chat_input_val:
    if not api_key:
        st.error("사이드바에 OpenAI API Key를 입력해주세요.")
    else:
        st.session_state["lib_messages"].append({"role": "user", "content": chat_input_val})
        with st.chat_message("user"):
            st.write(chat_input_val)

        # 시스템 프롬프트 설계하여 도서관 규정 주입
        system_prompt = f"당신은 국립부경대학교 도서관 안내 챗봇입니다. 아래 제공되는 [도서관 규정]만을 바탕으로 친절하고 정확하게 답변하세요. 규정에 없는 내용은 모른다고 정중히 답변하세요.\n\n{LIBRARY_REGULATIONS}"
        
        messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state["lib_messages"]

        client = OpenAI(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("규정 확인 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_to_send
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state["lib_messages"].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"오류 발생: {e}")