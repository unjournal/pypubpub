### Comparative Methodological Summary of PBMA vs. Meat Demand Studies

| **Dimension** | **Zhao et al. (2022)** *AEPP* | **Tonsor & Bina (2023)** *Working paper* | **Neuhofer & Lusk (2023)** *Working paper* | **Freitas-Groff et al. (2024)** *Working paper* |
|----------------|-------------------------------|-------------------------------------------|---------------------------------------------|-----------------------------------------------|
| **Econometric model** | Almost Ideal Demand System (AIDS) for fresh meat + PBMA. | Generalized AIDS (GAIDS) for beef, pork, chicken, PBMA. | Multivariate basket logit (random utility) over all ground meat options. | AIDS with demographic scaling + supplemental binary choice/event-study. |
| **Functional form** | Translog cost function, share eqns linear in log prices. | Share eqns with generalized price index (GAIDS). | Utility with linear price terms + pairwise γ interactions across items. | Translog AIDS with log-price interactions; probit for meat/no-meat. |
| **Estimation technique** | Iterative SUR (nonlinear least squares), constraints imposed. | SUR on weekly national data. | Maximum likelihood on household-week panel (≈4 M obs). | Nonlinear LS for AIDS; IV for cultural factors in ancillary regressions. |
| **Elasticities reported** | Uncompensated point elasticities (Marshallian). | Both uncompensated and compensated (Hicksian). | Arc elasticities from probabilities (uncompensated). | Uncompensated point elasticities; some arcs for interpretation. |
| **Data source & period** | Nielsen Retail Scanner (state-week), 2017–2020. | Nielsen Retail Scanner (national weekly), 2022. | Household panel (Nielsen/IRI), 2018–2020. | IRI consumer panel, 2004–2020. |
| **Product aggregation** | 7 meat categories + PBMA (category-level). | 4 broad categories: beef, pork, chicken, PBMA. | Ground beef, chicken, turkey, PBMA (ground only). | Broad meats + PBMA + traditional veg proteins (category aggregates). |
| **Inclusion/exclusion rules** | State-week aggregates, nonzero PBMA sales; processed meats excluded. | Retail at-home sales only; turkey/fish omitted. | HHs w/ any ground-meat or PBMA purchase 2018–20. | Full panel; aggregates counties/years to handle zeros. |
| **Controls** | Week + state FE, promotions, COVID-19 cases. | None reported (single-year time-series). | HH demographics, quarter FE, habit formation (lags). | Demographic scaling (income, age), cultural/media index, grocery volume. |
| **Cross-section vs. panel** | State-time panel (aggregate). | Weekly time-series (national). | Household-level dynamic panel (basket choices). | Repeated cross-sections + panel for event-study. |
| **Sample size** | 5,704 state-week obs. | 52 weeks (national). | ≈38 k HH × 104 weeks ≈ 4 M rows. | Tens of thousands HH per year (weighted to U.S. pop). |
| **Key assumptions / ID** | Two-stage budgeting (fixed meat budget); exogenous prices; symmetry imposed. | Static single-year demand; limited substitution set; assumes exogenous retail price changes. | No total expenditure constraint; prices exogenous; allows complementarity in baskets; assumes expanded IIA. | Preferences stable since 2004; broad aggregation; possible omitted cultural factors; limited IVs. |
| **Likely impact on cross-price results** | Conditional system constrains PBMA to compete *within* meat budget → small, sometimes complementary effects. | Narrow 4-good GAIDS, single-year snapshot → very small but precise cross-effects. | Ground-meat focus + basket model → precise but tiny elasticities, often complementary for poultry. | Broad, long-horizon model + underpowered PBMA data → noisy, imprecise, often insignificant cross-effects. |

---

**Summary**

- **Zhao et al.** use a conditional meat-budget AIDS: precise, tightly bounded, tiny cross-effects (PBMA complements red meat).
- **Tonsor & Bina** find similar magnitudes in a single-year GAIDS: small but significant cross-effects, stable substitution signs.
- **Neuhofer & Lusk**’s household-panel model gives tiny, precisely estimated elasticities—weak substitution for beef, complements for poultry.
- **Freitas-Groff et al.**’s long-run aggregate model yields noisy, often insignificant cross-effects: underpowered but consistent with near-zero substitution.

Together, differences stem mainly from:
(1) product scope (broad vs. ground meat),
(2) conditioning on fixed vs. total budget,
(3) time horizon and market maturity, and
(4) data granularity (aggregated vs. household).
All converge on the conclusion that **cross-price elasticities between PBMAs and animal meats are very small in magnitude.**

