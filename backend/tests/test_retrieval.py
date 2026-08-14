from app.rag.retrieval import reciprocal_rank_fusion
def test_rrf_rewards_consensus():
    s=reciprocal_rank_fusion([["a","b"],["a","c"]])
    assert s["a"]>s["b"] and s["a"]>s["c"]
