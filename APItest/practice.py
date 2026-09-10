import random
import streamlit as st

st.set_page_config(
    page_title="다윈의 대죄: 지옥 탈출 TRPG", page_icon="📜", layout="wide"
)

# -------------------------------------------------------------
# 1. 프리셋 캐릭터 및 종교 데이터 정의
# -------------------------------------------------------------
PRESET_CHARACTERS = {
    "통깡 (반신 주술사)": {
        "job": "주술사",
        "race": "반신",
        "god": "선신",
        "hp": 7,
        "max_hp": 7,
        "mp": 3,
        "max_mp": 3,
        "skills": ["반신(스탯교환)", "저주", "정령 소환", "설득"],
        "desc": "선한 행동을 할수록 선신의 권능 스택이 쌓입니다.",
    },
    "왈도순 (뱀파이어 기술자)": {
        "job": "기술자",
        "race": "뱀파이어",
        "god": "악신",
        "hp": 8,
        "max_hp": 8,
        "mp": 7,
        "max_mp": 7,
        "skills": ["박쥐 변신", "어둠 특화", "흡혈", "열쇠따기", "기계 능숙"],
        "desc": "악한 행동을 할수록 악신의 권능 스택이 쌓입니다.",
    },
    "모잉 (세이렌 드루이드)": {
        "job": "드루이드",
        "race": "세이렌",
        "god": "재물신",
        "hp": 11,
        "max_hp": 11,
        "mp": 5,
        "max_mp": 5,
        "skills": ["수중 호흡", "세이렌의 노래", "자연 치유", "감정"],
        "desc": "재물과 귀중품을 신에게 바쳐 기적을 얻습니다.",
    },
    "장마군 (천사 격투가)": {
        "job": "격투가",
        "race": "천사",
        "god": "혼돈신",
        "hp": 18,
        "max_hp": 18,
        "mp": 2,
        "max_mp": 2,
        "skills": ["이중 타격", "반격", "부수기", "도약", "협박"],
        "desc": "예측할 수 없는 혼돈신의 변덕스러운 기적을 받습니다.",
    },
}

DEATH_REASONS = [
    "젓가락이 피뢰침 역할을 하여 천둥 번개에 맞아 사망했습니다.",
    "장난감 자동차가 아킬레스건을 강타해 그대로 넘어져 사망했습니다.",
    "좋아하는 길고양이를 마주쳐 너무 기쁜 나머지 심장마비로 사망했습니다.",
    "바리스타가 실수로 떨어뜨린 각설탕이 머리 혈을 찔러 사망했습니다.",
]

# -------------------------------------------------------------
# 2. 게임 상태 초기화
# -------------------------------------------------------------
if "game_state" not in st.session_state:
    st.session_state.game_state = "CHAR_SELECT"
    st.session_state.player = None
    st.session_state.death_reason = ""
    st.session_state.location = "S01"
    st.session_state.inventory = []
    st.session_state.bloodstones = 0  # 혈석
    st.session_state.powers = []  # 획득한 마신의 권능
    st.session_state.god_stack = 0  # 신앙 스택
    st.session_state.logs = []


def add_log(msg):
    st.session_state.logs.append(msg)


def change_location(loc_id):
    st.session_state.location = loc_id


# -------------------------------------------------------------
# 3. 사이드바 (캐릭터 상태 및 신앙창)
# -------------------------------------------------------------
if st.session_state.player:
    st.sidebar.title("🧙 모험가 정보")
    p = st.session_state.player
    st.sidebar.markdown(f"**이름/직업:** {p['name']} ({p['job']})")
    st.sidebar.markdown(f"**섬기는 신:** `{p['god']}` (스택: {st.session_state.god_stack})")
    st.sidebar.progress(max(0.0, min(1.0, p["hp"] / p["max_hp"])), text=f"HP: {p['hp']}/{p['max_hp']}")
    st.sidebar.progress(max(0.0, min(1.0, p["mp"] / p["max_mp"])), text=f"MP: {p['mp']}/{p['max_mp']}")
    st.sidebar.metric("💎 소지 혈석", f"{st.session_state.bloodstones} 개")

    st.sidebar.subheader("👑 획득한 마신의 권능")
    if st.session_state.powers:
        for pw in st.session_state.powers:
            st.sidebar.success(f"• {pw}")
    else:
        st.sidebar.caption("아직 획득한 권능이 없습니다.")

    st.sidebar.subheader("🎒 소지품")
    if st.session_state.inventory:
        st.sidebar.write(", ".join([f"`{i}`" for i in st.session_state.inventory]))
    else:
        st.sidebar.caption("소지품이 비어있습니다.")

    # 기도하기 기능
    st.sidebar.divider()
    if st.sidebar.button("🙏 신에게 기도하기"):
        if p["god"] == "선신":
            if st.session_state.god_stack >= 1:
                st.session_state.god_stack -= 1
                p["hp"] = min(p["max_hp"], p["hp"] + 4)
                add_log("🙏 [선신의 기적] 온화한 빛이 감싸며 체력을 4 회복했습니다.")
            else:
                add_log("🙏 선신의 목소리: '더 많은 선행을 베풀어야 권능을 내릴 수 있느니라.'")
        elif p["god"] == "혼돈신":
            effect = random.choice(["hp_up", "mp_up", "item", "laugh"])
            if effect == "hp_up":
                p["hp"] = min(p["max_hp"], p["hp"] + 5)
                add_log("🎲 [혼돈신의 장난] 갑자기 상처가 아물었습니다!")
            elif effect == "mp_up":
                p["mp"] = p["max_mp"]
                add_log("🎲 [혼돈신의 장난] 마나가 가득 찼습니다!")
            elif effect == "item":
                st.session_state.inventory.append("이상한 과자")
                add_log("🎲 [혼돈신의 장난] 주머니에 이상한 과자가 생겼습니다.")
            else:
                add_log("🎲 [혼돈신] 큭큭 웃음소리만 들려오고 아무 일도 일어나지 않았습니다.")
        st.rerun()

# -------------------------------------------------------------
# 4. 게임 화면 분기
# -------------------------------------------------------------
st.title("📜 다윈의 대죄 (TRPG 지옥 탈출기)")

# [화면 1: 캐릭터 선택]
if st.session_state.game_state == "CHAR_SELECT":
    st.subheader("모험가를 선택하세요")
    selected_char = st.selectbox("캐릭터 목록", list(PRESET_CHARACTERS.keys()))
    char_data = PRESET_CHARACTERS[selected_char]

    st.info(f"**종족/직업:** {char_data['race']} / {char_data['job']}\n\n**신앙:** {char_data['god']} ({char_data['desc']})\n\n**스킬:** {', '.join(char_data['skills'])}")

    if st.button("이 캐릭터로 시작하기"):
        st.session_state.player = {
            "name": selected_char.split()[0],
            **char_data
        }
        st.session_state.death_reason = random.choice(DEATH_REASONS)
        st.session_state.game_state = "PROLOGUE"
        st.rerun()

# [화면 2: 프롤로그 (황당한 죽음)]
elif st.session_state.game_state == "PROLOGUE":
    st.subheader("💀 프롤로그: 뒤틀린 현실과 죽음")
    st.error(f"**당신의 사망 원인:** {st.session_state.death_reason}")
    st.markdown("""
    대악마가 부활을 위해 당신의 영혼을 강제로 지옥으로 끌고 왔습니다!  
    영혼이 온전히 집어삼켜지기 전에, 지옥의 7마신 혹은 찬탈자의 힘(권능)을 모아 **대악마의 봉인문**을 열고 탈출해야 합니다.
    """)
    if st.button("지옥의 입구로 눈을 뜬다"):
        st.session_state.game_state = "PLAYING"
        st.session_state.location = "S01"
        st.rerun()

# [화면 3: 메인 플레이 화면]
elif st.session_state.game_state == "PLAYING":
    loc = st.session_state.location
    p = st.session_state.player

    # 사망 체크
    if p["hp"] <= 0:
        st.error("💀 체력이 다해 쓰러졌습니다! 지옥의 성당으로 영혼이 이끌립니다...")
        st.session_state.location = "E03"
        p["hp"] = p["max_hp"] // 2
        st.rerun()

    # 최근 로그 출력
    if st.session_state.logs:
        with st.expander("📜 최근 발생한 모험 기록", expanded=False):
            for log in reversed(st.session_state.logs[-5:]):
                st.write(f"- {log}")

    # [S01: 지옥의 입구]
    if loc == "S01":
        st.subheader("📍 [S01] 지옥의 입구")
        st.write("말라 비틀어진 삭막한 땅입니다. 불빛이 새어나오지만 뜨겁지는 않습니다. 절벽과 넓은 개활지가 보입니다.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("➡️ [F01] 개활지로 나아간다"):
                change_location("F01")
                st.rerun()
        with c2:
            if st.button("🧗 [F03] 절벽을 기어오른다 (민첩 판정)"):
                if random.random() > 0.4:
                    st.success("절벽을 무사히 기어올랐습니다!")
                    change_location("F03")
                else:
                    st.error("절벽에서 미끄러졌습니다! (HP -2)")
                    p["hp"] -= 2
                st.rerun()
        with c3:
            if st.button("🔍 바닥의 균열을 조사한다"):
                st.info("영혼들의 기운이 흐르고 있습니다. [지옥과의 동화] 경험을 얻습니다.")
                if p["god"] == "선신":
                    st.session_state.god_stack += 1

    # [F01: 거대 악마(파수꾼) 조우]
    elif loc == "F01":
        st.subheader("📍 [F01] 거대 악마와의 조우")
        st.warning("쿵쿵거리는 진동과 함께 거대한 10M 크기의 악마 파수꾼이 다가옵니다!")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🏃 마수를 피해 옆길로 도망친다"):
                add_log("파수꾼을 피해 도망치던 중 신비한 마도사를 만났습니다.")
                change_location("F02")
                st.rerun()
        with c2:
            if st.button("⚔️ 정면으로 맞서 싸운다 (위험)"):
                st.error("압도적인 파수꾼의 일격에 큰 부상을 입었습니다! (HP -5)")
                p["hp"] -= 5
                if p["hp"] > 0:
                    st.warning("노병 크루세이더가 나타나 당신을 구출하고 기사의 집으로 데려갑니다!")
                    change_location("F06")
                st.rerun()
        with c3:
            if st.button("🔙 입구로 후퇴한다"):
                change_location("S01")
                st.rerun()

    # [F02: 마도사의 조우]
    elif loc == "F02":
        st.subheader("📍 [F02] 마도사와의 조우")
        st.write("고깔모자를 쓴 뿔 달린 마도사가 흥미로운 눈빛으로 당신을 바라봅니다.")
        st.info("'너, 온전한 지옥의 영혼이 아니구나? 우리 연구소로 가볼래?'")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 [F08] 마도사를 따라 집으로 간다"):
                change_location("F08")
                st.rerun()
        with c2:
            if st.button("🌲 [F32] 검은 숲 쪽으로 방향을 튼다"):
                change_location("F32")
                st.rerun()

    # [F08: 마도사의 집 (연구실)]
    elif loc == "F08":
        st.subheader("📍 [F08] 마도사와 연금술사의 집")
        st.write("따뜻하게 마법으로 조절된 방 안에 늙은 엘프 연금술사가 연구 중입니다.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧪 연금술사에게 비상 포션 받기"):
                if "회복 포션" not in st.session_state.inventory:
                    st.session_state.inventory.append("회복 포션")
                    st.success("연금술사가 여정에 도움이 될 **회복 포션**을 건네주었습니다!")
                else:
                    st.info("이미 포션을 받았습니다.")
        with c2:
            if st.button("🚪 밖으로 나가 [F22] 해골 마을로 이동"):
                change_location("F22")
                st.rerun()

    # [F22 / F23: 해골 마을]
    elif loc == "F22":
        st.subheader("📍 [F23] 해골들의 마을")
        st.write("무해한 해골들이 모여 사는 평화로운 마을입니다. 해골 문지기가 입구를 지키고 있습니다.")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💀 해골들과 잡담 및 주사위 놀이하기"):
                st.success("해골들과 즐거운 시간을 보냈습니다. 영혼이 안정됩니다. (HP +3 회복)")
                p["hp"] = min(p["max_hp"], p["hp"] + 3)
                if p["god"] == "선신":
                    st.session_state.god_stack += 1
        with c2:
            if st.button("🛍️ 해골 상점 구경하기"):
                if "조악한 낚싯대" not in st.session_state.inventory:
                    st.session_state.inventory.append("조악한 낚싯대")
                    st.success("**조악한 낚싯대**를 무료로 얻었습니다!")
        with c3:
            if st.button("🌊 [F26] 낚시터(나태의 영역)로 이동"):
                change_location("F26")
                st.rerun()

    # [F26: 낚시터 - 나태의 마신]
    elif loc == "F26":
        st.subheader("📍 [F26] 잔잔한 낚시터")
        st.write("오두막 그늘 아래서 산발 머리를 한 **나태의 마신**이 쿨쿨 자고 있습니다.")

        c1, c2, c3 = st.columns(3)
        with c1:
            if "나태의 권능" not in st.session_state.powers:
                if st.button("😴 마신이 깰 때까지 묵묵히 기다려준다"):
                    st.success("푹 자고 일어난 나태의 마신이 흐뭇해하며 **[나태의 권능]**을 부여했습니다!")
                    st.session_state.powers.append("나태의 권능")
                    st.rerun()
            else:
                st.caption("이미 나태의 권능을 획득했습니다.")
        with c2:
            if "조악한 낚싯대" in st.session_state.inventory:
                if st.button("🎣 바다에서 낚시하기"):
                    fish = random.choice(["잡어", "망각어", "혈석 1개"])
                    if fish == "혈석 1개":
                        st.session_state.bloodstones += 1
                        st.success("💎 낚싯대로 **혈석**을 낚아 올렸습니다!")
                    else:
                        st.session_state.inventory.append(fish)
                        st.success(f"🐟 **{fish}**을(를) 낚았습니다!")
        with c3:
            if st.button("🚪 [E05] 봉인된 문(최종 결전지)으로 이동"):
                change_location("E05")
                st.rerun()

    # [E03: 지옥의 성당 (교만의 마신)]
    elif loc == "E03":
        st.subheader("📍 [E03] 지옥의 성당")
        st.write("붉은 빛이 감도는 성당 안에서 수녀 복장을 한 **교만의 마신**이 당신을 내려다봅니다.")
        st.info("'참 한심한 영혼이네... 또 쓰러졌어?'")

        if "교만의 권능" not in st.session_state.powers:
            if st.button("🙇 교만의 마신에게 권능을 청한다"):
                st.session_state.powers.append("교만의 권능")
                st.success("교만의 마신이 혀를 차며 **[교만의 권능]**을 내려주었습니다.")
                st.rerun()
        if st.button("🚪 성당 밖으로 나가기"):
            change_location("S01")
            st.rerun()

    # [E05: 최종 봉인문 & 대악마]
    elif loc == "E05":
        st.subheader("📍 [E05] 대악마의 거대한 봉인문")
        st.write(f"현재 보유한 마신의 권능: **{len(st.session_state.powers)}개**")

        if len(st.session_state.powers) >= 2:
            st.success("봉인문에 마신의 힘이 공명하여 거대한 문이 열립니다!")
            if st.button("🔥 대악마와의 최종 결전에 돌입한다"):
                st.session_state.game_state = "BOSS_BATTLE"
                st.rerun()
        else:
            st.error("검은 안개가 길을 막고 있습니다! (최소 2개 이상의 마신 권능이 필요합니다)")
            if st.button("🔙 지옥 입구로 돌아간다"):
                change_location("S01")
                st.rerun()

# [화면 4: 최종 보스전]
elif st.session_state.game_state == "BOSS_BATTLE":
    st.subheader("🔥 [최종전] 권흉의 대악마")
    st.write("당신을 지옥으로 끌고 온 대악마가 거대한 화염을 뿜으며 나타났습니다!")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("👑 모아온 마신의 권능을 일제히 개방한다!"):
            st.balloons()
            st.session_state.game_state = "ENDING"
            st.rerun()
    with c2:
        if st.button("⚔️ 맨몸으로 돌격한다"):
            st.error("대악마의 암흑 브레스에 영혼이 산산조각 났습니다...")
            st.session_state.player["hp"] = 0
            st.session_state.game_state = "PLAYING"
            st.session_state.location = "E03"
            st.rerun()

# [화면 5: 엔딩]
elif st.session_state.game_state == "ENDING":
    st.balloons()
    st.success("🎉 **[탈출 성공: 현실 귀환 엔딩]**")
    st.markdown(f"""
    마신들의 힘이 대악마를 다시 깊은 심연 속으로 봉인했습니다.  
    
    뒤틀렸던 현실의 운명이 제자리로 돌아오며, **{st.session_state.player['name']}**님은 황당한 죽음의 위기를 벗어나 원래의 평화로운 일상으로 돌아왔습니다!
    """)
    if st.button("🔄 처음부터 다시 플레이하기"):
        st.session_state.game_state = "CHAR_SELECT"
        st.session_state.player = None
        st.session_state.powers = []
        st.session_state.logs = []
        st.session_state.inventory = []
        st.rerun()