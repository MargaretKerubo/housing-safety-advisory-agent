# Housing Safety Advisory Agent


## 1. Problem Statement

Accessing safe and suitable housing requires balancing multiple constraints such as budget, commute patterns, time of travel, and situational risk factors. Many people especially those relocating or working non-standard hour lack tools that help them reason transparently about safety-related trade-offs without relying on stigmatizing labels, crime rankings, or opaque recommendations.

This project addresses the absence of ethical, explainable, and context-aware decision-support systems that help people make informed housing choices while respecting uncertainty and user autonomy. Outputs are **advisory guidance, not a definitive assessment**.

---

## 2. SDG Alignment

*Promoting transparency, awareness, and individual agency.*

This project primarily aligns with **UN Sustainable Development Goal 11: Sustainable Cities and Communities**, particularly:

* **11.1**: Access to adequate, safe, and affordable housing
* **11.3**: Inclusive and sustainable urbanization
* **11.7**: Safe, inclusive, and accessible public spaces

The agent contributes by supporting informed housing decisions without exclusion or stigma, avoiding harmful labeling of communities, and preserving individual agency.

---

## 3. Architecture and Design Choices

The system is built as a **decision-support architecture** with a deterministic, rule-based core and a strictly separated AI explanation layer.

Design choices include:

* Rule-first evaluation of situational risk factors
* Deterministic logic for repeatable outcomes
* Explicit trade-off analysis across safety, cost, and convenience
* Ethical guardrails to prevent biased or unsafe usage
* Lightweight, explainable data assumptions

High-level flow:

1. Collect and validate user inputs
2. Normalize constraints and preferences
3. Apply rule-based situational risk evaluation
4. Analyze trade-offs and compute comparative scores
5. Generate human-readable explanations
6. Return ranked options (Low / Medium / Higher risk)

---

## 4. AI Usage

AI is used solely as an **explanation and communication layer**.

AI is responsible for:

* Explaining how inputs and rules led to an outcome
* Describing safety-related trade-offs in accessible language
* Answering “why” and “why not” questions
* Communicating uncertainty and system limits

AI is **not** used to:

* Predict crime or risk probabilities
* Rank or label neighborhoods
* Override rule-based evaluations

This separation preserves transparency, accountability, and ethical control.

---

## 5. Trade-offs and Limitations

### Trade-offs

* Transparency and explainability are prioritized over predictive accuracy
* Rule-based logic limits adaptability but ensures accountability
* The system informs decisions without prescribing outcomes

### Limitations

* No real-time or historical crime data is used
* Results depend on the accuracy of user-provided information
* Regional context may be generalized
* Risk levels are comparative, not absolute measures of safety

Users should treat all outputs as **advisory guidance, not definitive assessments**.

---

## Authors

* **Flovian Atieno**
* **Mitchelle Kangethe**
* **Anthony Oduor**
* **Stephen Oginga**
* **Margaret Kerubo**

---
