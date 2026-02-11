import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image, ImageDraw
import random
from pathlib import Path

# -----------------------------
# (A) 1) 키워드 + 레벨 구조 + 가중치 설계
# -----------------------------
# 레벨별 기본 점수(base_weight)를 크게 설정해 "중앙>근처>바깥" 구조를 만듭니다.
# 그 위에 각 키워드에 "importance"를 0.6~1.4 정도로 곱해 미세 조정합니다.

keywords = [
    # Level 1: Core (중앙)
    ("SKKU PEPV", "Core", 1.40),
    ("Pharmacoepidemiology", "Core", 1.30),
    ("Drug Safety", "Core", 1.20),
    ("Real-World Evidence", "Core", 1.10),

    # Level 2: Primary Clinical Areas (중앙 근처)
    ("Cardiovascular Disease", "Primary", 1.15),
    ("Metabolic Disorders", "Primary", 1.10),
    ("Diabetes", "Primary", 1.10),
    ("Mental Health", "Primary", 1.05),
    ("Neuropsychiatry", "Primary", 1.00),
    ("Methodology", "Primary", 1.20),

    # Level 3: Secondary - Drugs
    ("SGLT2 inhibitors", "Secondary", 1.15),
    ("GLP-1 receptor agonists", "Secondary", 1.10),
    ("DPP-4 inhibitors", "Secondary", 0.95),
    ("DOACs", "Secondary", 0.90),
    ("ADHD medications", "Secondary", 0.85),
    ("COVID-19 vaccines", "Secondary", 0.95),

    # Level 3: Secondary - Outcomes
    ("MACE", "Secondary", 1.05),
    ("Bleeding", "Secondary", 0.85),
    ("Acute Kidney Injury", "Secondary", 0.90),
    ("Adverse Drug Reactions", "Secondary", 0.95),

    # Level 3: Secondary - Methods (Methodology를 한 번 더 강조하고 싶으면 여기서도 넣기)
    ("Immeasurable time bias", "Secondary", 1.00),
    ("Marginal structural models", "Secondary", 1.10),
    ("Clone-censor weight", "Secondary", 1.05),
    ("Target trial emulation", "Secondary", 1.10),

    # Level 3: Value
    ("RWE", "Secondary", 0.95),
]

# 레벨별 기본 가중치 (핵심 아이디어)
level_base = {
    "Core": 240,
    "Primary": 140,
    "Secondary": 80,
}

# 최종 weight 계산
records = []
for term, level, importance in keywords:
    w = level_base[level] * importance
    records.append((term, level, importance, round(w, 1)))

df = pd.DataFrame(records, columns=["term", "level", "importance", "weight"])
# wordcloud는 dict 형태의 (word: weight)를 받음
freq = dict(zip(df["term"], df["weight"]))

# -----------------------------
# (B) 2) 원형 마스크 만들기 (원 밖에는 단어 배치 금지)
# -----------------------------
def make_circle_mask(size=1200, margin=30):
    img = Image.new("L", (size, size), 0)  # 0=검정(배치 금지), 255=흰색(배치 가능)
    draw = ImageDraw.Draw(img)
    draw.ellipse(
        (margin, margin, size - margin, size - margin),
        fill=255
    )
    return np.array(img)

mask = make_circle_mask(size=1400, margin=40)

# -----------------------------
# (C) 3) 워드클라우드 생성 파라미터
# -----------------------------
# prefer_horizontal을 높이면 읽기 좋아지고,
# random_state를 고정하면 결과 재현 가능
wc = WordCloud(
    width=1400,
    height=1400,
    background_color=None,          # 투명 배경
    mode="RGBA",
    mask=mask,
    prefer_horizontal=0.92,
    min_font_size=10,
    max_font_size=180,
    relative_scaling=0.45,          # weight 차이를 폰트에 반영하는 강도
    collocations=False,
    random_state=42,
)

# -----------------------------
# (D) 4) '원형 링 구조' 느낌 강화 옵션
# -----------------------------
# WordCloud 기본은 weight 기반으로 크기만 조절되고 위치는 랜덤입니다.
# 링 구조 느낌을 더 내려면:
#  - Core/Primary를 크게(이미 반영)
#  - rotation 줄이기(가독성)
#  - 단어 수 줄이고 여백 확보
# 정도가 가장 안정적입니다.

wc.generate_from_frequencies(freq)

# -----------------------------
# (E) 5) 저장 (PNG + weight table CSV)
# -----------------------------
out_dir = Path("wordcloud_output")
out_dir.mkdir(exist_ok=True)

# 투명 배경
transparent_path = out_dir / "wordcloud_circle_transparent.png"
wc.to_file(str(transparent_path))

# 흰 배경 버전
plt.figure(figsize=(8, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()

white_path = out_dir / "wordcloud_circle_white.png"
plt.savefig(white_path, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()

# 가중치 표 저장
csv_path = out_dir / "wordcloud_weights.csv"
df.sort_values(["level", "weight"], ascending=[True, False]).to_csv(csv_path, index=False, encoding="utf-8-sig")

print("Saved:")
print(" -", transparent_path)
print(" -", white_path)
print(" -", csv_path)
