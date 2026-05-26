import streamlit as st
from openai import OpenAI
import time

st.title("📄 4. ChatPDF (OpenAI File Search)")

api_key = st.session_state.get("openai_api_key", "")

# 세션 상태 초기화
if "pdf_messages" not in st.session_state:
    st.session_state["pdf_messages"] = []
if "assistant_id" not in st.session_state:
    st.session_state["assistant_id"] = None
if "vector_store_id" not in st.session_state:
    st.session_state["vector_store_id"] = None
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

# 리소스 삭제 함수 (Clear 버튼용)
def cleanup_resources():
    if not api_key:
        return
    client = OpenAI(api_key=api_key)
    try:
        if st.session_state["assistant_id"]:
            client.beta.assistants.delete(st.session_state["assistant_id"])
        if st.session_state["vector_store_id"]:
            client.beta.vector_stores.delete(st.session_state["vector_store_id"])
    except Exception as e:
        st.warning(f"리소스 삭제 중 일부 에러 발생: {e}")
    
    st.session_state["pdf_messages"] = []
    st.session_state["assistant_id"] = None
    st.session_state["vector_store_id"] = None
    st.session_state["thread_id"] = None

if st.button("Clear (Vector Store 및 대화 삭제)"):
    with st.spinner("OpenAI 클라우드 내 벡터스토어 및 어시스턴트 자원 삭제 중..."):
        cleanup_resources()
    st.success("초기화 완료!")
    st.rerun()

if not api_key:
    st.warning("사이드바에 OpenAI API Key를 먼저 입력해주세요.")
else:
    client = OpenAI(api_key=api_key)
    
    # 1. 파일 업로더 (단일 파일 제한)
    uploaded_file = st.file_uploader("PDF 파일을 하나 업로드하세요", type=["pdf"], accept_multiple_files=False)
    
    # 파일이 업로드되었고, 아직 Assistant 환경이 구성되지 않았다면 세팅 진행
    if uploaded_file and not st.session_state["assistant_id"]:
        with st.spinner("OpenAI File Search 서버에 벡터스토어를 생성하고 파일을 인덱싱하는 중..."):
            try:
                # 파일 서버 업로드
                file_object = client.files.create(file=(uploaded_file.name, uploaded_file.getvalue(), "application/pdf"), purpose="assistants")
                
                # 벡터 스토어 생성 및 파일 링크
                vector_store = client.beta.vector_stores.create(name=f"VS_{uploaded_file.name}")
                client.beta.vector_stores.files.create(vector_store_id=vector_store.id, file_id=file_object.id)
                
                # Assistant 생성 (file_search 툴 활성화)
                assistant = client.beta.assistants.create(
                    name="PDF Q&A Assistant",
                    instructions="당신은 업로드된 PDF 문서 내용을 기반으로 답변하는 전문 AI입니다. 문서 내용을 바탕으로 정확하게 답변하세요.",
                    model="gpt-4o-mini",
                    tools=[{"type": "file_search"}],
                    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
                )
                
                # 쓰레드 생성
                thread = client.beta.threads.create()
                
                # 세션에 정보 보관
                st.session_state["assistant_id"] = assistant.id
                st.session_state["vector_store_id"] = vector_store.id
                st.session_state["thread_id"] = thread.id
                st.success("PDF 문서 분석 완료! 이제 대화를 시작하실 수 있습니다.")
            except Exception as e:
                st.error(f"Assistant 세팅 오류: {e}")

    # 채팅 UI 표현
    for msg in st.session_state["pdf_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("PDF 내용에 대해 질문하세요"):
        if not st.session_state["assistant_id"]:
            st.error("먼저 PDF 파일을 업로드해야 합니다.")
        else:
            st.session_state["pdf_messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
                
            # Threads API를 사용하여 메시지 전달 및 실행(Run)
            client.beta.threads.messages.create(
                thread_id=st.session_state["thread_id"],
                role="user",
                content=prompt
            )
            
            run = client.beta.threads.runs.create(
                thread_id=st.session_state["thread_id"],
                assistant_id=st.session_state["assistant_id"]
            )
            
            with st.chat_message("assistant"):
                with st.spinner("PDF 문서 검색 및 답변 생성 중..."):
                    # 폴링(Polling) 작업 완료 대기
                    while run.status in ["queued", "in_progress"]:
                        time.sleep(0.5)
                        run = client.beta.threads.runs.retrieve(thread_id=st.session_state["thread_id"], run_id=run.id)
                    
                    if run.status == "completed":
                        messages = client.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
                        # 가장 최신 답변 가져오기
                        answer = messages.data[0].content[0].text.value
                        st.write(answer)
                        st.session_state["pdf_messages"].append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"Run 실패 상태: {run.status}")