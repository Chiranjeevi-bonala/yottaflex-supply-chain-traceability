# Operational Performance Metrics (M-01 to M-08): Mathematical Definitions

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`

---

## 1. Overview of Evaluation Metrics

The YottaFlex system evaluates the health, traceability, regulatory compliance, and audit integrity of the supply chain through 8 standardized mathematical metrics. All metrics are computed dynamically from live database records. Division-by-zero conditions are handled safely using default neutral values.

---

## 2. Metric Specifications

### M-01: Genealogy Completeness
- **Concept:** Measures the proportion of manufactured finished product batches possessing an unbroken, valid backward relational link to at least one raw material receipt lot.
- **Mathematical Formula:**
  \[
  M_{01} = \begin{cases}
  \frac{|\{f \in \mathcal{F} \mid \exists (f, r) \in \text{LotGenealogy} \land r \in \mathcal{R}\}|}{|\mathcal{F}|}, & |\mathcal{F}| > 0 \\
  1.0, & |\mathcal{F}| = 0
  \end{cases}
  \]
- **Target Threshold:** \( \ge 99.5\% \) (100% in pristine operations; drops when EC-01 anomalies exist).
- **Unit:** Percentage.

---

### M-02: Recall Scope Accuracy
- **Concept:** Measures the accuracy with which active recall cases identify and capture genuine affected customer deliveries compared to full downstream graph traversal.
- **Mathematical Formula:**
  \[
  M_{02} = \begin{cases}
  \frac{\sum_{r \in \text{Recalls}} |\mathcal{D}_{\text{recorded}}(r) \cap \mathcal{D}_{\text{graph}}(r)|}{\sum_{r \in \text{Recalls}} |\mathcal{D}_{\text{graph}}(r)|}, & \sum |\mathcal{D}_{\text{graph}}| > 0 \\
  1.0, & \text{otherwise}
  \end{cases}
  \]
- **Target Threshold:** \( 100.0\% \).
- **Unit:** Percentage.

---

### M-03: Customer Notification Coverage
- **Concept:** Evaluates the proportion of distinct commercial recipient customers within recall scope who have been formally issued statutory safety notices.
- **Mathematical Formula:**
  \[
  M_{03} = \begin{cases}
  \frac{|\{c \in \mathcal{C}_{\text{scope}} \mid \exists a \in \text{RecallActions} \text{ where } a.\text{type} = \text{'NOTIFY'} \land a.\text{target} = c\}|}{|\mathcal{C}_{\text{scope}}|}, & |\mathcal{C}_{\text{scope}}| > 0 \\
  1.0, & |\mathcal{C}_{\text{scope}}| = 0
  \end{cases}
  \]
- **Target Threshold:** \( 100.0\% \) (regulatory violation if \( < 100\% \); drops when EC-03 missed customers occur).
- **Unit:** Percentage.

---

### M-04: Quantity Reconciliation Rate
- **Concept:** Evaluates inventory mass balance across distributed finished batches, verifying that delivered volume does not exceed manufactured batch weight.
- **Mathematical Formula:**
  \[
  M_{04} = \begin{cases}
  \frac{|\{f \in \mathcal{F}_{\text{distributed}} \mid \sum_{d \in \mathcal{D}(f)} d.\text{qty} \le f.\text{quantity\_produced}\}|}{|\mathcal{F}_{\text{distributed}}|}, & |\mathcal{F}_{\text{distributed}}| > 0 \\
  1.0, & \text{otherwise}
  \end{cases}
  \]
- **Target Threshold:** \( 100.0\% \) (drops when EC-02 delivery overrun occurs).
- **Unit:** Percentage.

---

### M-05: Inventory Quarantine Compliance
- **Concept:** Measures whether finished goods batches implicated in active safety recalls have been locked with `status = 'QUARANTINED'` in warehouse management systems.
- **Mathematical Formula:**
  \[
  M_{05} = \begin{cases}
  \frac{|\{f \in \mathcal{F}_{\text{recalled}} \mid f.\text{status} = \text{'QUARANTINED'}\}|}{|\mathcal{F}_{\text{recalled}}|}, & |\mathcal{F}_{\text{recalled}}| > 0 \\
  1.0, & \text{otherwise}
  \end{cases}
  \]
- **Target Threshold:** \( 100.0\% \) (drops when EC-04 unquarantined stock occurs).
- **Unit:** Percentage.

---

### M-06: Recovery Rate
- **Concept:** Evaluates the cumulative physical volume of contaminated product retrieved or destroyed compared to total affected volume across safety recall cases.
- **Mathematical Formula:**
  \[
  M_{06} = \begin{cases}
  \frac{\sum_{r \in \text{Recalls}} r.\text{total\_qty\_recovered}}{\sum_{r \in \text{Recalls}} r.\text{total\_qty\_affected}}, & \sum r.\text{total\_qty\_affected} > 0 \\
  0.0, & \text{otherwise}
  \end{cases}
  \]
- **Target Threshold:** \( \ge 80.0\% \) (standard benchmark for mature recovery campaigns).
- **Unit:** Percentage.

---

### M-07: Outstanding Recall Quantity
- **Concept:** Quantifies the net volume of contaminated or suspect material remaining unaccounted for in logistics pipelines or customer facilities.
- **Mathematical Formula:**
  \[
  M_{07} = \max\left(0.0, \sum_{r \in \text{Recalls}} r.\text{total\_qty\_affected} - \sum_{r \in \text{Recalls}} r.\text{total\_qty\_recovered}\right)
  \]
- **Target Threshold:** Approaches \( 0 \text{ kg} \) as recall actions reach completion.
- **Unit:** Kilograms (KG).

---

### M-08: Exception Detection Rate
- **Concept:** Measures the sensitivity and success rate of automated audit algorithms identifying ground-truth operational anomalies across live database tables.
- **Mathematical Formula:**
  \[
  M_{08} = \begin{cases}
  \frac{|\text{Anomalies Identified by ExceptionDetector}|}{|\text{Ground-Truth Reference Anomalies}|}, & |\text{Ground-Truth}| > 0 \\
  1.0, & \text{otherwise}
  \end{cases}
  \]
- **Target Threshold:** \( 100.0\% \) (all 4 mandatory edge cases correctly flagged).
- **Unit:** Percentage.
