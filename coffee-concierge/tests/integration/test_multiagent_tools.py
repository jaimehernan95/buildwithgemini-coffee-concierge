import pytest
from app.agent import (
    root_agent,
    nutritionist_agent,
    order_logistics_agent,
    sommelier_guide_agent,
    query_coffee_analytics_db,
    execute_coffee_python_analysis,
    convert_currency,
    lookup_coffee_guide,
)

def test_multiagent_hierarchy_registration():
    """Verify all specialized subagents are properly wired to the root orchestrator."""
    assert root_agent.name == "root_agent"
    subagent_names = [sub.name for sub in root_agent.sub_agents]
    assert "nutrition_analyst_agent" in subagent_names
    assert "order_logistics_agent" in subagent_names
    assert "coffee_sommelier_agent" in subagent_names

def test_sql_analytics_tool():
    """Test SQL query tool on starbucks_drinks table."""
    res = query_coffee_analytics_db("SELECT beverage_name, category, size, calories, caffeine_mg FROM starbucks_drinks WHERE category = 'Cold Brew' LIMIT 2")
    assert res.get("success") is True
    assert res.get("count") == 2
    assert "beverage_name" in res["rows"][0]
    assert res["rows"][0]["category"] == "Cold Brew"

def test_python_pandas_analytics_tool():
    """Test Python sandbox code execution with pre-injected drinks_df."""
    code = """
venti_drinks = drinks_df[drinks_df['size'] == 'Venti']
avg_caffeine = venti_drinks['caffeine_mg'].mean()
result = {'avg_caffeine': round(avg_caffeine, 2), 'count': len(venti_drinks)}
"""
    res = execute_coffee_python_analysis(code)
    assert res.get("success") is True
    assert "output" in res
    assert res["output"]["count"] > 0
    assert res["output"]["avg_caffeine"] > 100

def test_currency_conversion_tool():
    """Test currency conversion tool returns valid converted values."""
    res = convert_currency(amount_usd=5.0, target_currency="EUR")
    assert "converted_amount" in res
    assert res["converted_amount"] > 0
    assert res["target_currency"] == "EUR"

def test_coffee_guide_tool():
    """Test coffee guide API retrieval."""
    res = lookup_coffee_guide(beverage_name="espresso")
    assert "title" in res or "available_drinks" in res


def test_firestore_session_persistence():
    """Verify enterprise distributed session persistence in Firestore."""
    from app.session_persistence import session_store
    sess_id = "test_eval_session_99"
    saved = session_store.save_session(sess_id, "tester@google.com", [{"role": "user", "text": "Espresso"}])
    assert saved is True
    loaded = session_store.get_session(sess_id)
    assert loaded is not None
    assert loaded["session_id"] == sess_id
    assert loaded["messages"][0]["text"] == "Espresso"
