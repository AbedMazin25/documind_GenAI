import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_raft_generates_samples():
    with patch("app.rag.raft_generator._client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content=(
                '{"samples": [{"question": "What is revenue?", "answer": "$100M", "cot": "Line 1 says 100M"}], '
                '"distractors": ["Unrelated passage about weather."]}'
            )))]
        ))
        from app.rag.raft_generator import raft_gen
        chunks = ["Apple revenue was $100M in Q3 2024. This represents 12% YoY growth."] * 3
        samples = await raft_gen.generate_dataset(chunks, samples_per_chunk=1)
        assert len(samples) >= 1
        assert "question" in samples[0]
        assert "oracle_context" in samples[0]

@pytest.mark.asyncio
async def test_raft_handles_json_error():
    with patch("app.rag.raft_generator._client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="I cannot help with that."))]
        ))
        from app.rag.raft_generator import raft_gen
        result = await raft_gen.generate("Some financial text.", n=1)
        assert result == []
