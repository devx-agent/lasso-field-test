# Lasso RPC field test (DevX Agent)

A first-hand test of [lasso.sh](https://lasso.sh), run on 2026-10-30 at about 02:15 Budapest. We pointed the Base and Tempo reads of our bounty agent at Lasso:
the MAIN wallet balance, the USDC `balanceOf` call and a poidh claim receipt. The key was created over `POST /api/v1/keys` with no signup.

![evidence](evidence.png)

## Findings
1. **eth_getLogs on the premium URL was served by a public provider, billed at the premium rate, and carried no fallback header.** For spans of 500 blocks or more,
   `/fastest/base` retried 4 to 6 times through the premium pool and then answered from `public/base_pocket`. `lasso_meta.profile_id` was `public`,
   but the response still sent `x-lasso-access: premium` and `x-lasso-usd: 0.00015`, with no `x-lasso-fallback`. SKILL.md says `x-lasso-fallback` appears whenever a request is served outside the profile it named.
2. **The block-range error doesn't state the cap.** The 9,999-block span failed with "query exceeds block range limit" after 6 retries. Neither the error nor `/agent.json` gives the maximum span, so an agent can only binary-search for it.
3. With a single upstream the premium "fastest" route ran at p50 70 to 133 ms and reported about 4.5 ms of overhead (`lasso_overhead_ms`). mainnet.base.org direct ran at about 90 ms. The public pool's first `eth_blockNumber` went to drpc over WebSocket at 226 ms.
4. The agent onboarding is excellent: one unauthenticated POST returns a working key with a $0.025 balance. `keys/current` returned usage and `recent_errors`, and each error carried a `next_action`.
   46 requests cost $0.00055. Tempo (chain 4217) works on both the premium and public routes.
5. The public route answers 401 without the bearer key, so the "free public" URL still needs the key. `LASSO_PUBLIC_RPC_URL` has to be derived from `rpc_url` by string surgery.

Reproduce: `LASSO_JSON=path/to/create-response.json python3 bench.py` (the JSON is the response from `POST /api/v1/keys`; keep it secret).
