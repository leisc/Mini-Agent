from mini_agent.tools.context_selector import ContextSelector


def test_selects_relevant_document():
    selector = ContextSelector()
    docs = [
        {"text": "The system encountered an error while saving file.", "ts": 9999999999, "id": "log1"},
        {"text": "Release notes: added new endpoint for payments.", "ts": 1000000000, "id": "notes1"},
    ]
    msgs = [
        "User: How do I fix file save error?",
        "Assistant: Try checking permissions.",
    ]

    selected = selector.select_context(query="file save error", documents=docs, messages=msgs, token_budget=200)

    # ensure at least one selected item and that the highest scored contains 'error'
    assert len(selected) >= 1
    top = selected[0]
    assert "error" in top["text"].lower() or "error" in top["metadata"].get("id", "")


def test_respects_token_budget():
    selector = ContextSelector()
    long_doc = "word " * 1000
    docs = [{"text": long_doc, "ts": 9999999999}]
    selected = selector.select_context(query="word", documents=docs, token_budget=10)
    # should include truncated version (not exceed budget)
    total_tokens = sum(it["est_tokens"] for it in selected)
    assert total_tokens <= 10
