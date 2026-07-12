
def run_benchmark(router, prompts):
    results = []
    for p in prompts:
        features = {"context_tokens": len(p.split()), "repo_aware": False, "capabilities": []}
        model = router.pick_model(features)
        results.append({
            "prompt": p,
            "model": getattr(model, "name", None)
        })
    return results
