# Optical architecture relationships
As of November 20, 2026 (America/Phoenix). Source retrieval session crossed November 21 UTC. Research, not a valuation or production qualification audit.

## Decision
Broadcom is the strongest demonstrated merchant switch-plus-CPO candidate among this comparison set; this is a qualitative architecture judgment, not a universal benchmark or investment ranking. Coherent is a close direct public optical-components comparator for Lumentum. Marvell/Celestial and Ayar address optical scale-up/package I/O. NVIDIA is essential to any platform comparison.

| Group | Role | Economic question |
|---|---|---|
| AVGO / NVDA | Merchant Ethernet integration / accelerated-computing and fabric ecosystem | Who controls architecture, qualification and customer access? |
| MRVL / Celestial / proposed LITE | Custom silicon, electrical/optical connectivity and prospective laser/manufacturing integration | Do broader capabilities translate into cash earnings after dilution? |
| LITE / COHR | Optical components, lasers and broader optical products | Which qualified capacity earns durable margins? |
| Ayar / MRVL-Celestial | Optical I/O and scale-up connectivity | Which implementations become paid production rather than demonstrations? |
| TSM / GLW / packaging and test candidates | Foundry/advanced packaging and fiber attachment | Which process constrains yield, repairability and scale? |
| AAOI / FN / module ecosystem | Module production and manufacturing exposure | What content survives migration from pluggables to OBO/NPO/CPO? |

Rows for FN and additional packaging/test companies are research candidates, not newly verified supplier relationships.

## Evidence and relationship types
1. AVGO: Broadcom describes Tomahawk 6-Davisson CPO and a portfolio including switch silicon, optical DSPs, lasers, photodiodes and packaging. Breadth supports the qualitative integration judgment. Portfolio ownership is not proof every link is vertically supplied or that every product is shipping at volume. Source: https://investors.broadcom.com/news-releases/news-release-details/broadcom-showcases-industry-leading-solutions-scaling-ai
2. MRVL owns Celestial: acquisition completed February 2, 2026. Its Photonic Fabric addresses optical scale-up. Acquisition completion does not establish customer volume, realized margin or shipment qualification. Source: https://www.marvell.com/company/newsroom/marvell-completes-acquisition-of-celestial-ai.html
3. MRVL→LITE: announced acquisition, not completed. November 2 announcement gives 4.500 MRVL shares per LITE share and expected 1H CY2028 close, subject to approvals. Earlier conversation references to 5.5 conflict with retrieved terms. Verify amendments before any trade/conversion calculation. Source: https://investor.marvell.com/news-events/press-releases/detail/1040/marvell-and-lumentum-to-combine-creating-a-category-leader-in-ai-connectivity and filing https://investor.marvell.com/sec-filings/all-sec-filings/content/0001193125-26-442728/d352474d425.htm
4. NVDA↔LITE and NVDA↔COHR: separately announced nonexclusive strategic agreements, purchase commitments and $2B investment in each. Purchase commitments, equity financing and recognized revenue are distinct. They establish ecosystem alignment, not sole-supplier status. Sources: https://nvidianews.nvidia.com/news/nvidia-announces-strategic-partnership-with-lumentum-to-develop-state-of-the-art-optics-technology and https://nvidianews.nvidia.com/news/nvidia-and-coherent-announce-strategic-partnership-to-develop-optics-technology-to-scale-next-generation-data-center-architecture
5. Ayar↔NVDA: joined NVLink Fusion ecosystem June 2, 2026. Ecosystem compatibility is not proof of a particular NVIDIA GPU design win. Source: https://ayarlabs.com/news/ayar-labs-joins-nvidia-nvlink-fusion-ecosystem-to-bring-co-packaged-optics-to-rack-scale-ai-infrastructure
6. Ayar↔TSM/GUC/Wiwynn: November 10 company report describes TSMC-COUPE optical engines and an integrated optical compute demonstration. Demonstration and manufacturing-ready claims do not establish sustained commercial production or audited revenue. Source: https://ayarlabs.com/news/ayar-labs-wins-demo-of-the-year-award-at-2026-tsmc-north-america-technology-symposium/
7. LITE↔ALAB↔GLW: October 12 PCIe-over-optics proof of concept combines Scorpio switching, VCSEL optical links and multimode fiber. It extends PCIe transport; it does not remove PCIe semantics or prove optics embedded in a shipping GPU. Source: https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Astera-Labs-and-Corning-to-Demonstrate-1060-nm-VCSEL-Based-PCIe-over-Optics-for-AI-Rack-Scale-Connectivity-at-the-2026-OCP-Global-Summit/default.aspx
8. AVGO↔GLW: Corning identifies itself as a qualified supplier of fiber infrastructure for Bailly CPO. This is a named complementary supplier relationship. Do not extrapolate its role to every later platform without evidence. Source: https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2025/05/corning-collaborates-with-broadcom-to-accelerate-ai-data-center-processing-capacity.html
9. Ayar TeraPHY: package-level optical I/O with an electrical UCIe interface and external SuperNova light source. Product page says specifications are preliminary. Source: https://ayarlabs.com/teraphy/

## Interpretation and falsifiers
- Competition and complementarity coexist: optical-component firms can enable a platform while competing with that platform's internal optical products. Actual customer/product overlap requires named evidence.
- Optical I/O moves data; it does not turn an ordinary GPU into a photonic arithmetic processor or automatically replace caches, local metal wiring, coherence, PCIe or memory protocols.
- CPO, optical circuit switching, optical DSPs and optical computation are separate functions. Do not aggregate their market sizes as disjoint demand.
- Copper displacement is selective. Compare total link power, distance, latency, utilization held constant, repairability, yield, laser/fiber costs and amortized packaging.
- Hypothesis: architecture owners capture qualification/control value; component suppliers retain pricing where yields or reliable lasers constrain capacity. Falsifiers: second-source qualification, falling content per bandwidth, customers internalizing engines, weaker gross profit despite unit growth.
- Hypothesis: CPO adoption grows optical demand while changing module/DSP content. Falsifier of a blanket beneficiary thesis: higher optical bandwidth with lower revenue or profit per deployed rack for the studied supplier.
- Technology leadership is not stock attractiveness. EPS requires revenue, mix, margin, operating cost, tax and diluted shares; share return additionally depends on the entry multiple and later multiple.

## Existing work to reuse
These are unmerged branch artifacts, not authoritative integrated implementation:
- PR191, B04 #189: research/models/mrvl_lite/optical_competition_2026-11-20.json and case.json on work/189-mrvl-lite-maturation.
- PR292, B04 #290: research/models/MRVL/gaap-bridge-2026-11-20/ on work/290-mrvl-gaap-calendar-2028.
- PR277, B11 #273: research/AAOI/forward-valuation/ on work/273-aaoi-forward-valuation.
Read exact current heads before reuse; no competing EPS model created here.

## Review and limits
All current technical/commercial assertions above are attributed issuer statements; comparative rankings are inference. Exact supplier economics, production yields, CPO revenue splits and architecture market shares remain unknown. No live prices, forward multiples, quantitative probabilities or synthetic private-company EPS added. Canonical relationships/events are unchanged. Receiver access and prompt execution are pending.
