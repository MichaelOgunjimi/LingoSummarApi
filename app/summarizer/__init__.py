"""
LingoSummar NLP summarization engine.

Pipeline: Preprocessing → Feature Extraction → Clustering → Fuzzy Logic Ranking → Summary
"""

from app.summarizer.engine import TextSummarizer

__all__ = ["TextSummarizer"]
