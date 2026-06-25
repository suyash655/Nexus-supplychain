"""
Generate chart diagrams for the research paper
Creates three charts and saves them as high-quality PNG images
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import rcParams

# Configure matplotlib for academic paper quality
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['lines.linewidth'] = 1.5
rcParams['axes.linewidth'] = 1.2

# ===================================================================
# FIGURE 1: SME Satisfaction Score Distribution (Histogram)
# ===================================================================

fig1, ax1 = plt.subplots(figsize=(8, 5))

stars = [1, 2, 3, 4, 5]
counts = [28, 10, 12, 15, 35]
colors = ['#d62728', '#ff7f0e', '#ffdd57', '#90ee90', '#2ca02c']

bars = ax1.bar(stars, counts, color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

ax1.set_xlabel('Satisfaction Rating (Stars)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Respondents', fontsize=12, fontweight='bold')
ax1.set_title('Distribution of Overall SME Satisfaction Scores', fontsize=13, fontweight='bold', pad=15)
ax1.set_xticks(stars)
ax1.set_ylim(0, 40)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Add value labels on bars
for bar, count in zip(bars, counts):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{count}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('d:\\supex1\\figure1_satisfaction_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 1 created: Satisfaction Score Distribution")

# ===================================================================
# FIGURE 2: AI-Alert vs Traditional Systems (Bar Chart)
# ===================================================================

fig2, ax2 = plt.subplots(figsize=(8, 5))

systems = ['AI-Alert Systems\n(n=47)', 'Traditional Data\n(n=53)']
scores = [4.7, 1.9]
colors2 = ['#1f77b4', '#ff7f0e']
std_errors = [0.52, 0.88]

bars2 = ax2.bar(systems, scores, color=colors2, edgecolor='black', linewidth=1.2, 
               alpha=0.8, yerr=std_errors, capsize=10, error_kw={'linewidth': 1.5})

ax2.set_ylabel('Mean Resilience Confidence Score', fontsize=12, fontweight='bold')
ax2.set_title('Resilience Confidence: AI-Alert vs. Traditional Systems', 
             fontsize=13, fontweight='bold', pad=15)
ax2.set_ylim(0, 6)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add value labels
ax2.text(0, 4.7 + 0.3, '4.7', ha='center', fontsize=11, fontweight='bold')
ax2.text(1, 1.9 + 0.3, '1.9', ha='center', fontsize=11, fontweight='bold')

# Add note about statistical significance
ax2.text(0.5, 0.3, 'p < 0.001 ***  |  Cohen\'s d = 3.2', 
        ha='center', fontsize=10, style='italic',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('d:\\supex1\\figure2_alert_vs_traditional.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 2 created: AI-Alert vs. Traditional Systems")

# ===================================================================
# FIGURE 3: Mitigation Cost vs Satisfaction (Line Chart with Markers)
# ===================================================================

fig3, ax3 = plt.subplots(figsize=(9, 5))

cost_categories = ['Low\n($0-5K)', 'Moderate\n($5-25K)', 'Neutral/Avg\n($25-75K)', 
                   'High\n($75-250K)', 'Critical\n($250K+)']
satisfaction_scores = [4.9, 4.3, 3.2, 2.1, 1.2]
sample_sizes = [8, 19, 31, 28, 14]

# Create color gradient from green to red
colors3 = ['#2ca02c', '#90ee90', '#ffdd57', '#ff7f0e', '#d62728']

ax3.plot(range(len(cost_categories)), satisfaction_scores, 'o-', linewidth=2.5, 
        markersize=10, color='#1f77b4', markerfacecolor='#1f77b4', 
        markeredgecolor='black', markeredgewidth=1.2)

# Color code the markers by satisfaction level
for i, (score, color) in enumerate(zip(satisfaction_scores, colors3)):
    ax3.plot(i, score, 'o', markersize=10, color=color, 
            markeredgecolor='black', markeredgewidth=1.2, zorder=5)

ax3.set_xlabel('Mitigation Cost Category (Average Annual Spending)', 
              fontsize=12, fontweight='bold')
ax3.set_ylabel('Mean SME Satisfaction Score', fontsize=12, fontweight='bold')
ax3.set_title('Inverse Relationship: Mitigation Cost and Satisfaction\n(r = −0.72)',
             fontsize=13, fontweight='bold', pad=15)
ax3.set_xticks(range(len(cost_categories)))
ax3.set_xticklabels(cost_categories, fontsize=10)
ax3.set_ylim(0, 5.5)
ax3.grid(axis='y', alpha=0.3, linestyle='--')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Add value labels and sample sizes
for i, (score, n) in enumerate(zip(satisfaction_scores, sample_sizes)):
    ax3.text(i, score + 0.2, f'{score}', ha='center', fontsize=10, fontweight='bold')
    ax3.text(i, score - 0.35, f'(n={n})', ha='center', fontsize=9, style='italic', color='gray')

plt.tight_layout()
plt.savefig('d:\\supex1\\figure3_cost_satisfaction.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 3 created: Mitigation Cost vs. Satisfaction")

print("\n✓ All three charts generated successfully:")
print("  - figure1_satisfaction_distribution.png")
print("  - figure2_alert_vs_traditional.png")
print("  - figure3_cost_satisfaction.png")
