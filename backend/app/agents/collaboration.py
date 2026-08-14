class CollaborativeReview:
    """Optional CrewAI collaboration boundary.

    LangGraph remains authoritative. When CrewAI is installed/configured, this adapter can run
    Debugger + Security Reviewer + Test Engineer as a bounded subtask and return one typed result.
    The base install intentionally does not require CrewAI to keep local startup deterministic.
    """
    async def run(self, context: dict) -> dict:
        try:
            import crewai  # type: ignore # noqa:F401
        except ImportError:
            return {"enabled":False,"reason":"CrewAI optional dependency is not installed"}
        return {"enabled":True,"reason":"Adapter ready; configure real agents/provider before use"}
