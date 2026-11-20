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