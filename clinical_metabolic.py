"""Educational Korean-adult metabolic syndrome component screening; not a diagnosis."""
from dataclasses import dataclass
from math import isfinite

FIELDS = {
    'waist': ('허리둘레', 'cm', 35, 220, '35~220'),
    'tg': ('중성지방(TG)', 'mg/dL', 10, 2000, '10~2000'),
    'hdl': ('HDL 콜레스테롤', 'mg/dL', 5, 200, '5~200'),
    'sbp': ('수축기 혈압', 'mmHg', 50, 300, '50~300'),
    'dbp': ('이완기 혈압', 'mmHg', 25, 200, '25~200'),
    'glucose': ('공복혈당', 'mg/dL', 20, 700, '20~700'),
}
SOURCES = [
    '대한비만학회: 한국인 복부비만 기준(남성 90cm 이상, 여성 85cm 이상) — https://www.kosso.or.kr/',
    '대한당뇨병학회: 당뇨병 진료지침 및 공복혈당 평가 — https://www.diabetes.or.kr/',
    '국민건강보험공단: 국가건강검진 및 대사증후군 안내 — https://www.nhis.or.kr/',
    '2009 Joint Interim Statement: Harmonizing the Metabolic Syndrome (Alberti et al., Circulation, 2009).',
]

# Educational associations, not diagnoses. Only include findings supported by entered values.
HEALTH_ASSOCIATIONS = {
    '복부비만': ('복부비만 및 대사 건강', '허리둘레 증가가 확인되었습니다. 복부 지방 축적은 인슐린 저항성 및 제2형 당뇨병과 관련될 수 있습니다.', '허리둘레 측정 방법과 생활습관을 확인하고 필요하면 의료진과 상담하세요.'),
    '중성지방 상승': ('중성지방 증가 및 이상지질혈증 관련 소견', '중성지방 상승이 확인되었습니다. 이상지질혈증과 관련될 수 있으며, 수치가 매우 높다면 별도의 의학적 평가가 필요합니다.', '공복 여부와 지질 검사 결과를 확인하고 필요하면 재검사 및 진료를 상담하세요.'),
    'HDL 감소': ('낮은 HDL 콜레스테롤', 'HDL 콜레스테롤 감소가 확인되었습니다. 다른 대사 위험인자와 함께 나타날 수 있으며 심혈관 건강과 관련됩니다.', '다른 지질 수치와 생활습관을 함께 점검하세요.'),
    '혈압 상승': ('혈압 상승 및 고혈압 가능성', '측정된 혈압이 대사증후군 구성요소 기준에 해당합니다. 고혈압 여부는 반복 측정과 진료를 통해 확인해야 합니다.', '안정된 상태에서 혈압을 다시 측정하고 지속적으로 높으면 진료를 상담하세요.'),
    '공복혈당 상승': ('혈당 조절 이상 및 당뇨병 전단계 가능성', '공복혈당이 대사증후군 구성요소 기준에 해당합니다. 수치에 따라 당뇨병 전단계 또는 당뇨병 평가가 필요할 수 있지만 한 번의 검사로 확진할 수 없습니다.', '공복 상태를 확인하고 HbA1c 또는 반복 공복혈당 검사 필요성을 상담하세요.'),
}

def related_health_findings(components):
    """Build transparent, component-specific associations without inferring diagnoses."""
    findings = []
    for component in components:
        if component.status == '해당' and component.name in HEALTH_ASSOCIATIONS:
            title, meaning, followup = HEALTH_ASSOCIATIONS[component.name]
            findings.append({'component': component.name, 'title': title,
                             'meaning': meaning, 'followup': followup,
                             'value': component.display})
    return findings

@dataclass
class Component:
    name: str
    display: str
    criterion: str
    status: str  # 해당 / 미해당 / 판정 보류
    reason: str


def validate(values, age, sex):
    errors = []
    if not 19 <= age <= 120:
        errors.append('이 버전은 만 19세 이상 성인용입니다. 나이를 확인해 주세요.')
    if sex not in ('남성', '여성', '미선택'):
        errors.append('성별 입력값을 확인해 주세요.')
    for key, val in values.items():
        if val is None:
            continue
        if key not in FIELDS:
            errors.append(f'지원하지 않는 검사 항목: {key}')
            continue
        label, unit, lo, hi, _ = FIELDS[key]
        if not isfinite(val) or not lo <= val <= hi:
            errors.append(f'{label}: 입력 허용 범위 {lo}~{hi} {unit}를 확인해 주세요. (정상범위가 아닌 오타 검사용)')
    if values.get('sbp') is not None and values.get('dbp') is not None and values['sbp'] <= values['dbp']:
        errors.append('수축기 혈압은 이완기 혈압보다 커야 합니다.')
    return errors


def evaluate(values, *, sex, fasting, bp_treatment=False, lipid_treatment=False,
             glucose_treatment=False, pregnant=False, urgent_symptom=False):
    """Returns component-based screening, preserving unknowns; treatments need clinical review."""
    components = []
    def add(name, keys, criterion, flag, reason=''):
        present = all(values.get(k) is not None for k in keys)
        display = ' / '.join(f'{values[k]:g} {FIELDS[k][1]}' for k in keys if values.get(k) is not None) or '미입력'
        if flag is True:
            status = '해당'
        elif flag is False:
            status = '미해당'
        else:
            status = '판정 보류'
        components.append(Component(name, display, criterion, status, reason))

    waist = values.get('waist')
    if waist is None or sex == '미선택' or pregnant:
        wflag = None
        wreason = '허리둘레·성별 정보가 필요합니다.' if not pregnant else '임신 중 허리둘레 기준은 적용하지 않습니다.'
    else:
        wflag = waist >= (90 if sex == '남성' else 85)
        wreason = '한국 성인 복부비만 기준과 비교했습니다.'
    add('복부비만', ['waist'], '남성 ≥90cm / 여성 ≥85cm', wflag, wreason)

    tg = values.get('tg')
    # Treatment indication alone is not sufficient to infer the exact medication or indication.
    add('중성지방 상승', ['tg'], '≥150 mg/dL', None if tg is None else tg >= 150,
        '지질 치료 중이라면 정상 수치라도 치료 전 기록을 확인해야 합니다.' if lipid_treatment else '')
    hdl = values.get('hdl')
    hflag = None if hdl is None or sex == '미선택' else hdl < (40 if sex == '남성' else 50)
    add('HDL 감소', ['hdl'], '남성 <40 / 여성 <50 mg/dL', hflag,
        '성별 정보가 있어야 판정할 수 있습니다.' if sex == '미선택' else '')

    sbp, dbp = values.get('sbp'), values.get('dbp')
    bpflag = None if sbp is None or dbp is None else (sbp >= 130 or dbp >= 85)
    add('혈압 상승', ['sbp', 'dbp'], '수축기 ≥130 또는 이완기 ≥85 mmHg', bpflag,
        '혈압약을 복용 중이면 수치가 기준 미만이어도 관련 치료 이력을 확인해야 합니다.' if bp_treatment else '두 혈압값을 모두 입력해야 판정합니다.')

    glucose = values.get('glucose')
    gflag = None if glucose is None or fasting is not True else glucose >= 100
    add('공복혈당 상승', ['glucose'], '8시간 이상 금식 후 ≥100 mg/dL', gflag,
        '공복 여부를 확인해야 합니다.' if fasting is not True else ('혈당 치료 중이면 이전 검사 및 치료 이력을 확인해야 합니다.' if glucose_treatment else ''))

    yes = sum(c.status == '해당' for c in components)
    unknown = sum(c.status == '판정 보류' for c in components)
    possible = yes + unknown
    # Classification uses three user-facing groups only when all five components
    # are evaluable. With missing data, never describe unmeasured factors as normal.
    if urgent_symptom:
        category = 'incomplete'
        level = '응급 증상 우선 평가'
        summary = '응급 증상이 의심되면 대사증후군 판정보다 신속한 의료 평가가 우선입니다.'
    elif yes >= 3:
        category = 'consult'
        level = '의료진 상담 권장'
        summary = f'5가지 대사증후군 구성요소 중 {yes}개가 기준에 해당합니다. 대사증후군 가능성이 있으므로 의료진과 상담해 전문적인 평가 및 관리 계획을 세우는 것이 좋습니다.'
    elif unknown:
        category = 'incomplete'
        level = '추가 확인 필요'
        summary = f'현재 확인된 위험인자는 {yes}개이고, {unknown}개는 판정 보류입니다. 누락된 검사값을 정상으로 가정할 수 없어 전체 판정은 보류합니다.'
    elif yes == 0:
        category = 'normal'
        level = '현재 결과 양호'
        summary = '5가지 대사증후군 구성요소 모두 기준에 해당하지 않습니다. 현재 검사 결과는 양호하며 건강한 생활습관을 유지하는 것이 좋습니다.'
    else:
        category = 'manage'
        level = '생활습관 관리 권장'
        summary = f'5가지 구성요소 중 {yes}개가 기준에 해당합니다. 대사증후군의 3개 이상 기준에는 미치지 않지만, 해당 위험인자에 대한 관리와 추적 관찰이 권장됩니다.'
    if pregnant:
        summary += ' 임신 중에는 일반 성인 대사증후군 기준의 적용이 제한됩니다.'
    if bp_treatment or lipid_treatment or glucose_treatment:
        summary += ' 약물치료 중이라면 검사 수치만으로 구성요소를 배제하기 어려울 수 있습니다.'
    return dict(components=components, findings=related_health_findings(components), yes=yes, unknown=unknown, possible=possible,
                level=level, category=category, summary=summary, urgent=urgent_symptom,
                treatment_review=bp_treatment or lipid_treatment or glucose_treatment)
