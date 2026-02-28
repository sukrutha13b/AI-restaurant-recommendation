from llm.parser import LLMRecommendationOut, LLMResponseEnvelope
from pydantic import ValidationError
import pytest

def test_llm_recommendation_out_valid():
    data = {
        "restaurant_id": "123",
        "explanation": "Great vibe.",
        "score": 0.95
    }
    rec = LLMRecommendationOut(**data)
    assert rec.restaurant_id == "123"
    assert rec.explanation == "Great vibe."
    assert rec.score == 0.95

def test_llm_recommendation_out_invalid_score():
    data = {"restaurant_id": "1", "explanation": "x", "score": 1.5}
    with pytest.raises(ValidationError):
        LLMRecommendationOut(**data)

def test_envelope_parsing():
    data = {"recommendations": [{"restaurant_id": "1", "explanation": "x", "score": 0.5}]}
    env = LLMResponseEnvelope(**data)
    assert len(env.recommendations) == 1
    assert env.recommendations[0].restaurant_id == "1"
