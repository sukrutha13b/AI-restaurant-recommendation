import pytest
from unittest.mock import MagicMock, patch
from llm.client import GeminiRecommender, LLMError
from core.preferences import UserPreferences
from data.models import Restaurant

@pytest.fixture
def mock_restaurants():
    return [
        Restaurant(id="1", name="A", city="C", area="A", cuisines=["Italian"], price_range=1, rating=4.0, votes=100),
        Restaurant(id="2", name="B", city="C", area="A", cuisines=["Mexican"], price_range=2, rating=4.5, votes=200)
    ]

@pytest.fixture
def preferences():
    return UserPreferences(top_n=2)

@patch("google.genai.Client")
def test_recommender_successful_response(mock_client_class, mock_restaurants, preferences, tmp_path):
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    
    mock_response = MagicMock()
    # Mocking what the Gemini structured output would look like as JSON string
    mock_response.text = '{"recommendations": [{"restaurant_id": "1", "explanation": "Perfect match", "score": 0.9}]}'
    mock_instance.models.generate_content.return_value = mock_response

    client = GeminiRecommender(api_key="fake", cache_dir=str(tmp_path))
    recs = client.re_rank_candidates(mock_restaurants, preferences)
    
    assert len(recs) == 1
    assert recs[0].restaurant_id == "1"
    assert recs[0].explanation == "Perfect match"
    
@patch("google.genai.Client")
def test_recommender_handles_empty_candidates(mock_client_class, preferences, tmp_path):
    client = GeminiRecommender(api_key="fake", cache_dir=str(tmp_path))
    recs = client.re_rank_candidates([], preferences)
    assert recs == []

@patch("google.genai.Client")
def test_recommender_raises_llm_error_on_network_fail(mock_client_class, mock_restaurants, preferences, tmp_path):
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_instance.models.generate_content.side_effect = Exception("Network timeout")
    
    client = GeminiRecommender(api_key="fake", cache_dir=str(tmp_path))
    with pytest.raises(LLMError, match="Gemini API invocation failed"):
        client.re_rank_candidates(mock_restaurants, preferences)

@patch("google.genai.Client")
def test_recommender_raises_llm_error_on_bad_json(mock_client_class, mock_restaurants, preferences, tmp_path):
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    mock_response = MagicMock()
    mock_response.text = '{"bad": "schema"}'  # Missing 'recommendations' list
    mock_instance.models.generate_content.return_value = mock_response

    client = GeminiRecommender(api_key="fake", cache_dir=str(tmp_path))
    with pytest.raises(LLMError, match="Failed to parse or validate"):
        client.re_rank_candidates(mock_restaurants, preferences)
