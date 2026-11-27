# Formulas
- Sequential betas: r_i = a + b_M r_M + b_S r_{S|M} + b_G r_{G|S} + e_i (each level orthogonalised to levels above, ex-self).
- ICC(1) = (MSB - MSW) / (MSB + (n0 - 1) MSW), n0 = (n - sum(n_g^2)/n)/(k - 1).
- Forbes-Rigobon: rho* = rho / sqrt(1 + d (1 - rho^2)), d = var_stress/var_calm - 1.
- Shrinkage: b_shrunk = w b_i + (1 - w) b_G, w = tau^2 / (tau^2 + s_i^2).
- Event-day spillover: AR_j = r_j - (a_j + b_j r_M), summed over the window.
Code: `engines/valuation/relative_value/sympathy.py` (`icc1`, `loo_mean`, `analyse`).
