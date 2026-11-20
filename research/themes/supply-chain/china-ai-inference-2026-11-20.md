# Chinese AI development and inference economics

B19 research snapshot, 2026-11-20. Worker #285, branch work/285-china-ai-inference. Historical benchmark and scenario v2.

China has multiple independent model developers, evidence of large domestic training runs and domestic inference serving real users. Leadership in open weights and competitive token prices can coexist with a US lead on difficult reasoning and weaker domestic capacity per megawatt. No matched facility-metered benchmark or invoice-based fleet TCO was verified.

## Development and supply

Artificial Analysis v5.0.1 on November 16, rounded as reported by [Danske Bank, p.25](https://research.danskebank.com/link/AIinvestmenttrackerNovember2026201126/%24file/AI%20investment%20tracker%20November%202026_201126.pdf): Fable 5.2 65, GPT-6.2 Astra 62, Gemini 4 Neon 61, Kimi K3.1 Pro 46 (highest open weights), Qwen4 Max 43, DeepSeek V4.1 Flash 33. Index point differences do not measure percent capability.

[DeepSeek V3](https://huggingface.co/deepseek-ai/DeepSeek-V3) reports 37B active of 671B total parameters, 14.8T training tokens and 2.788M NVIDIA H800 hours. At the paper's assumed $2/hour this yields $5.576M for reported training compute. Company-wide R&D and unsuccessful experiments require separate evidence. [Huawei Pangu Ultra](https://arxiv.org/abs/2504.07866) reports a 135B dense model trained using 8,192 Ascend devices. [Zhipu's interim filing, p.19](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0924/2026092401583.pdf) reports serving GLM-5.3-Flash traffic on domestic chips. Neither demonstration establishes domestic training provenance for Kimi K3.1 Pro. [Reuters, October 28](https://www.reuters.com/world/china/chinas-cxmt-start-advanced-ai-memory-production-despite-poor-yields-sources-say-2026-10-28/) reports early domestic HBM3E yield challenges. Installed volume, deliverable good units and commercial pricing matter separately.

## Ownership economics per million generated tokens

Scenario combines historical system power estimates with different R1 benchmarks. No synchronized wattmeter measurements. Huawei FlexNPU fixed 1024/1024 token inputs/outputs, first token <=1 s and subsequent tokens <=50 ms, 618.18 requests/s times 1024 = 633,016 generated tokens/s. GB200 MLPerf v6.1 interactive 240,274 tokens/s at 1.5s/15ms, with a different prompt set and accuracy target. Comparisons are conditional. [FlexNPU](https://arxiv.org/abs/2606.04415), [throughput reconstruction](https://margins.ashitaorbis.com/research/dive-ascend), [MLPerf results](https://developer.nvidia.com/ai-hardware-benchmarks).

Assume $8.2M Huawei, $3M NVIDIA acquisition, active IT system power 559/145 kW respectively. Estimates from [system-price reconstruction](https://margins.ashitaorbis.com/research/dive-ascend), [Banca d'Italia, table A1](https://www.bancaditalia.it/pubblicazioni/qef/2026-1006/QEF_1006_26.pdf?language_id=1), [SemiAnalysis](https://semianalysis.com/2025/04/16/huawei-ai-cloudmatrix-384-chinas-answer-to-nvidia-gb200-nvl72/). Assume four-year straight-line life, no salvage, 10% of purchase cost annually for operations, PUE 1.20, $0.08/kWh, 100% utilization at each cited benchmark rate for 8,760 hours/year. Financing, construction, training, taxes and extraordinary replacements are outside the scenario.

Let T be generated tokens/s, P be IT kW and K be purchase price in USD. Annual million tokens M = T * 3600 * 8760 / 1e6. Annual facility energy E = P * 1.2 * 8760. USD/M = (0.35*K + 0.08*E)/M. IT tokens/J = T/(1000*P).

| System | IT tokens/J | Facility kWh/M | Equipment and operations USD/M | Electricity USD/M | Total USD/M |
|---|---:|---:|---:|---:|---:|
| CloudMatrix384 | 1.13 | 0.294 | 0.14377 | 0.02355 | 0.16732 |
| GB200 NVL72 | 1.66 | 0.201 | 0.13857 | 0.01609 | 0.15466 |

Huawei costs 8.2% more relative to GB200 under these assumptions. Economic parity at the GB200 tariff of $0.08/kWh requires Huawei electricity around $0.037/kWh. Energy parity threshold = 240274 * 559 / 145 = approximately 926,300 generated tokens/s on the same workload. Compare end-to-end quality, P95/P99 latency, retries, billable reasoning, realized utilization and uptime. The current benchmark is a prior-generation reference. [Huawei announced Atlas 960E](https://www.huawei.com/en/news/2026/9/hc-ascend960-supernode). NVIDIA lists Vera Rubin interactive R1 at 652,750 tokens/s. New platform parity requires measured system power plus delivered cost and matched traffic.

[DeepSeek customer tariff](https://api-docs.deepseek.com/quick_start/pricing/) observed November 20: V4.1 Flash $0.30/$1.20 peak per million uncached input/output, $0.15/$0.60 off-peak. These are different models and accounting boundaries from the R1 infrastructure scenario. For deployment compare total spend and facility energy per accepted task across a shared workload, including rework.

## Current-generation comparison, November 20

[MUFG, November 18, p.3](https://www.mufgamericas.com/sites/default/files/document/mufgamericas_com/2026-11/Chart_of_the_Day_11_18_Nvidia.pdf) reports 4 TB/s memory bandwidth and 144 GB per Ascend 950DT against 4.8 TB/s and 141 GB for H200, 8 TB/s and 288 GB for B300, and up to 22 TB/s and 288 GB for Rubin. [NVIDIA's specifications](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/) corroborate Rubin's maxima. On these memory metrics the 950DT resembles Hopper, two NVIDIA architecture steps behind Rubin. Rubin's 5.5x bandwidth and 2x capacity are chip specifications, not token or TCO multipliers. MUFG's estimated 1,000 W versus 2,300 W chip power ratings imply about 2.4x peak bandwidth per rated chip watt. This proxy excludes the host, switches, and actual workload behavior.

[NVIDIA's November MLPerf Endpoints report](https://developer.nvidia.com/blog/nvidia-vera-rubin-nvl72-leads-agentic-inference-performance-on-mlperf-endpoints-v1-0) shows 5–10x the throughput per kW of GB300 on selected agent workloads. This is an NVIDIA generational comparison. Huawei [targets Q1 2027 for 960DT](https://www.huawei.com/en/news/2026/9/hc-wang-keynote). National time-to-parity and loaded 950DT/Rubin USD per million tokens or tokens per facility watt are unresolved. At 100% utilization an inference operator still needs matched throughput, power and acquisition cost. The older 8.2% ownership-cost scenario cannot be transferred to Rubin.


## Can China supply domestic AI demand?

November 20 assessment: domestic inference can expand materially, while frontier training and total unmet demand remain constrained. [Tencent Q3 results](https://www.tencent.com/wp-content/uploads/2026/11/Tencent-Announces-2026-Third-Quarter-Results.pdf) report increasing allocations to model serving and GPU rental. [Reuters, Nov 20](https://www.reuters.com/business/retail-consumer/us-ai-chip-curbs-hit-china-tech-stocks-spur-self-sufficiency-push-2026-11-20/) reports Tencent expects domestic chips to support inference while its next model slows; Alibaba reports constrained supply. Revenue growth alone cannot quantify unmet token demand.

[IFP October forecast](https://ifp.org/how-to-increase-americas-ai-lead-over-china/) estimates domestic production of 0.986M H100-equivalents in 2026 and 1.3M in 2027, on top of 0.743M at end-2025. Without retirements, domestic-origin compute thus rises from 1.729M to 3.029M (+75%). These are equivalent compute units, not physical shipments or measured inference throughput. Of its projected 8.8M total accessible in 2027, 2.8M is offshore. Its 4.6M 2026 total includes 1M offshore. By subtraction estimated mainland stocks grow 3.6M to 6.0M, including foreign hardware. These estimates predate November restrictions and do not measure demand. Domestic-origin additions represent about 31% of the projected 4.2M increase in all accessible compute.

At full load 10 GW of facility power consumes 87.6 TWh/year, under 0.93% of [China's 2025 net electricity demand](https://www.iea.org/reports/electricity-2026/demand). This is a scale reference, with no implied spare power. [Rystad](https://www.rystadenergy.com/news/chinas-data-center-capacity-doubling-of-power) estimates 32 GW of all data center capacity at end-2025 and 28 GW of additions through 2030. [Reuters](https://www.reuters.com/business/energy/chinas-push-green-power-use-ai-projects-faces-hurdles-experts-say-2026-06-22/) documents local grid and firm supply obstacles. Future evidence: domestic accelerator systems commissioned and accepted, workload throughput and latency, reported queues and available capacity.
