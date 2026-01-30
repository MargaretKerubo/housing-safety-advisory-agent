# Internal Build Guide – Housing Safety Advisory Agent

> Purpose of this document
> This document defines what we are building, how the agent should reason, and how the codebase should be structured.

---

## 1. Agent Goal

Build an explainable AI-powered **decision-support agent** that helps users evaluate accommodation options by reasoning over **safety-related trade-offs** such as commute patterns, time of travel, budget constraints, and situational risk factors.

The agent supports **informed decision-making** without labeling neighborhoods or making authoritative or predictive claims. The system is aligned with **SDG 11: Sustainable Cities and Communities**.

---

## 2. What This Agent Is / Is Not

### The agent IS:

* Advisory, not authoritative
* Decision-support, not decision-making
* Rule-driven with AI-assisted explanation
* Focused on trade-offs, not predictions
* Context-aware (user preferences + situational factors)

### The agent IS NOT:

* A crime prediction system
* A neighborhood or area ranking engine
* A system that labels places as “safe” or “unsafe”
* A chatbot that gives generic housing advice
* A system that uses real crime, surveillance, or demographic data

---

## 3. Core Design Principles

These principles guide all implementation decisions.

1. **Explainability first** – every output must be traceable to explicit rules and user inputs
2. **Ethical neutrality** – avoid stigmatizing language, assumptions, or labels
3. **AI as a component** – rules decide, AI explains
4. **Minimal but structured data** – no heavy datasets or opaque models
5. **Deterministic core logic** – same inputs must always lead to the same evaluation

---

## 4. High-Level System Flow

1. Collect user inputs
2. Validate inputs and apply guardrails
3. Build or update the user session profile
4. Evaluate situational risk using deterministic rules
5. Analyze trade-offs and compute comparable scores
6. Generate explanations using AI
7. Return structured recommendations

---

## 5. Key Components to Implement

### 5.1 Input Layer

Responsible for:

* Collecting structured user inputs
* Normalizing values (e.g. budget bands, distance ranges)

Expected user inputs:

* City / town
* Budget range (estimate)
* Preferred location or area
* Commute destination
* Commute distance or time
* Typical return time (day / night)
* **How cautious do you prefer your housing options to be?** (low / medium / high)
* Living arrangement (alone / shared)

---

### 5.2 Guardrails & Validation Layer

Responsible for:

* Rejecting incomplete or invalid inputs
* Refusing unsafe, biased, or stigmatizing queries
* Reframing problematic requests into ethical alternatives

Examples:

* Refuse: “Which areas are dangerous?”
* Reframe to: “I can help you compare housing options based on situational risk trade-offs.”

---

### 5.3 User Profile & Session State

Responsible for:

* Persisting user preferences during a session
* Supporting multi-step interactions

Session state includes:

* Budget constraints
* Commute preferences
* Caution level (safety preference)

---

### 5.4 Rule-Based Risk Evaluation Engine

Responsible for:

* Applying predefined, transparent rules
* Producing numeric or categorical risk indicators

Rules may consider:

* Time of travel (day vs night)
* Commute length
* Transport availability
* Living alone vs shared accommodation

Example rule:
```bash
* If `return_time = night` AND `commute_distance > threshold` → increase situational risk

> This component must **not** use AI.
```
---

### 5.5 Scoring & Trade-Off Analyzer

Responsible for:

* Aggregating rule outputs
* Balancing safety, cost, and convenience
* Identifying explicit trade-offs

Outputs include:

* Risk category (Low / Medium / Higher)
* Key trade-offs influencing the evaluation

---

### 5.6 AI Reasoning & Explanation Layer

Responsible for:

* Translating scores into clear, natural language
* Explaining *why* certain options rank higher or lower
* Communicating uncertainty and limitations

AI does **not**:

* Decide risk levels
* Override rule-based outputs

AI **does**:

* Explain decisions
* Summarize trade-offs
* Answer “why” and “why not” questions

---

### 5.7 Output Formatter

Responsible for:

* Producing final user-facing responses
* Supporting both human-readable explanations and structured outputs

---

## 6. Data Strategy

* No real crime datasets
* No real-time feeds
* No surveillance or demographic data
* Use small, static, explainable reference values

All assumptions must be documented in code comments.

---

## 7. Ethical Constraints (Hard Rules)

The system must:

* Never label locations as safe or unsafe
* Never rank neighborhoods by crime
* Avoid demographic or socioeconomic assumptions
* Include advisory disclaimers in all outputs

---

## 8. What Success Looks Like (Internal)

* Clean separation of components
* Deterministic and testable core logic
* Clear explanations for every recommendation
* A simple, easy-to-follow demo flow
* Code that directly reflects this document

---

## 9. What Comes Next

1. Define input and output schemas
2. Implement the rule-based risk engine
3. Integrate the AI explanation layer
4. Build a simple CLI or UI
5. Write a public-facing README

---

## Authors

* Flovian Atieno
* Mitchelle Kangethe
* Anthony Oduor
* Stephen Oginga
* Margaret Kerubo

---

### Quote Reminder: If a feature does not support decision-making or explainability, it does not belong in this agent.
