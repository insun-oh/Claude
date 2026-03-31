import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# -----------------------------
# (A) 키워드 + 레벨 구조 + 가중치 설계 (대폭 확장)
# -----------------------------
keywords = [
    # ===== Level 1: Core =====
    ("SKKU PEPV", "Core", 1.40),
    ("Pharmacoepidemiology", "Core", 1.35),
    ("Drug Safety", "Core", 1.25),
    ("Real-World Evidence", "Core", 1.15),
    ("Pharmacovigilance", "Core", 1.10),

    # ===== Level 2: Primary Clinical Areas =====
    ("Cardiovascular Disease", "Primary", 1.20),
    ("Metabolic Disorders", "Primary", 1.15),
    ("Diabetes", "Primary", 1.15),
    ("Mental Health", "Primary", 1.10),
    ("Neuropsychiatry", "Primary", 1.05),
    ("Methodology", "Primary", 1.25),
    ("Oncology", "Primary", 1.00),
    ("Infectious Disease", "Primary", 1.05),
    ("Respiratory Disease", "Primary", 0.95),
    ("Renal Disease", "Primary", 0.95),

    # ===== Level 3: Secondary - Drug Classes =====
    ("SGLT2 inhibitors", "Secondary", 1.20),
    ("GLP-1 receptor agonists", "Secondary", 1.15),
    ("DPP-4 inhibitors", "Secondary", 1.00),
    ("DOACs", "Secondary", 0.95),
    ("ADHD medications", "Secondary", 0.90),
    ("COVID-19 vaccines", "Secondary", 1.00),
    ("Statins", "Secondary", 0.95),
    ("ACE inhibitors", "Secondary", 0.90),
    ("ARBs", "Secondary", 0.85),
    ("Beta-blockers", "Secondary", 0.85),
    ("Insulin", "Secondary", 0.90),
    ("Metformin", "Secondary", 0.95),
    ("Antipsychotics", "Secondary", 0.90),
    ("Antidepressants", "Secondary", 0.85),
    ("NSAIDs", "Secondary", 0.85),
    ("Opioids", "Secondary", 0.80),
    ("Immunosuppressants", "Secondary", 0.85),
    ("Anticoagulants", "Secondary", 0.90),
    ("Proton pump inhibitors", "Secondary", 0.80),
    ("Biologics", "Secondary", 0.85),

    # ===== Level 3: Secondary - Outcomes =====
    ("MACE", "Secondary", 1.10),
    ("Bleeding", "Secondary", 0.90),
    ("Acute Kidney Injury", "Secondary", 0.95),
    ("Adverse Drug Reactions", "Secondary", 1.00),
    ("Heart Failure", "Secondary", 0.95),
    ("Stroke", "Secondary", 0.90),
    ("Myocardial Infarction", "Secondary", 0.95),
    ("Mortality", "Secondary", 1.00),
    ("Hospitalization", "Secondary", 0.90),
    ("Fracture", "Secondary", 0.80),
    ("Venous Thromboembolism", "Secondary", 0.85),
    ("Hypoglycemia", "Secondary", 0.80),
    ("Hepatotoxicity", "Secondary", 0.75),
    ("Arrhythmia", "Secondary", 0.80),
    ("Infection", "Secondary", 0.85),
    ("Cancer Risk", "Secondary", 0.80),

    # ===== Level 3: Secondary - Methods =====
    ("Immeasurable time bias", "Secondary", 1.05),
    ("Marginal structural models", "Secondary", 1.15),
    ("Clone-censor weight", "Secondary", 1.10),
    ("Target trial emulation", "Secondary", 1.15),
    ("RWE", "Secondary", 1.00),
    ("Propensity score", "Secondary", 1.10),
    ("Inverse probability weighting", "Secondary", 1.05),
    ("Instrumental variable", "Secondary", 0.95),
    ("Difference-in-differences", "Secondary", 0.90),
    ("Regression discontinuity", "Secondary", 0.85),
    ("Cox regression", "Secondary", 0.95),
    ("Competing risks", "Secondary", 0.90),
    ("Time-varying confounding", "Secondary", 1.00),
    ("Immortal time bias", "Secondary", 1.00),
    ("Self-controlled designs", "Secondary", 0.90),
    ("New-user design", "Secondary", 0.95),
    ("Active comparator", "Secondary", 1.00),
    ("Negative control", "Secondary", 0.90),
    ("Sensitivity analysis", "Secondary", 0.85),
    ("Causal inference", "Secondary", 1.10),

    # ===== Level 3: Secondary - Data Sources =====
    ("Claims data", "Secondary", 0.95),
    ("Electronic health records", "Secondary", 1.00),
    ("National health insurance", "Secondary", 0.95),
    ("HIRA", "Secondary", 0.90),
    ("NHIS", "Secondary", 0.90),
    ("Registry data", "Secondary", 0.85),
    ("Cohort study", "Secondary", 0.95),
    ("Case-control study", "Secondary", 0.85),
    ("Nested case-control", "Secondary", 0.80),
    ("Multi-database study", "Secondary", 0.85),
]

# 레벨별 기본 가중치
level_base = {
    "Core": 300,
    "Primary": 150,
    "Secondary": 70,
}

# 최종 weight 계산
records = []
for term, level, importance in keywords:
    w = level_base[level] * importance
    records.append((term, level, importance, round(w, 1)))

df = pd.DataFrame(records, columns=["term", "level", "importance", "weight"])

# SKKU PEPV는 중앙에 별도 배치 → 워드클라우드 freq에서 제외
freq = {row["term"]: row["weight"]
        for _, row in df.iterrows() if row["term"] != "SKKU PEPV"}

# -----------------------------
# (B) 도넛형 마스크 (중앙 비우기 → SKKU PEPV 자리)
# -----------------------------
SIZE = 1600
MARGIN = 40
CENTER_R = 180  # 중앙 빈 공간 반지름 (SKKU PEPV 텍스트 자리)

def make_donut_mask(size, margin, center_r):
    img = Image.new("L", (size, size), 255)  # 흰색=배치 금지
    draw = ImageDraw.Draw(img)
    # 바깥 원: 배치 허용 (검정)
    draw.ellipse((margin, margin, size - margin, size - margin), fill=0)
    # 중앙 원: 배치 금지 (흰색) → SKKU PEPV 자리 확보
    cx, cy = size // 2, size // 2
    draw.ellipse((cx - center_r, cy - center_r, cx + center_r, cy + center_r), fill=255)
    return np.array(img)

mask = make_donut_mask(SIZE, MARGIN, CENTER_R)

# -----------------------------
# (C) 색상 팔레트 (파랑-초록-청록 계열)
# -----------------------------
color_list = [
    "#1B3A5C",  # 진한 남색
    "#1D4E89",  # 남색
    "#2471A3",  # 파랑
    "#2E86AB",  # 중간 파랑
    "#3498DB",  # 밝은 파랑
    "#1ABC9C",  # 청록
    "#27AE60",  # 초록
    "#5DAB8B",  # 연한 초록
    "#48C9B0",  # 민트
    "#76D7C4",  # 밝은 민트
]

def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    t = min(1.0, max(0.0, (font_size - 8) / 130))
    idx = int((1.0 - t) * (len(color_list) - 1))
    return color_list[idx]

# -----------------------------
# (D) 워드클라우드 생성 (SKKU PEPV 제외)
# -----------------------------
wc = WordCloud(
    width=SIZE,
    height=SIZE,
    background_color=None,
    mode="RGBA",
    mask=mask,
    prefer_horizontal=0.88,
    min_font_size=8,
    max_font_size=140,
    relative_scaling=0.45,
    collocations=False,
    random_state=42,
    color_func=custom_color_func,
    margin=3,
)

wc.generate_from_frequencies(freq)

# -----------------------------
# (E) SKKU PEPV를 중앙에 합성 (PIL)
# -----------------------------
wc_img = wc.to_image()  # RGBA

# SKKU PEPV 텍스트를 중앙에 그리기
draw = ImageDraw.Draw(wc_img)

# 폰트 크기를 자동 조정 (중앙 공간에 맞춤)
target_text = "SKKU PEPV"
font_size = 120
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
except OSError:
    font = ImageFont.load_default()

# 텍스트 크기 측정 후 중앙 배치
bbox = draw.textbbox((0, 0), target_text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (SIZE - tw) // 2
y = (SIZE - th) // 2 - 10  # 살짝 위로 보정
draw.text((x, y), target_text, fill="#1B3A5C", font=font)

# -----------------------------
# (F) 저장
# -----------------------------
out_dir = Path("wordcloud_output")
out_dir.mkdir(exist_ok=True)

# 투명 배경
transparent_path = out_dir / "wordcloud_transparent.png"
wc_img.save(str(transparent_path))

# 흰 배경 버전
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(wc_img, interpolation="bilinear")
ax.axis("off")
plt.tight_layout()

white_path = out_dir / "wordcloud_white.png"
fig.savefig(white_path, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()

# 가중치 표 저장
csv_path = out_dir / "wordcloud_weights.csv"
df.sort_values(["level", "weight"], ascending=[True, False]).to_csv(
    csv_path, index=False, encoding="utf-8-sig"
)

print(f"Total keywords: {len(keywords)}")
print("Saved:")
print(" -", transparent_path)
print(" -", white_path)
print(" -", csv_path)
