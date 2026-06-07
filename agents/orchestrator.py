from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from agents.chief_analyst import ChiefAnalystAgent
from agents.coach_agent import CoachAgent
from agents.debate_agent import DebateAgent
from agents.news_agent import NewsAgent
from agents.player_agent import PlayerAgent
from agents.scout_agent import ScoutAgent
from agents.stats_agent import StatsAgent
from agents.tactical_agent import TacticalAgent
from llm.mistral_analyst import MistralAnalyst
from models.predictor import MatchPredictor
from rag.vector_knowledge_retriever import VectorKnowledgeRetriever


class AgentOrchestrator:
    """World Cup Intelligence Center orchestration layer.

    Level 3 architecture:
        Stats + Scout + Tactical + Player + News
                  ↓
              Debate Agent
                  ↓
        Chief Analyst powered by Mistral
                  ↓
        World Cup Executive Briefing
    """

    def __init__(self, teams_df: pd.DataFrame, matches_df: pd.DataFrame | None = None, kb_path: str = "knowledge_base", players_path: str = "data/players.csv"):
        retriever = VectorKnowledgeRetriever(kb_path)
        predictor = MatchPredictor(teams_df)
        self.teams_df = teams_df
        self.matches_df = matches_df
        self.players_df = self._load_players(players_path)

        self.stats_agent = StatsAgent(predictor)
        self.scout_agent = ScoutAgent(retriever)
        self.tactical_agent = TacticalAgent(retriever)
        self.player_agent = PlayerAgent(self.players_df)
        self.news_agent = NewsAgent(retriever)
        self.debate_agent = DebateAgent()
        self.chief_agent = ChiefAnalystAgent()
        self.mistral_analyst = MistralAnalyst()
        self.coach_agent = CoachAgent(teams_df, matches_df if matches_df is not None else pd.DataFrame(), self.mistral_analyst)

    def run_match_analysis(self, home_team: str, away_team: str) -> dict[str, Any]:
        """Backward-compatible local analysis endpoint."""
        return self.run_intelligence_center(home_team, away_team, question="Create an executive match briefing.")

    def run_intelligence_center(self, home_team: str, away_team: str, question: str) -> dict[str, Any]:
        stats = self.stats_agent.analyze(home_team, away_team)
        scout = self.scout_agent.analyze(home_team, away_team)
        tactical = self.tactical_agent.analyze(home_team, away_team)
        player = self.player_agent.analyze(home_team, away_team)
        news = self.news_agent.analyze(home_team, away_team)
        debate = self.debate_agent.analyze(home_team, away_team, stats, scout, tactical, player, news)

        reports = {
            "stats": stats,
            "scout": scout,
            "tactical": tactical,
            "player": player,
            "news": news,
            "debate": debate,
        }
        local_briefing = self.chief_agent.synthesize(stats, scout, tactical, player, news, debate)
        context = self._build_chief_context(home_team, away_team, reports, local_briefing)
        ai_briefing = self.mistral_analyst.answer(question=question, context=context)

        return {
            **reports,
            "briefing": local_briefing,
            "local_chief_analyst_fallback": local_briefing,
            "ai_answer": ai_briefing,
            "mistral_answer": ai_briefing,
            "mistral_configured": self.mistral_analyst.is_configured,
            "llm_context": context,
            "agent_reports": reports,
        }

    def ask_ai_analyst(self, home_team: str, away_team: str, question: str) -> dict[str, Any]:
        return self.run_intelligence_center(home_team, away_team, question)

    def ask_gemini_analyst(self, home_team: str, away_team: str, question: str) -> dict[str, Any]:
        """Backward-compatible alias kept for older UI code."""
        return self.ask_ai_analyst(home_team, away_team, question)

    def ask_the_coach(self, question: str, focus_team: str = "Portugal", simulations: int = 12000) -> dict[str, Any]:
        """Strategic Ask-the-Coach endpoint for path, dark horse and what-if questions."""
        return self.coach_agent.answer(question=question, focus_team=focus_team, n=simulations)


    def _build_chief_context(self, home_team: str, away_team: str, reports: dict[str, Any], local_briefing: str) -> dict[str, Any]:
        prediction = reports["stats"]["prediction"]
        return {
            "match": {
                "home_team": home_team,
                "away_team": away_team,
            },
            "prediction": {
                "home_win_percent": prediction.home_win,
                "draw_percent": prediction.draw,
                "away_win_percent": prediction.away_win,
                "home_expected_goals": prediction.home_expected_goals,
                "away_expected_goals": prediction.away_expected_goals,
                "explanation_factors": getattr(prediction, "explanation_factors", {}),
            },
            "team_profiles": {
                home_team: self._team_profile(home_team),
                away_team: self._team_profile(away_team),
            },
            "specialist_agent_reports": self._json_safe_reports(reports),
            "local_chief_analyst_fallback": local_briefing,
            "data_notes": [
                "Phase 4 uses a realistic local cache for 48 teams, rankings, Elo, historical results and players.",
                "SofaScore is optional/cache-first and not required for the demo.",
                "Live injuries, confirmed lineups and breaking news are not guaranteed unless a compliant live source is connected.",
            ],
        }

    def _team_profile(self, team: str) -> dict[str, Any]:
        row = self.teams_df.loc[self.teams_df["team"] == team].iloc[0]
        keys = [
            "team",
            "group",
            "confederation",
            "fifa_rank",
            "fifa_points",
            "elo",
            "elo_rank",
            "recent_form",
            "form_string",
            "attack_strength",
            "defense_strength",
            "squad_strength",
            "top_player_rating",
            "squad_market_value_m",
            "players_tracked",
            "data_quality_score",
        ]
        return {key: self._scalar(row[key]) for key in keys if key in row.index}

    @staticmethod
    def _load_players(players_path: str) -> pd.DataFrame:
        path = Path(players_path)
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path)

    @classmethod
    def _json_safe_reports(cls, reports: dict[str, Any]) -> dict[str, Any]:
        safe = {}
        for name, report in reports.items():
            safe[name] = cls._json_safe(report)
        return safe

    @classmethod
    def _json_safe(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: cls._json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._json_safe(v) for v in value]
        if hasattr(value, "__dict__"):
            return cls._json_safe(value.__dict__)
        if hasattr(value, "item"):
            return value.item()
        return value

    @staticmethod
    def _scalar(value: Any) -> Any:
        return value.item() if hasattr(value, "item") else value
