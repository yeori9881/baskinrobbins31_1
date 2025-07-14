import streamlit as st
import random

# --- 커스텀 CSS (폰트 크기 2배 확대) ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 1.7em !important;
    }
    .stTextInput > div > div > input {
        font-size: 1.5em !important;
    }
    .stButton button {
        font-size: 1.2em !important;
        padding: 0.5em 1.5em;
    }
    </style>
""", unsafe_allow_html=True)

# 상태 초기화
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "current_number" not in st.session_state:
    st.session_state.current_number = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "bot_first" not in st.session_state:
    st.session_state.bot_first = None
if "awaiting_user_input" not in st.session_state:
    st.session_state.awaiting_user_input = False
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = None

st.title("챗봇과 하는 베스킨라빈스31 게임")

def display_chat():
    for role, text in st.session_state.chat_log:
        prefix = "👤 너:" if role == "user" else "🤖 챗봇:"
        st.markdown(f"{prefix} {text}")

def bot_turn():
    cur = st.session_state.current_number

    if st.session_state.bot_first:
        # 챗봇이 선공일 경우: 필승 루트 (4n+2)
        next_target = ((cur - 2) // 4 + 1) * 4 + 2
        to_say = list(range(cur + 1, min(next_target + 1, 32)))
    else:
        # 챗봇이 후공일 경우: 기회가 되면 필승 루트 진입
        for count in range(1, 4):
            target = cur + count
            if target % 4 == 2:
                to_say = list(range(cur + 1, target + 1))
                break
        else:
            count = random.randint(1, 3)
            to_say = list(range(cur + 1, min(cur + count + 1, 32)))

    # 챗봇 말하기
    if to_say:
        bot_speak = " ".join(map(str, to_say))
        st.session_state.chat_log.append(("bot", bot_speak))
        st.session_state.current_number = to_say[-1]

    # 게임 종료 여부 확인
    if st.session_state.current_number >= 31:
        st.session_state.chat_log.append(("bot", "앗! 내가 31을 말해버렸네... 네가 이겼어! 이 화면을 보여주고 상품을 달라고 해!"))
        st.session_state.game_over = True
    else:
        st.session_state.awaiting_user_input = True

def start_game():
    if st.session_state.bot_first:
        st.session_state.chat_log.append(("bot", "그럼 내가 먼저 시작할게!"))
        st.session_state.chat_log.append(("bot", "1 2"))
        st.session_state.current_number = 2
    else:
        st.session_state.chat_log.append(("bot", "네가 먼저 해!"))
    st.session_state.awaiting_user_input = True

# 선공 선택
if st.session_state.bot_first is None:
    choice = st.radio("누가 먼저 시작할까요?", ("챗봇", "나"))
    if st.button("게임 시작"):
        st.session_state.bot_first = (choice == "챗봇")
        start_game()

# 유저가 입력한 값이 있다면 챗봇 차례 실행
if st.session_state.last_user_input:
    user_numbers = st.session_state.last_user_input
    st.session_state.chat_log.append(("user", " ".join(map(str, user_numbers))))
    st.session_state.current_number = user_numbers[-1]
    st.session_state.last_user_input = None

    if st.session_state.current_number >= 31:
        st.session_state.chat_log.append(("bot", "내가 이겼다! 사실 이 게임에는 필승법이 있어. 한번 물어보고 다시 도전해보자!"))
        st.session_state.game_over = True
    else:
        st.session_state.awaiting_user_input = False
        bot_turn()

    st.rerun()

# 채팅 출력
display_chat()

# ✅ 자동 스크롤: 맨 아래로 이동
st.markdown("""
    <div id="bottom"></div>
    <script>
        var element = document.getElementById("bottom");
        if (element) {
            element.scrollIntoView({behavior: "smooth"});
        }
    </script>
""", unsafe_allow_html=True)

# 유저 입력 폼
if not st.session_state.game_over and st.session_state.awaiting_user_input:
    with st.form("user_input_form", clear_on_submit=True):
        user_input = st.text_input("숫자를 1개~3개 입력하세요 (띄어쓰기 구분)")
        submitted = st.form_submit_button("제출")

    if submitted:
        try:
            numbers = list(map(int, user_input.strip().split()))
            expected = st.session_state.current_number + 1

            if not (1 <= len(numbers) <= 3):
                st.error("❗ 1개에서 3개의 숫자를 입력하세요.")
            elif numbers[0] != expected or any(numbers[i] != numbers[i - 1] + 1 for i in range(1, len(numbers))):
                st.error(f"❗ 숫자는 {expected}부터 연속되어야 합니다.")
            else:
                st.session_state.last_user_input = numbers
                st.rerun()
        except ValueError:
            st.error("❗ 숫자를 정확하게 입력해주세요.")

# 게임 끝났을 때 다시 시작 버튼
if st.session_state.game_over:
    if st.button("다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
