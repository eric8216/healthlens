"""HealthLens v10: minimal metabolic syndrome educational screening."""
from datetime import date
import streamlit as st
from clinical_metabolic import FIELDS, SOURCES, evaluate, validate

st.set_page_config(page_title='HealthLens | 대사증후군 분석', page_icon='💜', layout='wide')
st.markdown('''<style>
:root {color-scheme:light!important}
html,body,[data-testid="stAppViewContainer"],.stApp {background:#fafaff!important;color:#20294b!important}
[data-testid="stHeader"] {background:#fafaff!important}
.block-container {max-width:1120px;padding-top:1.5rem}
h1,h2,h3,p,label,span {color:inherit}
.hero {padding:36px 32px;border-radius:22px;background:linear-gradient(115deg,#eeecff,#f6f8ff);border:1px solid #dcdaf7;margin:16px 0 25px}
.hero h1 {color:#24265e;font-size:clamp(34px,5vw,55px);margin:8px 0}
.hero p {color:#4b557b;font-size:18px}
.panel {padding:17px 20px;border:1px solid #dedff1;border-radius:16px;background:white;margin:10px 0}
.small-note {font-size:14px;color:#505a79}
/* Explicit light theme on every BaseWeb input layer, including focus/disabled/hover states. */
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"],
[data-baseweb="textarea"],[data-baseweb="input"] > div,[data-baseweb="select"] > div,
[data-baseweb="base-input"] > div,[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stDateInput"] input {background-color:#ffffff!important;color:#20294b!important;border-color:#b9bed6!important;caret-color:#20294b!important;-webkit-text-fill-color:#20294b!important}
input,textarea,[role="combobox"],[role="listbox"],[role="option"] {color:#20294b!important;-webkit-text-fill-color:#20294b!important}
input::placeholder,textarea::placeholder {color:#68738c!important;opacity:1!important;-webkit-text-fill-color:#68738c!important}
[data-baseweb="select"] *,[data-baseweb="input"] *,[data-testid="stWidgetLabel"] *,
[data-testid="stCheckbox"] *,[data-testid="stRadio"] * {color:#20294b!important;-webkit-text-fill-color:#20294b!important}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[role="option"],
[data-baseweb="popover"] *,[data-baseweb="menu"] * {background:#ffffff!important;color:#20294b!important;-webkit-text-fill-color:#20294b!important}
[data-testid="stExpander"], [data-testid="stExpander"] details,[data-testid="stExpander"] summary,
[data-testid="stExpander"] details>div,[data-testid="stForm"] {background:#ffffff!important;color:#20294b!important}
[data-testid="stExpander"] summary *,[data-testid="stExpander"] p {color:#20294b!important;-webkit-text-fill-color:#20294b!important}
[data-testid="stAlert"] {background:#f0f2ff!important;color:#20294b!important}
[data-testid="stAlert"] *,[data-testid="stAlert"] p {color:#20294b!important;-webkit-text-fill-color:#20294b!important}
.stButton>button,.stFormSubmitButton>button {background:#fff!important;color:#29325a!important;border:1px solid #bfc1dd!important;border-radius:12px;min-height:52px;height:auto!important;padding:12px 16px!important;line-height:1.5!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:visible!important}
.stButton>button *, .stFormSubmitButton>button * {line-height:1.5!important;overflow:visible!important;color:inherit!important;-webkit-text-fill-color:currentColor!important}
.stButton>button:hover {background:#f0edff!important;color:#35277d!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {background:#6754ca!important;color:#fff!important;border-color:#6754ca!important}
.stButton>button[kind="primary"] *,.stFormSubmitButton>button[kind="primary"] * {color:#fff!important;-webkit-text-fill-color:#fff!important}
@media(max-width:700px){.hero{padding:22px 18px}.block-container{padding-left:1rem;padding-right:1rem}}
</style>''', unsafe_allow_html=True)

COMPONENT_EXPLANATIONS = {
    '복부비만': '허리둘레는 복부에 지방이 집중된 정도를 간접적으로 보여주는 지표입니다.',
    '중성지방 상승': '중성지방은 혈액 속 지방 성분으로, 높은 수치는 대사 건강과 관련이 있습니다.',
    'HDL 감소': 'HDL은 혈관 건강과 관련된 콜레스테롤로, 수치가 낮으면 대사증후군 구성요소에 해당할 수 있습니다.',
    '혈압 상승': '혈압은 혈액이 혈관 벽에 가하는 압력이며, 수축기 또는 이완기 혈압이 높으면 해당합니다.',
    '공복혈당 상승': '공복혈당은 일정 시간 금식한 뒤 측정한 혈당으로, 높은 수치는 혈당 조절 이상과 관련이 있습니다.',
}

if 'page' not in st.session_state:
    st.session_state.page = 'home'

def navigate(page):
    st.session_state.page = page
    st.rerun()

brand, nav1, nav2 = st.columns([3,1,2],vertical_alignment='center')
with brand:
    st.markdown('### 💜 HealthLens')
with nav1:
    if st.button('⌂ 홈',use_container_width=True): navigate('home')
with nav2:
    if st.button('🔎 대사증후군 분석',use_container_width=True): navigate('analysis')
st.divider()

if st.session_state.page == 'home':
    st.markdown('''<div class="hero"><div style="color:#6754ca;font-weight:700">✦ 건강검진 결과 이해 도우미 · 교육용</div><h1>HealthLens</h1><p>검사 수치 6개로 대사증후군 관련 5가지 구성요소를 살펴보세요.</p><p>✓ 간단한 입력 &nbsp; ✓ 연관 수치 분석 &nbsp; ✓ 알기 쉬운 결과</p></div>''',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3>🔎 대사증후군 검사 결과 해석하기</h3><p>허리둘레, 혈압, 중성지방, HDL 콜레스테롤, 공복혈당을 종합적으로 비교합니다.</p></div>',unsafe_allow_html=True)
    if st.button('지금 시작하기 →',type='primary',use_container_width=True): navigate('analysis')
    st.caption('교육용 시연 서비스입니다. 실제 건강정보 대신 가상 데이터를 사용하세요. 의료진의 진단을 대신하지 않습니다.')
    st.stop()

st.title('🔎 대사증후군 가능성 분석')
st.write('**이 검사는 대사증후군의 가능성을 판단합니다.** 한국 성인 기준의 5개 구성요소를 비교하며, 입력하지 않은 값은 정상으로 간주하지 않습니다.')


with st.form('metabolic_form'):
    st.subheader('1. 기본 정보')
    a,b,c=st.columns(3)
    with a:
        age=st.number_input('나이 (만 나이, 성인)',min_value=19,max_value=120,value=35)
    with b:
        sex=st.selectbox('성별 (허리둘레·HDL 기준 적용)',['미선택','남성','여성'])
    with c:
        fasting=st.selectbox('혈당 검사 전 8시간 이상 금식',['모름/미입력','예','아니요'])
    st.caption('만 19세 이상 성인용입니다. 임신 중에는 별도의 의학적 평가가 필요합니다.')
    st.subheader('2. 검사 수치 입력')
    st.caption('입력칸의 숫자 범위는 입력 가능한 값의 예시이며, 정상 판정 기준이 아닙니다. 빈칸은 판정 보류입니다.')
    values={};parse_errors=[]
    groups=[('① 복부비만',['waist']),('② 지질 검사',['tg','hdl']),('③ 혈압',['sbp','dbp']),('④ 혈당 검사',['glucose'])]
    for title,keys in groups:
        with st.expander(title,expanded=True):
            cols=st.columns(2)
            for i,key in enumerate(keys):
                label,unit,lo,hi,example=FIELDS[key]
                with cols[i%2]:
                    raw=st.text_input(f'{label} ({unit})',placeholder=f'{lo}~{hi}',key=f'm_{key}',help=f'입력 허용 범위: {lo}~{hi} {unit}. 정상범위가 아닌 오타 검사용 범위입니다.')
                    if not raw.strip():
                        values[key]=None
                    else:
                        try: values[key]=float(raw.strip())
                        except ValueError:
                            values[key]=None
                            parse_errors.append(f'{label}: 숫자로 입력해 주세요. (예: 120)')
    ack=st.checkbox('이 결과는 교육용 참고이며 의료진의 진단을 대신하지 않음을 이해했습니다.')
    submitted=st.form_submit_button('대사증후군 가능성 분석하기',type='primary',use_container_width=True)

if submitted:
    errors=parse_errors+validate(values,age,sex)
    if all(v is None for v in values.values()): errors.append('최소 한 가지 검사 수치를 입력해 주세요.')
    if not ack: errors.append('교육용 안내 확인에 체크해 주세요.')
    if errors:
        st.session_state.pop('metabolic_report',None)
        for err in errors: st.error(err)
    else:
        st.session_state.metabolic_report=evaluate(values,sex=sex,fasting={'예':True,'아니요':False}.get(fasting))

if 'metabolic_report' in st.session_state:
    result=st.session_state.metabolic_report
    st.divider()
    st.header('A. 대사증후군 가능성 판정')
    st.caption('허리둘레·중성지방·HDL·혈압·공복혈당의 5가지 구성요소 중 기준에 해당하는 항목을 확인합니다. 3개 이상이면 대사증후군 기준에 해당할 가능성이 있습니다.')
    if result['category'] == 'consult':
        st.error('🔴 대사증후군 기준에 해당할 가능성이 있습니다 · 의료진 상담 권장')
    elif result['category'] == 'manage':
        st.warning('🟡 대사 관련 위험인자가 확인되었습니다 · 생활습관 관리 권장')
    elif result['category'] == 'normal':
        st.success('🟢 5가지 구성요소 모두 기준 미해당 · 현재 결과는 양호합니다')
    else:
        st.info('🔵 일부 검사 정보가 부족합니다 · 추가 확인 필요')
    m1,m2,m3=st.columns(3)
    m1.metric('기준 해당 항목',f"{result['yes']} / 5",help='대사증후군의 5개 구성요소 중 판정 기준을 충족한 항목 수')
    m2.metric('판정 보류 항목',f"{result['unknown']} / 5",help='검사값이나 검사 조건이 부족해 판단할 수 없는 항목 수')
    m3.metric('최대 해당 가능 항목',f"{result['possible']} / 5",help='현재 해당 항목 수와 판정 보류 항목 수의 합. 질병 발생 확률이 아닙니다.')
    st.caption('기준 해당: 판정 기준을 충족한 개수 · 판정 보류: 정보가 부족한 개수 · 최대 해당 가능: 보류 항목이 모두 해당할 경우의 개수')
    st.write(result['summary'])
    st.header('B. 대사증후군 5가지 구성요소별 판정')
    st.caption('각 항목을 펼치면 입력값, 판정 기준과 검사 지표의 의미를 확인할 수 있습니다.')
    for c in result['components']:
        symbol={'해당':'⚠️','미해당':'✅','판정 보류':'❔'}[c.status]
        with st.expander(f'{symbol} {c.name} — {c.status}',expanded=c.status!='미해당'):
            st.write('**입력값:** '+c.display)
            st.write('**판정 기준:** '+c.criterion)
            st.write('**이 항목의 의미:** '+COMPONENT_EXPLANATIONS[c.name])
            if c.reason:st.write('**참고:** '+c.reason)
    st.header('C. 결과에 따른 건강 관리 안내')
    if result['category'] == 'consult':
        st.error('**의료진의 전문적인 평가와 관리가 권장됩니다.**')
        st.write('**관련 건강 문제:** 아래 내용은 실제로 기준에 해당한 검사 항목을 바탕으로 작성되었습니다. 여러 대사 위험인자가 함께 존재하면 장기적으로 제2형 당뇨병 및 심혈관질환 발생 위험과 관련될 수 있어 전문적인 평가가 중요합니다.')
        for finding in result['findings']:
            st.markdown(f"**• {finding['title']}** ({finding['component']}: {finding['value']})")
            st.write(finding['meaning'])
            st.caption('추가 확인: ' + finding['followup'])
        st.write('**권고:** 내과 또는 가정의학과에서 검사 결과를 확인하고, 필요한 추가 검사와 개인별 관리 계획을 상담하세요. 현재 수치만으로 특정 질환이나 합병증을 확진할 수는 없습니다.')
    elif result['category'] == 'manage':
        st.warning('**일부 대사 위험인자가 확인되어 관리가 필요합니다.**')
        st.write('**권고:** 해당 수치의 추적 검사와 식사·활동·수면 등 생활습관을 점검하세요. 이상 수치가 지속되면 의료진과 상담하는 것이 좋습니다.')
        if result['findings']:
            st.write('**확인된 항목과 관련된 건강 문제**')
            for finding in result['findings']:
                st.markdown(f"**• {finding['title']}** ({finding['component']}: {finding['value']})")
                st.write(finding['meaning'])
                st.caption('추가 확인: ' + finding['followup'])
    elif result['category'] == 'normal':
        st.success('**현재 입력된 5가지 구성요소는 모두 기준에 해당하지 않습니다.**')
        st.write('**권고:** 현재의 건강한 생활습관을 유지하고 정기적으로 건강검진을 받으세요. 정상 판정이 모든 질환이 없다는 의미는 아닙니다.')
    else:
        st.info('**판정에 필요한 정보가 부족합니다.**')
        st.write('**권고:** 미입력 항목, 성별 정보 및 공복 여부를 확인한 뒤 다시 분석하세요. 확인된 이상 항목이 있다면 그 수치는 별도로 관리해야 합니다.')
        if result['findings']:
            st.write('**현재 확인된 항목 관련 건강 문제 (전체 판정은 보류)**')
            for finding in result['findings']:
                st.markdown(f"**• {finding['title']}** ({finding['component']}: {finding['value']})")
                st.write(finding['meaning'])
    if result['unknown']:
        st.write(f"**미확인 항목:** {result['unknown']}개. 미입력 항목은 정상으로 계산하지 않았습니다.")
    st.caption('이 도구는 검사 수치만을 이용한 교육용 선별 프로그램입니다. 치료로 조절된 수치는 반영되지 않으며, 약물 복용 여부를 확인하지 않아 실제 임상 판정과 차이가 날 수 있습니다. 응급 증상이 있으면 검사 결과와 무관하게 119 등 응급의료 도움을 받으세요.')
    with st.expander('기준 출처 및 구현 한계'):
        for source in SOURCES:st.write('• '+source)
        st.write('본 프로그램은 한국 성인의 교육용 대사증후군 구성요소 선별 도구입니다. 약물치료 여부와 치료 전 수치, 검사실 조건을 확인하지 않으므로 임상 진단을 대신하지 않습니다. 임신 중에는 별도 평가가 필요합니다.')
        st.write('외부 생성형 AI API, 파일 저장, 데이터베이스 전송을 사용하지 않습니다. Streamlit 실행 환경의 로그 및 세션 관리는 별도 운영 정책에 따릅니다.')
