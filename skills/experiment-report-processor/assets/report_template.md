# 实验报告

## 摘要

本实验共处理 {{ sample_count }} 个样本。

## 数据质量

- **总样本数**: {{ data_quality.total_rows }}
- **有效样本数**: {{ data_quality.valid_rows }}
- **数据完整度**: {{ "%.2f"|format(data_quality.completion_rate) }}%

## 数据列信息

{% for col in columns %}
- {{ col }}
{% endfor %}

## 统计结果

{% if statistics %}
{% for col, stats in statistics.items() %}
### {{ col }}

- 平均值: {{ "%.2f"|format(stats.mean) }}
- 标准差: {{ "%.2f"|format(stats.std) }}
- 最小值: {{ "%.2f"|format(stats.min) }}
- 最大值: {{ "%.2f"|format(stats.max) }}
- 中位数: {{ "%.2f"|format(stats.median) }}

{% endfor %}
{% else %}
无数值数据可供统计分析。
{% endif %}

## 结论

[在此添加实验结论]

## 建议

[在此添加后续建议]

---

*本报告由实验报告处理器自动生成*
