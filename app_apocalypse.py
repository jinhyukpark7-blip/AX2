import random
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="아포칼립스: 데드 시티 탈출", page_icon="🧟", layout="centered"
)


# --- 1. 세션 상태 초기화 ---
def init_game():
    st.session_state.scene = "intro"
    st.session_state.hp = 100
    st.session_state.hunger = 0  # 100에 도달하면 아사 위험
    st.session_state.inventory = ["낡은 배낭", "비상용 생수"]
    st.session_state.day = 1
    st.session_state.log = []


if "scene" not in st.session_state:
    init_game()


def log_msg(msg):
    st.session_state.log.insert(0, msg)


def change_scene(scene_name):
    st.session_state.scene = scene_name


# --- 2. 상단 상태창 (Dashboard) ---
st.title("🧟 데드 시티: 최후의 탈출")

stat_col1, stat_col2, stat_col3 = st.columns(3)
with stat_col1:
    st.metric("❤️ 체력", f"{st.session_state.hp} / 100")
with stat_col2:
    st.metric("🍖 허기", f"{st.session_state.hunger} %")
with stat_col3:
    st.metric("📅 생존 일수", f"{st.session_state.day}일 차")

with st.expander("🎒 소지품 확인", expanded=True):
    if st.session_state.inventory:
        st.write(", ".join([f"`{item}`" for item in st.session_state.inventory]))
    else:
        st.write("소지품이 비어 있습니다.")

st.divider()

# 체력/허기 체크
if st.session_state.hp <= 0 or st.session_state.hunger >= 100:
    st.session_state.scene = "game_over"

# --- 3. 씬(Scene) 로직 ---

# [씬: 인트로]
if st.session_state.scene == "intro":
    st.markdown("""
    도시가 무너진 지 3주가 지났습니다.  
    라디오에서는 **'강 건너 방벽 너머 제3 안전 구역'**으로 통하는 마지막 헬기가 오늘 해질녘에 출발한다는 방송이 흘러나옵니다.
    
    당신은 버려진 편의점 은신처에서 눈을 떴습니다. 이제 결단을 내려야 합니다.
    """)
    if st.button("🚪 은신처를 나와 탈출을 시작한다"):
        change_scene("crossroad")
        st.rerun()

# [씬: 교차로]
elif st.session_state.scene == "crossroad":
    st.subheader("📍 안개 낀 교차로")
    st.write(
        "버려진 차량들이 엉켜있는 도로입니다. 멀리 강 너머로 탈출 헬기가 보이지만, 가는 길을 선택해야 합니다."
    )

    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("🏪 약국 폐허 수색하기"):
            st.session_state.hunger += 15
            change_scene("pharmacy")
            st.rerun()
    with btn2:
        if st.button("🚇 지하철 통로로 진입"):
            st.session_state.hunger += 15
            change_scene("subway")
            st.rerun()
    with btn3:
        if st.button("🚗 대교 위 직진 돌파"):
            st.session_state.hunger += 15
            change_scene("bridge")
            st.rerun()

# [씬: 약국 수색]
elif st.session_state.scene == "pharmacy":
    st.subheader("💊 버려진 약국")
    st.write("깨진 유리창 너머로 선반들이 어지럽게 쓰러져 있습니다.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 구급상자 수색하기 (위험)"):
            # 70% 확률로 붕대/구급약 획득, 30% 감염자 기습
            dice = random.randint(1, 100)
            if dice > 30:
                if "구급상자" not in st.session_state.inventory:
                    st.session_state.inventory.append("구급상자")
                    st.session_state.inventory.append("통조림")
                    st.success(
                        "🎉 **구급상자**와 **통조림**을 온전히 찾아냈습니다!"
                    )
                else:
                    st.info("더 이상 쓸 만한 약품이 없습니다.")
            else:
                st.error(
                    "구석에 숨어있던 감염자가 기습했습니다! 팔을 물렸습니다. (HP -25)"
                )
                st.session_state.hp -= 25
                if "쇠파이프" not in st.session_state.inventory:
                    st.session_state.inventory.append("피 묻은 쇠파이프")
                    st.write("바닥에 굴러다니던 쇠파이프로 겨우 떨쳐냈습니다.")
    with c2:
        if st.button("🔙 교차로로 돌아가기"):
            change_scene("crossroad")
            st.rerun()

    # 인벤토리 소비 액션
    if "통조림" in st.session_state.inventory:
        if st.button("🥫 통조림 먹기 (허기 -40%)"):
            st.session_state.hunger = max(0, st.session_state.hunger - 40)
            st.session_state.inventory.remove("통조림")
            st.success("배를 채워 기력을 회복했습니다.")
            st.rerun()

    if "구급상자" in st.session_state.inventory:
        if st.button("🩹 구급상자 사용하기 (체력 +30)"):
            st.session_state.hp = min(100, st.session_state.hp + 30)
            st.session_state.inventory.remove("구급상자")
            st.success("상처를 치료했습니다.")
            st.rerun()

# [씬: 지하철 통로]
elif st.session_state.scene == "subway":
    st.subheader("🚇 어두운 지하철 터널")
    st.write(
        "지하 통로는 조용하지만 지독한 악취가 납니다. 저 멀리 개찰구 쪽에 변종 감염체 1마리가 서성이고 있습니다."
    )

    if (
        "피 묻은 쇠파이프" in st.session_state.inventory
        or "샷건" in st.session_state.inventory
    ):
        if st.button("⚔️ 무기를 쥐고 은밀하게 처치"):
            st.success(
                "무기로 감염체의 뒤를 가격해 소리 없이 처치했습니다! 사물함에서 '비상 탈출 열쇠'를 얻었습니다."
            )
            st.session_state.inventory.append("비상 탈출 열쇠")
            change_scene("safezone_tunnel")
            st.rerun()
    else:
        if st.button("👟 소리를 내지 않고 우회 시도 (50% 확률)"):
            if random.random() > 0.5:
                st.success("다행히 들키지 않고 통로를 빠져나왔습니다!")
                change_scene("safezone_tunnel")
            else:
                st.error(
                    "발밑의 캔을 밟아 감염체에게 포위당했습니다! (HP -50)"
                )
                st.session_state.hp -= 50
                change_scene("safezone_tunnel")
            st.rerun()

    if st.button("🔙 교차로로 돌아가기"):
        change_scene("crossroad")
        st.rerun()

# [씬: 대교 직진]
elif st.session_state.scene == "bridge":
    st.subheader("🚗 불타는 대교")
    st.write(
        "다리 위는 버려진 차량과 불길로 아수라장입니다. 감염자 무리가 저 멀리서 몰려오고 있습니다!"
    )

    if st.button("🏃 전력 질주로 차량 사이를 뛰어넘기"):
        st.session_state.hp -= 20
        st.session_state.hunger += 20
        st.warning("숨이 턱 끝까지 찹니다. 긁히고 다쳤지만 대교 끝에 도달했습니다!")
        change_scene("final_gate")
        st.rerun()

    if st.button("🔙 교차로로 돌아가기"):
        change_scene("crossroad")
        st.rerun()

# [씬: 지하철 비상구/대교 통과 후 최종 관문]
elif st.session_state.scene in ["safezone_tunnel", "final_gate"]:
    st.subheader("🚁 제3 안전 구역 검문소")
    st.write(
        "마침내 안전 구역의 철책선 앞입니다. 헬기의 프로펠러 소리가 요란하게 들립니다."
    )

    if "비상 탈출 열쇠" in st.session_state.inventory:
        st.success(
            "🔑 '비상 탈출 열쇠'로 잠긴 검문소 보안문을 열고 헬기 착륙장으로 곧장 진입합니다!"
        )
        if st.button("🚁 헬기에 탑승하기"):
            change_scene("ending_perfect")
            st.rerun()
    else:
        st.write(
            "문이 굳게 잠겨 있어 철조망을 넘어야 합니다. 감염자들이 다가오고 있습니다!"
        )
        if st.button("🧗 철조망을 기어오른다"):
            st.session_state.hp -= 30
            if st.session_state.hp > 0:
                change_scene("ending_survival")
            else:
                change_scene("game_over")
            st.rerun()

# [씬: 엔딩 - 완벽 생존]
elif st.session_state.scene == "ending_perfect":
    st.balloons()
    st.success("🎉 **[히든 클리어: 완벽한 구출 엔딩]**")
    st.markdown("""
    - 안전하게 보안문을 통과해 헬기에 가장 먼저 탑승했습니다.
    - 방역 의료진의 치료를 받으며 안전 지대로 향합니다.
    """)
    if st.button("🔄 처음부터 다시 도전"):
        init_game()
        st.rerun()

# [씬: 엔딩 - 부상 생존]
elif st.session_state.scene == "ending_survival":
    st.warning("🩹 **[일반 클리어: 만신창이 생존 엔딩]**")
    st.markdown("""
    - 철조망에 긁히고 찢겼지만, 헬기 조종사가 당신을 끌어올려 주었습니다.
    - 간신히 목숨은 건졌습니다!
    """)
    if st.button("🔄 처음부터 다시 도전"):
        init_game()
        st.rerun()

# [씬: 게임 오버]
elif st.session_state.scene == "game_over":
    st.error("💀 **[생존 실패: 게임 오버]**")
    if st.session_state.hp <= 0:
        st.write("원인: 치명적인 부상으로 쓰러졌습니다.")
    elif st.session_state.hunger >= 100:
        st.write("원인: 극심한 탈진과 허기로 쓰러졌습니다.")

    if st.button("🔄 부활하여 다시 도전"):
        init_game()
        st.rerun()