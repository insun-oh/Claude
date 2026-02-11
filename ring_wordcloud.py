import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import math

# -----------------------------
# (A) 키워드 + 레벨 구조 + 가중치 설계
# -----------------------------
keywords = [
    # Level 1: Core (중앙)
    ("SKKU PEPV", "Core", 1.40),
    ("Pharmacoepidemiology", "Core", 1.30),
    ("Drug Safety", "Core", 1.20),
    ("Real-World Evidence", "Core", 1.10),

    # Level 2: Primary (중간 링)
    ("Cardiovascular Disease", "Primary", 1.15),
    ("Metabolic Disorders", "Primary", 1.10),
    ("Diabetes", "Primary", 1.10),
    ("Mental Health", "Primary", 1.05),
    ("Neuropsychiatry", "Primary", 1.00),
    ("Methodology", "Primary", 1.20),

    # Level 3: Secondary (바깥 링)
    ("SGLT2 inhibitors", "Secondary", 1.15),
    ("GLP-1 receptor agonists", "Secondary", 1.10),
    ("DPP-4 inhibitors", "Secondary", 0.95),
    ("DOACs", "Secondary", 0.90),
    ("ADHD medications", "Secondary", 0.85),
    ("COVID-19 vaccines", "Secondary", 0.95),
    ("MACE", "Secondary", 1.05),
    ("Bleeding", "Secondary", 0.85),
    ("Acute Kidney Injury", "Secondary", 0.90),
    ("Adverse Drug Reactions", "Secondary", 0.95),
    ("Immeasurable time bias", "Secondary", 1.00),
    ("Marginal structural models", "Secondary", 1.10),
    ("Clone-censor weight", "Secondary", 1.05),
    ("Target trial emulation", "Secondary", 1.10),
    ("RWE", "Secondary", 0.95),
]

level_base = {"Core": 240, "Primary": 140, "Secondary": 80}

records = []
for term, level, importance in keywords:
    w = level_base[level] * importance
    records.append((term, level, importance, round(w, 1)))

df = pd.DataFrame(records, columns=["term", "level", "importance", "weight"])

# -----------------------------
# (B) 레벨별 색상 팔레트
# -----------------------------
level_colors = {
    "Core":      "#1B3A5C",   # 진한 남색
    "Primary":   "#2E86AB",   # 중간 파랑
    "Secondary": "#5DAB8B",   # 초록 계열
}

# -----------------------------
# (C) 링 배치 설정
# -----------------------------
# 각 링의 반지름 (0~1 범위, 1이 캔버스 가장자리)
ring_config = {
    "Core":      {"radius": 0.0,  "font_base": 22, "font_scale": 0.06},
    "Primary":   {"radius": 0.48, "font_base": 13, "font_scale": 0.025},
    "Secondary": {"radius": 0.82, "font_base": 10, "font_scale": 0.015},
}

# -----------------------------
# (D) 원형 링 위에 키워드 배치
# -----------------------------
fig, ax = plt.subplots(1, 1, figsize=(14, 14))
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-1.05, 1.05)
ax.set_aspect("equal")
ax.axis("off")

# 배경 원 (장식용 링)
for r, lw, alpha in [(0.95, 1.5, 0.12), (0.55, 1.0, 0.10), (0.20, 0.8, 0.08)]:
    circle = plt.Circle((0, 0), r, fill=False, edgecolor="#2E86AB",
                         linewidth=lw, alpha=alpha, linestyle="--")
    ax.add_patch(circle)

# 레벨별로 키워드 배치
for level_name in ["Core", "Primary", "Secondary"]:
    cfg = ring_config[level_name]
    color = level_colors[level_name]
    level_df = df[df["level"] == level_name].reset_index(drop=True)
    n = len(level_df)

    if level_name == "Core":
        # Core: SKKU PEPV를 정중앙에 크게, 나머지를 그 아래 세로로 배치
        core_positions = [
            (0,  0.12),   # SKKU PEPV
            (0,  0.01),   # Pharmacoepidemiology
            (0, -0.07),   # Drug Safety
            (0, -0.15),   # Real-World Evidence
        ]
        core_font_mult = [1.0, 0.55, 0.50, 0.45]
        for i, row in level_df.iterrows():
            fontsize = cfg["font_base"] + row["weight"] * cfg["font_scale"]
            fs = fontsize * core_font_mult[i]
            px, py = core_positions[i]
            ax.text(px, py, row["term"],
                    fontsize=fs, fontweight="bold",
                    ha="center", va="center", color=color,
                    alpha=1.0 if i == 0 else 0.85,
                    fontfamily="sans-serif")
    else:
        # Primary / Secondary: 원형 링 위에 균등 배치
        radius = cfg["radius"]
        # 시작 각도를 90도(12시 방향)로 하고, 균등 분할
        angles = [math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

        for i, row in level_df.iterrows():
            angle = angles[i]
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            fontsize = cfg["font_base"] + row["weight"] * cfg["font_scale"]

            # 텍스트가 원 바깥쪽을 향하도록 회전 (가독성 위해 ±90도 제한)
            rot_deg = math.degrees(angle)
            # 아래쪽 반원(180~360도)에서는 텍스트를 뒤집어서 읽기 쉽게
            if 90 < rot_deg <= 270 or -270 <= rot_deg < -90:
                rot_deg += 180

            ax.text(x, y, row["term"],
                    fontsize=fontsize, fontweight="semibold",
                    ha="center", va="center", color=color,
                    rotation=0,  # 수평 배치 (가독성 우선)
                    alpha=0.88, fontfamily="sans-serif")

plt.tight_layout()

# -----------------------------
# (E) 저장
# -----------------------------
out_dir = Path("wordcloud_output")
out_dir.mkdir(exist_ok=True)

# 흰 배경
white_path = out_dir / "ring_wordcloud_white.png"
fig.savefig(white_path, dpi=300, bbox_inches="tight", facecolor="white")

# 투명 배경
transparent_path = out_dir / "ring_wordcloud_transparent.png"
fig.savefig(transparent_path, dpi=300, bbox_inches="tight", facecolor="none")
plt.close()

# 가중치 표 저장
csv_path = out_dir / "ring_wordcloud_weights.csv"
df.sort_values(["level", "weight"], ascending=[True, False]).to_csv(
    csv_path, index=False, encoding="utf-8-sig"
)

print("Saved:")
print(" -", white_path)
print(" -", transparent_path)
print(" -", csv_path)
