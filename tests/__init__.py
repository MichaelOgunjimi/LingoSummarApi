import pytest
from app.summarizer.engine import TextSummarizer


def test_health_check():
    """Placeholder — will test the /api/v1/ endpoint."""
    assert True


def test_summarizer_basic():
    """Verify the summarizer engine runs end-to-end."""
    text = """Climate Change and Its Effects
    Climate change is one of the most pressing issues facing our planet today.
    Rising global temperatures have led to melting ice caps and rising sea levels.
    Extreme weather events are becoming more frequent and more severe.
    Many species are struggling to adapt to rapidly changing environments.
    Scientists warn that immediate action is needed to reduce greenhouse gas emissions.
    Governments around the world are implementing policies to combat climate change.
    Renewable energy sources such as solar and wind power are becoming more accessible.
    Individual actions like reducing waste and conserving energy can also make a difference.
    The future of our planet depends on the collective efforts of all nations.
    Education and awareness are key to driving meaningful change in society."""
    summarizer = TextSummarizer(text, percentage=50, num_threads=4)
    result = summarizer.summarize()
    assert isinstance(result, str)
    assert len(result) > 0
    assert len(result) < len(text)
