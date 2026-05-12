"""Agent factories for the life-sandbox pipeline.

Two-phase pipeline:
  Phase 1 (POST /candidates):
    - coordinator    : profile → 5 candidate path archetypes
  Phase 2 (POST /analyze/stream): the user-selected 1-3 paths flow through
    - career_eval    : profile + paths → CareerOutput     (parallel)
    - finance_eval   : profile + paths → FinanceOutput    (parallel)
    - risk_eval      : profile + paths → RiskOutput       (parallel)
    - lifestyle_eval : profile + paths → LifestyleOutput  (parallel — WLB, pressure, burnout)
    - decision       : profile + paths + all evals → ranked paths
    - critic         : challenges the decision's ranking → CritiqueOutput

Side-channel agents:
  - path_expander  : profile + free-form description → PathCandidate
                     (used when the user types a custom career path)
  - ingest         : raw profile extracts → IngestSummary (field, stage, notes_seed)
  - career_advice  : profile + chosen RankedPath → CareerAdvice (post-pick advice)

NOTE: All agents use free-text responses (no response_schema). The caller
must parse the returned JSON text into the appropriate Pydantic model.
"""

from __future__ import annotations

import os

from autogen.beta import Agent
from autogen.beta.config import GeminiConfig, OpenAIConfig
from autogen.beta.config.config import ModelConfig

_PROVIDER_DEFAULTS = {
    "gemini": {"model": "gemini-2.5-flash", "env": "GEMINI_API_KEY"},
    "openai": {"model": "gpt-4o-mini", "env": "OPENAI_API_KEY"},
}


def build_config(max_tokens: int | None = None) -> ModelConfig:
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise SystemExit(f"LLM_PROVIDER must be one of {list(_PROVIDER_DEFAULTS)}")

    model = os.environ.get("MODEL", _PROVIDER_DEFAULTS[provider]["model"])
    env = _PROVIDER_DEFAULTS[provider]["env"]
    if not os.environ.get(env):
        raise SystemExit(
            f"{env} is required for LLM_PROVIDER={provider}. "
            f"Copy .env.example to .env and add your key."
        )

    if provider == "openai":
        base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        config = OpenAIConfig(
            model=model,
            streaming=True,
            base_url=base_url,
            max_tokens=max_tokens,
        )
        return config
    return GeminiConfig(model=model, streaming=False)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

COORDINATOR_PROMPT = (
    "You are the lead career strategist. Given a user's profile, propose EXACTLY 5 "
    "DISTINCT, REALISTIC career path archetypes that span a meaningful range of "
    "trade-offs. Aim for at least one of each: stable corporate IC, high-growth "
    "startup / founder, specialist (quant, researcher, consultant), creative / "
    "freelance, and a wildcard the user might not have considered themselves. "
    "Avoid duplicates. Each path should be specific enough to evaluate financially "
    "and stylistically — name the role and typical employer type. Optimize for "
    "diversity of trade-off profile, not generic 'safe' choices. The user will "
    "pick 1-3 of these to evaluate in depth.\n\n"
    "Return a valid JSON object with a single key \"paths\" containing an array of 5 objects, "
    "each with keys: id (snake_case slug), title (human-readable), archetype (one of: "
    "corporate_ic, founder, quant, consultant, researcher, freelance, other), "
    "summary (2-3 sentence pitch). Return ONLY the JSON, no markdown, no explanation."
)


PATH_EXPANDER_PROMPT = (
    "You normalize a user's free-form career idea into a structured PathCandidate "
    "for the rest of the pipeline. Given the user's profile and a short description "
    "of a career they have in mind.\n\n"
    "Return a JSON object with keys: id (snake_case slug), title (short human-readable title), "
    "archetype (one of: corporate_ic, founder, quant, consultant, researcher, freelance, other), "
    "summary (2-3 sentence pitch describing what this path looks like for THIS user over the "
    "next 5 years). If the description is vague, make conservative best guesses anchored "
    "in the user's field, location, and stage. Be specific enough that downstream evaluators "
    "can produce meaningful numbers.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


CAREER_PROMPT = (
    "You are a quantitative career-trajectory analyst. For each candidate path, return "
    "a JSON object with a single key \"evals\" containing an array of evaluation objects, "
    "each with:\n"
    "  - path_id: string (the path's id)\n"
    "  - milestones: array of 3-5 strings (year-by-year milestones, year 1 first)\n"
    "  - growth_rate: float 0..1 (annual rate of skill/title progression)\n"
    "  - plateau_prob: float 0..1 (probability the user stalls within 5 years)\n\n"
    "Be honest about plateau risk. A senior IC track plateaus more than a high-growth "
    "startup; a quant trading seat has narrow advancement; consulting has up-or-out. "
    "Reflect the user's stage and field — a high-schooler has more setup years.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


FINANCE_PROMPT = (
    "You are a quantitative compensation modeler. For each candidate path, return "
    "a JSON object with a single key \"evals\" containing an array of evaluation objects, "
    "each with:\n"
    "  - path_id: string\n"
    "  - salary_curve_5y: array of 5 floats (expected total comp by year 1..5, USD)\n"
    "  - stddev_curve_5y: array of 5 floats (stddev of total comp by year 1..5, USD)\n"
    "  - ev_5y: float (expected cumulative comp over 5 years, USD)\n"
    "  - tail_upside: float (P95 cumulative 5y comp, USD)\n\n"
    "Use realistic 2026 market levels. Big-tech ICs ≈ $150k–$400k by Y5. Founders have "
    "wide stddev and large tail upside but low mean. Quant traders have high mean + medium "
    "tail. Consultants have low stddev. Reflect location: NYC > remote > LCOL.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


RISK_PROMPT = (
    "You are a quantitative career-risk analyst. For each candidate path, return "
    "a JSON object with a single key \"evals\" containing an array of evaluation objects, "
    "each with:\n"
    "  - path_id: string\n"
    "  - layoff_hazard_yr: float 0..1 (annual probability of involuntary exit)\n"
    "  - ruin_prob_5y: float 0..1 (probability of bad outcome within 5 years)\n"
    "  - downside_pctile_5y: float (P5 cumulative 5y total comp, USD)\n\n"
    "Founders have high ruin (>=0.5), big-tech ICs low (<=0.05). Layoff hazard rose in "
    "2023-2025 even at big tech (~0.10/yr). Be specific — this is the agent the user "
    "trusts to surface bad scenarios.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


LIFESTYLE_PROMPT = (
    "You are a quantitative lifestyle / work-life-balance analyst. For each candidate path, return "
    "a JSON object with a single key \"evals\" containing an array of evaluation objects, "
    "each with:\n"
    "  - path_id: string\n"
    "  - work_hours_per_week: float (sustained typical hours, not crunch peaks)\n"
    "  - pressure_level: float 0..1 (day-to-day stress / intensity)\n"
    "  - wlb_score: float 0..1 (overall work-life balance)\n"
    "  - burnout_prob_5y: float 0..1 (probability of significant burnout within 5y)\n\n"
    "Big-tech IC ~45-55 hours, pressure ~0.45, wlb ~0.75, burnout ~0.15. "
    "Investment banking 70-90 hours, pressure ~0.80, wlb ~0.20, burnout ~0.50. "
    "Early founder 60-80 hours, pressure ~0.85, wlb ~0.25, burnout ~0.40. "
    "Be honest. Don't soften brutal paths.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


CAREER_ADVICE_PROMPT = (
    "You are a concrete career-coaching agent. You receive the user's profile and ONE "
    "career path they have committed to. Return a JSON object with keys:\n"
    "  - path_id: string (use the input path_id verbatim)\n"
    "  - headline: string (one sentence framing what to focus on FIRST)\n"
    "  - courses: array of 3-6 strings (named courses, MOOCs, books, or certifications)\n"
    "  - programs: array of 3-6 strings (internships, fellowships, summer programs)\n"
    "  - personal_projects: array of 3-6 strings (specific buildable portfolio projects, "
    "    each concrete enough the user could start tomorrow)\n\n"
    "Anchor advice to the user's stage, field, and location.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


CRITIQUE_PROMPT = (
    "You are an adversarial decision critic in a multi-agent career-advisory system. "
    "Your job is to find PRINCIPLED weaknesses in the decision agent's ranking — "
    "not contrarianism, but actual issues a thoughtful skeptic would raise.\n\n"
    "You receive: the user's profile, candidate paths, evaluator outputs, and the "
    "decision agent's ranking.\n\n"
    "Look for over-optimistic assumptions, underweighted risks, mismatch with user "
    "preferences, and common biases.\n\n"
    "Return a JSON object with:\n"
    "  - overall_challenge: string (2-3 sentences framing the strongest dissent)\n"
    "  - most_overrated_path_id: string or null (path id ranked too high, or null)"
    "  - most_underrated_path_id: string or null\n"
    "  - per_path: array of objects, each with:\n"
    "      - path_id: string\n"
    "      - challenge: string (2-3 sentences arguing why this rank might be wrong, "
    "        or 'No major issues' if it's sound)\n"
    "      - optimism_flags: array of 1-4 strings (specific evaluator assumptions "
    "        that should be questioned)\n\n"
    "BE PRINCIPLED. If the decision is solid, say so. Don't manufacture critiques.\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


DECISION_PROMPT = (
    "You are the decision agent. You receive: the user's profile, candidate paths, "
    "and career/finance/risk/lifestyle evaluations for each.\n\n"
    "Compute a utility score per path. The formula should consider: ambition * growth_rate, "
    "(1 - risk_tol) * ev_5y, -(1 - risk_tol) * ruin_prob_5y, risk_tol * tail_upside, "
    "wlb_score, and burnout_prob_5y. Normalize where appropriate.\n\n"
    "Return a JSON object with a single key \"top3\" containing an array of 3 ranked path "
    "objects, each with:\n"
    "  - path_id: string\n"
    "  - title: string\n"
    "  - archetype: string\n"
    "  - summary: string\n"
    "  - utility_score: float (higher is better)\n"
    "  - why: string (2-3 sentences on why this path scores well for THIS user)\n"
    "  - tradeoffs: string (2-3 sentences on what the user gives up)\n"
    "  - salary_curve_5y: array of 5 floats\n"
    "  - stddev_curve_5y: array of 5 floats\n"
    "  - ev_5y: float\n"
    "  - ruin_prob_5y: float\n"
    "  - growth_rate: float\n"
    "  - work_hours_per_week: float\n"
    "  - pressure_level: float 0..1\n"
    "  - wlb_score: float 0..1\n"
    "  - burnout_prob_5y: float 0..1\n\n"
    "Sorted by utility, highest first. Return ONLY the JSON, no markdown, no explanation."
)


INGEST_PROMPT = (
    "You are a profile-summarization agent. Given raw extracts from a user's "
    "online profiles (GitHub, LinkedIn, personal site, or pasted text).\n\n"
    "Return a JSON object with:\n"
    "  - field: string (the user's current field of study or work)\n"
    "  - stage: one of 'high_school', 'undergrad', 'new_grad'\n"
    "  - notes_seed: string (2-4 concrete sentences capturing goals, projects, roles, and interests)\n\n"
    "Return ONLY the JSON, no markdown, no explanation."
)


ACTION_PLANNER_PROMPT = (
    "你是一名职业规划教练。根据以下职业路径，为一位计算机专业、中等风险偏好的用户，"
    "列出下一步具体的 4 条行动计划，包括课程学习、项目实践、社交活动三个方面，用中文分条返回。\n\n"
    "路径信息：{final_paths}\n\n"
    "Return a JSON object with a single key \"items\" containing an array of exactly 4 strings, "
    "each a concrete action item in Chinese. Return ONLY the JSON, no markdown, no explanation."
)


# ---------------------------------------------------------------------------
# Factories — all agents use free-text responses (no response_schema)
# ---------------------------------------------------------------------------


def build_coordinator() -> Agent:
    return Agent(
        name="coordinator",
        prompt=COORDINATOR_PROMPT,
        config=build_config(),
    )


def build_path_expander() -> Agent:
    return Agent(
        name="path_expander",
        prompt=PATH_EXPANDER_PROMPT,
        config=build_config(),
    )


def build_career_evaluator() -> Agent:
    return Agent(
        name="career_eval",
        prompt=CAREER_PROMPT,
        config=build_config(),
    )


def build_finance_evaluator() -> Agent:
    return Agent(
        name="finance_eval",
        prompt=FINANCE_PROMPT,
        config=build_config(),
    )


def build_risk_evaluator() -> Agent:
    return Agent(
        name="risk_eval",
        prompt=RISK_PROMPT,
        config=build_config(),
    )


def build_lifestyle_evaluator() -> Agent:
    return Agent(
        name="lifestyle_eval",
        prompt=LIFESTYLE_PROMPT,
        config=build_config(),
    )


def build_decision_agent() -> Agent:
    return Agent(
        name="decision",
        prompt=DECISION_PROMPT,
        config=build_config(max_tokens=2048),
    )


def build_critic() -> Agent:
    return Agent(
        name="critic",
        prompt=CRITIQUE_PROMPT,
        config=build_config(),
    )


def build_ingest_agent() -> Agent:
    return Agent(
        name="ingest",
        prompt=INGEST_PROMPT,
        config=build_config(),
    )


def build_career_advice_agent() -> Agent:
    return Agent(
        name="career_advice",
        prompt=CAREER_ADVICE_PROMPT,
        config=build_config(),
    )


def build_action_planner() -> Agent:
    return Agent(
        name="action_planner",
        prompt=ACTION_PLANNER_PROMPT,
        config=build_config(),
    )
