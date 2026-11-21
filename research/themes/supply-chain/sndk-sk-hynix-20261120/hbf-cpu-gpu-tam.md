# CPU/GPU integration expands NAND's serviceable market
B19 #309 research v6, as-of Nov20 2026 Phoenix, retrieved Nov21 UTC. Branch work/309-sndk-sk-hynix-comparison. Extends existing comparison; no new quote ingestion or shared valuation model.

## Finding
HBF can expand NAND's role into near-processor inference memory, in addition to SSD storage. This supports a structurally broader demand thesis for Sandisk and SK hynix. Technical compatibility and issuer illustrations are not production design wins, confirmed annual shipments or incremental revenue forecasts.

## What integration means
Separate NAND-derived HBF stacks with a logic/base die, packaging and host interface connected near a processor. Sandisk's July2025 fact sheet explicitly depicts HBF stacks, interposer, processor die and package substrate, including GPU/CPU/TPU/SoC. Concept diagrams show mixed HBM+HBF and multiple-terabyte HBF configurations. They are conceptual, not a shipping NVIDIA/AMD/Intel product.
Aug2026 specification: SK describes UCIe host integration and capacities up to512GB per stack configuration; bandwidth grades approximately0.4–3TB/s. Sandisk describes xPU-HBF interface. Do not assume every generation ships at the highest bandwidth or infer full processor-system bandwidth by adding nominal stack rates without interface limits.
HBF remains distinct from DRAM/HBM in latency, write behavior, endurance and access granularity. Sandisk's modeling footnote explicitly acknowledges higher latency and larger pages. Similar aggregate read bandwidth is not identical memory semantics. Suitability strongest for read-heavy inference/model weights and managed memory tiering; active frequently rewritten data may still require DRAM/HBM.

## TAM mechanisms and maturity
| Path | Demand mechanism | Maturity/evidence |
|---|---|---|
| Inference GPU/accelerator HBF | More near-compute capacity per accelerator; larger resident models, fewer transfers or distributed shards | HBF standard plus issuer package concepts; qualification/volume design wins unverified |
| CPU/SoC-attached HBF | Persistent model/data capacity close to host or custom processor | Interface supports processor diversity; not evidence of universal CPU attachment |
| Rack/pod flash context tier | More flash for shared inference context, KV caching and reuse | NVIDIA CMX architecture documented; Ethernet-attached tier, separate from co-packaged HBF |
| Edge/robotics/autonomous systems | Local models/persistent state with power/thermal constraints | Potential market extension, no verified per-device HBF shipments or content forecast |

Greater capacity per compute device, new memory placement and potentially higher-value controller/packaging content can expand supplier revenue. Supplier margin share depends on who owns base die/controller/package/system IP; not all module BOM belongs to NAND supplier.
Lower cost per token can induce more inference deployment, but demand elasticity is unknown. More NAND bytes need not mean a larger total memory dollar pool if it displaces expensive HBM/DRAM or traditional SSD capacity.

## Bottom-up sizing, purely illustrative
Annual HBF revenue opportunity = eligible annual processor shipments * attach rate * TB per adopted processor * supplier realized USD/TB.
Use ADOPTED processors directly to avoid multiplying attach twice.
At hypothetical supplier realizationUSD500/TB:
| Per1million adopted processors annually | HBF capacity | Gross HBF market revenue |
|---|---:|---:|
|1TB each|1EB|USD0.5B|
|2TB each|2EB|USD1B|
|4TB each|4EB|USD2B|

Example10million adopted processors/year *2TB*USD500/TB=USD10B annual industry HBF revenue,20EB capacity.
At hypothetical Sandisk share25%, revenueUSD2.5B; net margin25–35%; diluted shares1.2B post split: EPS contributionUSD0.5208–0.7292 BEFORE displaced existing profit, additional development/qualification costs beyond assumed margin, ramp losses and capital/working-capital demands.
All units, attach, ASP, margin and share inputs are assumptions; not management guidance, customer commitments or forecasts. No year assigned. USD500/TB is illustrative supplier realization, not verified HBF price or commodity NAND quotation.
For earnings truly incremental to an existing forecast, subtract displaced NAND/SSD profit and any HBF already included in the baseline. Do not simply add modeled revenue to company datacenter guidance.
Sandisk's1.2ZB2030 enterprise datacenter flash market is a broader industry capacity forecast; HBF may overlap.20EB is1.67% of1.2ZB by capacity, not equal revenue share, and adding the full HBF estimate to1.2ZB would risk double counting.
Annual TAM is annual shipments, not installed GPU/CPU stock times capacity.

## SNDK versus SK
SNDK: route from NAND/SSDs into processor-adjacent memory content; CBA/NAND design and emerging HBF implementation can support product differentiation/qualification stickiness. Smaller portfolio makes the category more consequential to mix, but share/royalties not verified.
SK: can supply HBM/DRAM, NAND/Solidigm and HBF; packaging and system/customer relationships provide a potential broader integration offering. Displacing some HBM means the net benefit needs product-level analysis; no automatic addition of full HBM TAM to NAND TAM.
Both are primary contributors to the shared open standard. Shared standard is not exclusive mutual licensing economics and not proof of interchangeable qualified products. Company-specific implementation IP/yield/power/firmware can still differ.
Google and Tenstorrent named as consortium members; membership is not binding purchases, shipment commitments or a confirmed deployed product. No primary-source named NVIDIA, AMD or Intel HBF production win verified.
NVIDIA CMX independently demonstrates flash extending the GPU memory hierarchy at pod level. Do not label it a Sandisk HBF design win, processor co-package, or proof of supplier market share.

## Timing
Sandisk Oct29 FY27Q1 presentation: first HBF memory die taped out; first HBF-based product samples targeted next calendar year2027.
SK Feb2026 release: industry expects complex memory solutions including HBF demand to pick up around2030. Issuer outlook, not guaranteed volume ramp.
2027 sampling, subsequent qualification and possible later expansion are separate states; no precise2028 commercial revenue or2030 penetration verified.
This possibility can change long-run growth and moat assumptions but does not by itself repair near-term NAND ASP/margin stress. Earlier price illustrations remain conditional and do not include a separately quantified HBF upside.

## Sources
Primary:
1. https://www.sandisk.com/company/newsroom/press-releases/2026/2026-08-03-Sandisk-and-sk-hynix-advance-global-standardization-of-hbf (Aug3 specification/interface and consortium)
2. https://news.skhynix.com/en/hbf-at-fms-2026/ (Aug4 specification, UCIe, capacity/bandwidth grades)
3. https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/sandisk/collateral/company/Sandisk-HBF-Fact-Sheet.pdf (July2025 concept architecture and simulation limitations)
4. https://investor.sandisk.com/static-files/4ca97b6e-7da4-4d52-b4ac-0e80f462716f (Oct29 die tape-out and2027 sample target)
5. https://news.skhynix.com/en/sk-hynix-and-sandisk-begin-global-standardization-ofnext-generation-memory-hbf/ (Feb26 outlook around2030)
6. https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/ (Mar16 CMX Ethernet-attached flash)
7. https://www.sandisk.com/company/newsroom/press-releases/2026/2026-08-13-sandisk-investor-day-2026 (1.2ZB2030 market)

## Review and next action
Primary technical material opened; mechanism/maturity/overlap classified. JS arithmetic executed for TAM andEPS example. No production code/tests; no forecast validation or independent CI claim. Exact prices, shipments, customer design wins, yield, endurance and margins remain unknown.
Next: track first named processor/platform HBF qualification and separate production purchase commitments from ecosystem participation before revising earnings.
