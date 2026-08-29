# Appeal Ground Response Coverage Covenant

Standalone GenLayer Intelligent Contract for a revision-bound, consensus-validated coverage receipt over a locked appeal-ground set. It answers only whether the submitted final response materially addresses every locked ground; it does not decide legal merits or legal compliance.

## API

Writes: `file_appeal`, `lock_grounds`, `submit_response`, `assess_coverage`, `correct_response`, `close_case`.

Deterministic view: `read_case` exposes lifecycle, actors, ground IDs, current response revision, append-only revision history, normalized decision fields, omitted grounds, bounded explanation/references, evidence digest and `closure_ready`.

## Consensus engineering

One `run_nondet_unsafe` execution per assessment. Leader and validators independently fetch the same three digest-bound public texts and compare every consequence-bearing normalized field, including each ground result. Storage writes happen after consensus. Failures are fail-closed and cannot set `closure_ready`.

## Verification

```powershell
genvm-lint check contracts/appeal_ground_response_coverage_covenant.py
python -m pytest tests/direct tests/integration -q
```

### Final Studionet evidence

- Network: Studionet, chain ID `61999`.
- Contract: [`0xc7140be95ac4d9A3606aFE84D3707a9dc8D7BB40`](https://explorer-studio.genlayer.com/address/0xc7140be95ac4d9A3606aFE84D3707a9dc8D7BB40).
- Deployment: [`0x911de41534ad0419d524eb6df273015f0fb616db40939bedc32f9408f5196bc8`](https://explorer-studio.genlayer.com/tx/0x911de41534ad0419d524eb6df273015f0fb616db40939bedc32f9408f5196bc8).
- Deployed source SHA-256: `194bb846b090d24f4df80ad8bb0d9245fcd69cfb7c41fe59e3e4f3ef7d0e2e12`.
- E2E gate: PASS. Every required scenario below has a finalized receipt, consensus/result evidence, authoritative readback, and Explorer link.

Required live paths:

- Covered case `e2e-covered-002`: file [`0x508f946a21b962eca8ef298fd47f21e500587d346f9d22515f0494d79185dc0b`](https://explorer-studio.genlayer.com/tx/0x508f946a21b962eca8ef298fd47f21e500587d346f9d22515f0494d79185dc0b), lock [`0x0fb14c617b4d02a3d8598e41bc05cbb7bcb1140027447854e9651da053717386`](https://explorer-studio.genlayer.com/tx/0x0fb14c617b4d02a3d8598e41bc05cbb7bcb1140027447854e9651da053717386), response [`0xdbd3ec52561b7d89ead1a0b530131a288ba79d8b5af76a217aeba33e064c029b`](https://explorer-studio.genlayer.com/tx/0xdbd3ec52561b7d89ead1a0b530131a288ba79d8b5af76a217aeba33e064c029b), assessment [`0xa1024ff96aa73356b8db412f2260cdb162dc8fd5383c50e0ed83277a82e45a97`](https://explorer-studio.genlayer.com/tx/0xa1024ff96aa73356b8db412f2260cdb162dc8fd5383c50e0ed83277a82e45a97), and close [`0xd7cc44c3610deb18c38e29d0f9c25e6b72a050c15e839da37a5d815bc4a3d39c`](https://explorer-studio.genlayer.com/tx/0xd7cc44c3610deb18c38e29d0f9c25e6b72a050c15e839da37a5d815bc4a3d39c). Readback: `COVERED`, `closure_ready=true`, then `CLOSED`, `is_closed=true`.
- Correction case `e2e-gap-002`: file [`0xc5f7e73b90149e63652d2f7c4ec92933d62de81ece0fae8a86f4e73fb326d73e`](https://explorer-studio.genlayer.com/tx/0xc5f7e73b90149e63652d2f7c4ec92933d62de81ece0fae8a86f4e73fb326d73e), lock [`0x2c2a930ef7b136390ad63b4d8b06a9db0316f0b296ec65f7fff6acd2522bb416`](https://explorer-studio.genlayer.com/tx/0x2c2a930ef7b136390ad63b4d8b06a9db0316f0b296ec65f7fff6acd2522bb416), response [`0x895eefd1ad6392b177703fab76ac95f68d144d0426f0527a8ca3f611b5fa9e5d`](https://explorer-studio.genlayer.com/tx/0x895eefd1ad6392b177703fab76ac95f68d144d0426f0527a8ca3f611b5fa9e5d), omitted-ground assessment [`0x687ffbac8cca03cf89696ebf71f75858ba2cb38a7e0af49ffcc5288c8d69f417`](https://explorer-studio.genlayer.com/tx/0x687ffbac8cca03cf89696ebf71f75858ba2cb38a7e0af49ffcc5288c8d69f417), owner close rejection [`0x9e8a825a8987d025f9a531732c243eb90d8cda972740fd2d3cf1204ed43993f8`](https://explorer-studio.genlayer.com/tx/0x9e8a825a8987d025f9a531732c243eb90d8cda972740fd2d3cf1204ed43993f8), correction rev-2 [`0xbf0befea79e854e6f96608b58816653bb4b64bf67cfb3cbcfbd992591399e1af`](https://explorer-studio.genlayer.com/tx/0xbf0befea79e854e6f96608b58816653bb4b64bf67cfb3cbcfbd992591399e1af), reassessment [`0xc29361809307c10944b2b105193ee218cb1b01daaf6e37ef778d193326c289b6`](https://explorer-studio.genlayer.com/tx/0xc29361809307c10944b2b105193ee218cb1b01daaf6e37ef778d193326c289b6), and close [`0x9806c2680331b7d3e75307432360e0e336783642f679e79809a5f7a8b6e5d986`](https://explorer-studio.genlayer.com/tx/0x9806c2680331b7d3e75307432360e0e336783642f679e79809a5f7a8b6e5d986). Readbacks: `GAPS_FOUND` with omitted `g2`, close rejected with state unchanged, `CORRECTED` with revisions 1 and 2, then `COVERED`, then `CLOSED`.
- Unauthorized writer case `e2e-auth-001`: file [`0xf946c7c36e8fce7de3af17a872c649fe57565d19230ecb050635072dabf40396`](https://explorer-studio.genlayer.com/tx/0xf946c7c36e8fce7de3af17a872c649fe57565d19230ecb050635072dabf40396); reader submit [`0x52d653fb4b3dae0d758d01b3fb74d736d9110b6957794601132ac5e0ee7da8a6`](https://explorer-studio.genlayer.com/tx/0x52d653fb4b3dae0d758d01b3fb74d736d9110b6957794601132ac5e0ee7da8a6). Readback remained `FILED`; receipt was finalized `ERROR`.
- Invalid evidence case `e2e-bad-evidence-001`: file [`0xb6ef8705a6d491c35414114fe7c9ba540feaace2799ef991e514093fb2a0c5cb`](https://explorer-studio.genlayer.com/tx/0xb6ef8705a6d491c35414114fe7c9ba540feaace2799ef991e514093fb2a0c5cb), lock [`0x02842270596e3bfc269d28f611bde8cdbace78e45b6b04cbe76bf9ae9fa996ec`](https://explorer-studio.genlayer.com/tx/0x02842270596e3bfc269d28f611bde8cdbace78e45b6b04cbe76bf9ae9fa996ec), response [`0x946ed1ba0209d1fa8e59b264012ba694969954b2f61d1f8abd76dee63eb0ba07`](https://explorer-studio.genlayer.com/tx/0x946ed1ba0209d1fa8e59b264012ba694969954b2f61d1f8abd76dee63eb0ba07), assessment [`0x80fd73a2a16804c7370636f14a3d3931747824783732bc47765945d743e35b08`](https://explorer-studio.genlayer.com/tx/0x80fd73a2a16804c7370636f14a3d3931747824783732bc47765945d743e35b08). Readback remained `RESPONSE_SUBMITTED`; receipt was finalized `ERROR`/`UNDETERMINED`.

## Reuse and limits

The reusable primitive is an argument-set-to-response coverage receipt for downstream case-closure workflows. It performs no payment, access grant, legal determination, external actuation, cross-contract call or private-data processing.
