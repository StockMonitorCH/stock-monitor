"""
portfolio_analysis_texts.py — Textbausteine für die erweiterte Portfolio-Synthese
Kein API-Key. Rein regelbasiert. ~140 Schnipsel, 5 Module.

Struktur:
  M1 = Eröffnung       (Archetype × Performance)
  M2 = Rendite/Risiko  (Beta × Sharpe × Alpha)
  M3 = Was passierte   (Drawdown × Beta × RSI)
  M4 = Marktkontext    (Sektor × ECY × Monte Carlo)
  M5 = Abschluss       (Risiko + Chance + Gesamtfazit)

Platzhalter: {top_sym}, {top_pct}, {sector}, {counter_sector}, {mc_pct}
Werden zur Laufzeit durch echte Werte ersetzt.
"""

# ══════════════════════════════════════════════════════════════════════════════
# MODUL 1 — Eröffnung / Portfolio-Charakter
# Schlüssel: (archetype, perf_class)
# archetype: aggressive_growth | speculative | momentum_trend | balanced |
#            defensive | diversified | dividends_income |
#            buy_and_hold | high_risk | retirement
# perf_class: strong_pos | pos | flat | loss
# ══════════════════════════════════════════════════════════════════════════════

M1 = {

    # ── Aggressiver Wachstumsinvestor ─────────────────────────────────────────
    ("aggressive_growth", "strong_pos"): {
        "DE": (
            "Dein Portfolio zeigt das Profil eines aggressiven Wachstumsinvestors — "
            "und die Wette geht bisher auf. Die Ausrichtung auf wachstumsstarke Titel "
            "hat klare Früchte getragen und einen messbaren Mehrwert gegenüber dem Markt erzeugt."
        ),
        "EN": (
            "Your portfolio shows the profile of an aggressive growth investor — "
            "and the bet is paying off so far. The focus on high-growth positions "
            "has delivered clear results and generated measurable outperformance."
        ),
    },
    ("aggressive_growth", "pos"): {
        "DE": (
            "Dein Portfolio ist klar auf Wachstum ausgerichtet — mit allem was dazugehört: "
            "Chancen, aber auch erhöhtes Risiko. Die bisherige Performance ist positiv, "
            "aber diese Struktur verlangt konstante Aufmerksamkeit."
        ),
        "EN": (
            "Your portfolio is clearly growth-oriented — with everything that entails: "
            "Opportunities, but also elevated risk. Performance is positive so far, "            "but this structure demands constant attention."
        ),
    },
    ("aggressive_growth", "flat"): {
        "DE": (
            "Dein Portfolio trägt das Profil eines aggressiven Wachstumsinvestors — "
            "doch die Zahlen zeigen: Dieses Risikoprofil bringt aktuell keine Mehrrendite. "
            "Das Marktrisiko wird eingegangen, ohne entsprechend entlohnt zu werden."
        ),
        "EN": (
            "Your portfolio carries the profile of an aggressive growth investor — "
            "but the numbers show: this risk profile is not generating excess returns currently. "
            "Market risk is being taken without adequate compensation."
        ),
    },
    ("aggressive_growth", "loss"): {
        "DE": (
            "Dein Portfolio ist auf Wachstum ausgerichtet — und befindet sich aktuell unter Druck. "
            "Das ist bei diesem Risikoprofil keine Überraschung, aber ein klares Signal, "
            "die Struktur kritisch zu prüfen."
        ),
        "EN": (
            "Your portfolio is growth-oriented — and currently under pressure. "
            "For this risk profile, that's not surprising, but it's a clear signal "
            "to critically review the structure."
        ),
    },

    # ── Spekulativer Opportunist ──────────────────────────────────────────────
    ("speculative", "strong_pos"): {
        "DE": (
            "Dein Portfolio hat einen stark spekulativen Charakter — und die aktuelle Marktlage "
            "spielt dir in die Hände. Solche Phasen können schnell drehen; Gewinne jetzt zu "
            "sichern ist wichtiger als weiteres Risiko aufzubauen."
        ),
        "EN": (
            "Your portfolio has a strongly speculative character — and current market conditions "
            "are working in your favour. These phases can reverse quickly; securing gains now "
            "is more important than adding further risk."
        ),
    },
    ("speculative", "pos"): {
        "DE": (
            "Das Portfolio zeigt ein spekulatives Profil — konzentriert, volatil, mit erheblichem "
            "Krypto-Anteil. Die Performance ist positiv, aber das Fundament ist fragil."
        ),
        "EN": (
            "The portfolio shows a speculative profile — concentrated, volatile, with significant "
            "crypto exposure. Performance is positive, but the foundation is fragile."
        ),
    },
    ("speculative", "flat"): {
        "DE": (
            "Dein Portfolio ist spekulativ aufgestellt, aber die Zahlen zeigen: Das Risiko lohnt "
            "sich aktuell nicht. Viel Schwankung, wenig Ertrag — das ist die kostspieligste Kombination."
        ),
        "EN": (
            "Your portfolio is speculatively positioned, but the numbers show: the risk is not paying "
            "off currently. High volatility, little return — that's the most costly combination."
        ),
    },
    ("speculative", "loss"): {
        "DE": (
            "Das Portfolio hat ein spekulatives Profil — und befindet sich aktuell im Verlust. "
            "Das ist bei dieser Struktur das wahrscheinlichste Szenario in einem schwachen "
            "Marktumfeld. Zeit für eine ehrliche Bestandsaufnahme."
        ),
        "EN": (
            "The portfolio has a speculative profile — and is currently in loss. "
            "For this structure, that's the most likely scenario in a weak market environment. "
            "Time for an honest assessment."
        ),
    },

    # ── Momentum- & Trend-Investor ───────────────────────────────────────────
    ("momentum_trend", "strong_pos"): {
        "DE": (
            "Das Portfolio hat das Profil eines Momentum-Investors — und der Momentum trägt. "
            "Die Performance wird von wenigen, starken Titeln getragen. "
            "Das funktioniert — solange der Trend intakt bleibt."
        ),
        "EN": (
            "The portfolio has the profile of a momentum investor — and the momentum is carrying it. "
            "Performance is driven by a few strong positions. "
            "This works — as long as the trend remains intact."
        ),
    },
    ("momentum_trend", "pos"): {
        "DE": (
            "Momentum-Profil: Ein oder zwei Titel tragen überproportional zur Performance bei. "
            "Das ist kein Problem, solange diese Titel intakt bleiben — "
            "aber ein Konzentrationsrisiko das man kennen sollte."
        ),
        "EN": (
            "Momentum profile: One or two positions contribute disproportionately to performance. "
            "That's fine as long as these positions remain intact — "
            "but it's a concentration risk worth knowing."
        ),
    },
    ("momentum_trend", "flat"): {
        "DE": (
            "Das Portfolio zeigt Merkmale eines Momentum-Investors — doch der Momentum ist "
            "aktuell nicht da. Titel die stark gelaufen sind, können in solchen Phasen "
            "besonders stark korrigieren."
        ),
        "EN": (
            "The portfolio shows momentum investor characteristics — but the momentum isn't "
            "there currently. Positions that have run hard can correct particularly sharply "
            "in such phases."
        ),
    },
    ("momentum_trend", "loss"): {
        "DE": (
            "Das Momentum-Portfolio verliert seinen Treiber. Wenn die Leitpositionen unter Druck "
            "kommen, gibt es wenig im Portfolio was dagegenhält. "
            "Das ist die Verwundbarkeit dieses Profils."
        ),
        "EN": (
            "The momentum portfolio is losing its driver. When the leading positions come under "
            "pressure, there is little in the portfolio to counteract it. "
            "That is the vulnerability of this profile."
        ),
    },

    # ── Ausgewogener Langfristinvestor ────────────────────────────────────────
    ("balanced", "strong_pos"): {
        "DE": (
            "Das Portfolio ist ausgewogen aufgestellt und entwickelt sich stark — "
            "das ist die beste Kombination. Solide Grundlage, gute Rendite, überschaubares Risiko."
        ),
        "EN": (
            "The portfolio is well-balanced and developing strongly — "
            "that's the best combination. Solid foundation, good return, manageable risk."
        ),
    },
    ("balanced", "pos"): {
        "DE": (
            "Das Portfolio zeigt ein ausgewogenes Profil: Breit gestreut, moderat ausgerichtet, "
            "positive Entwicklung. Eine solide Basis für langfristigen Vermögensaufbau."
        ),
        "EN": (
            "The portfolio shows a balanced profile: well diversified, moderately positioned, "
            "positive development. A solid base for long-term wealth building."
        ),
    },
    ("balanced", "flat"): {
        "DE": (
            "Das Portfolio ist ausgewogen aufgestellt — aber die Performance bleibt hinter dem "
            "Anspruch zurück. Bei einem ausgewogenen Profil sollte der Markt mindestens "
            "mitgemacht werden."
        ),
        "EN": (
            "The portfolio is well-balanced — but performance is falling short of expectations. "
            "With a balanced profile, the market should at least be matched."
        ),
    },
    ("balanced", "loss"): {
        "DE": (
            "Das Portfolio ist ausgewogen — und trotzdem im Minus. Das zeigt, dass aktuell "
            "breite Marktbewegungen das Portfolio erfassen. Eine Überprüfung der Grundausrichtung "
            "ist sinnvoll."
        ),
        "EN": (
            "The portfolio is balanced — and still in the red. That shows broad market movements "
            "are currently affecting the portfolio. A review of the fundamental positioning "
            "is worthwhile."
        ),
    },

    # ── Defensiver Stabilitätsinvestor ────────────────────────────────────────
    ("defensive", "strong_pos"): {
        "DE": (
            "Das Portfolio hat ein defensives Profil — und zeigt eine für diesen Typ "
            "bemerkenswerte Entwicklung. Defensive Portfolios performen in turbulenten Märkten "
            "besonders stark; dieser Trend bestätigt sich hier."
        ),
        "EN": (
            "The portfolio has a defensive profile — and shows remarkable development "
            "for this type. Defensive portfolios perform particularly well in turbulent markets; "
            "that trend is confirmed here."
        ),
    },
    ("defensive", "pos"): {
        "DE": (
            "Das Portfolio ist defensiv ausgerichtet und entwickelt sich solide. "
            "Das ist exakt was dieses Profil versprechen soll: "
            "Verlässliche Entwicklung statt Achterbahn."        ),
        "EN": (
            "The portfolio is defensively positioned and developing solidly. "
            "That is exactly what this profile should deliver: "
            "Reliable development rather than a rollercoaster."        ),
    },
    ("defensive", "flat"): {
        "DE": (
            "Das Portfolio ist defensiv aufgestellt — und die Performance bleibt derzeit moderat. "
            "Bei einem defensiven Profil ist das akzeptabel: "
            "Der Schutz in Abschwüngen ist die eigentliche Stärke."        ),
        "EN": (
            "The portfolio is defensively positioned — and performance remains moderate currently. "
            "For a defensive profile, that's acceptable: "
            "Protection during downturns is the real strength."        ),
    },
    ("defensive", "loss"): {
        "DE": (
            "Das defensiv aufgestellte Portfolio verliert — das ist ein ungewöhnliches Signal. "
            "Entweder erfasst ein breiter Marktabschwung alles, oder einzelne Positionen "
            "haben spezifische Probleme. Das verdient genauere Betrachtung."
        ),
        "EN": (
            "The defensively positioned portfolio is losing — that's an unusual signal. "
            "Either a broad market downturn is affecting everything, or individual positions "
            "have specific problems. That deserves closer attention."
        ),
    },

    # ── Diversifizierter Allrounder ───────────────────────────────────────────
    ("diversified", "strong_pos"): {
        "DE": (
            "Das Portfolio ist breit diversifiziert und entwickelt sich stark — "
            "das zeigt, dass breite Streuung nicht auf Kosten der Rendite gehen muss."
        ),
        "EN": (
            "The portfolio is broadly diversified and developing strongly — "
            "this shows that broad diversification doesn't have to come at the cost of returns."
        ),
    },
    ("diversified", "pos"): {
        "DE": (
            "Das Portfolio ist gut diversifiziert und entwickelt sich positiv. "
            "Breite Streuung bedeutet selten spektakuläre, aber dafür verlässliche Rendite."
        ),
        "EN": (
            "The portfolio is well diversified and developing positively. "
            "Broad diversification rarely means spectacular, but delivers reliable returns."
        ),
    },
    ("diversified", "flat"): {
        "DE": (
            "Das Portfolio ist gut diversifiziert — aber die breite Streuung schützt aktuell "
            "nicht vor Stagnation. In einem seitwärts laufenden Markt ist das normal."
        ),
        "EN": (
            "The portfolio is well diversified — but broad diversification is not protecting "
            "against stagnation currently. In a sideways market, that's normal."
        ),
    },
    ("diversified", "loss"): {
        "DE": (
            "Das Portfolio ist breit gestreut — und trotzdem im Verlust. "
            "Das deutet auf einen breiten Marktabschwung, keine strukturelle Schwäche. "
            "Diversifikation schützt vor Einzeltitelrisiken, nicht vor Marktbewegungen."
        ),
        "EN": (
            "The portfolio is broadly diversified — and still at a loss. "
            "That points to a broad market downturn, not a structural weakness. "
            "Diversification protects against single-stock risk, not market movements."
        ),
    },

    # ── Dividenden- & Einkommensinvestor ─────────────────────────────────────
    ("dividends_income", "pos"): {
        "DE": (
            "Das Portfolio trägt die Handschrift eines auf Einkommen ausgerichteten Investors — "
            "stabil, defensiv, auf regelmässige Ausschüttungen fokussiert. "
            "Eine bewährte Strategie für kapitalerhaltungsorientierten Vermögensaufbau."
        ),
        "EN": (
            "The portfolio bears the hallmark of an income-oriented investor — "
            "stable, defensive, focused on regular distributions. "
            "A proven strategy for capital-preservation-oriented wealth building."
        ),
    },
    ("dividends_income", "flat"): {
        "DE": (
            "Einkommens-orientiertes Portfolio: Der Kurswert stagniert, aber das Gesamtbild "
            "inklusive Dividenden dürfte besser aussehen. "
            "Bei diesem Profil ist der Kursgewinn nicht das einzige Mass."
        ),
        "EN": (
            "Income-oriented portfolio: Price performance is flat, but the full picture "
            "including dividends is likely better. "
            "For this profile, price gain is not the only measure."
        ),
    },
    ("dividends_income", "loss"): {
        "DE": (
            "Das Einkommens-Portfolio ist unter Druck. Steigende Zinsen oder Sektorrotationen "
            "treffen defensive Dividendentitel typischerweise am stärksten. "
            "Die Ertragsseite (Dividenden) sollte die Verluste zumindest teilweise puffern."
        ),
        "EN": (
            "The income portfolio is under pressure. Rising interest rates or sector rotations "
            "typically hit defensive dividend stocks hardest. "
            "The income side (dividends) should at least partially buffer the losses."
        ),
    },

    # ── Solider Buy-and-Hold-Investor ─────────────────────────────────────────
    ("buy_and_hold", "strong_pos"): {
        "DE": (
            "Das Portfolio hat das Profil eines überzeugten Buy-and-Hold-Investors — "
            "und der Zinseszins arbeitet. Wer gute Positionen über Jahre hält, "
            "lässt die Zeit für sich arbeiten. Die starke Entwicklung bestätigt diesen Ansatz."
        ),
        "EN": (
            "The portfolio has the profile of a conviction buy-and-hold investor — "
            "and compounding is working. Holding quality positions over years "
            "lets time do the heavy lifting. The strong development confirms this approach."
        ),
    },
    ("buy_and_hold", "pos"): {
        "DE": (
            "Das Portfolio ist auf langfristigen Vermögensaufbau ausgerichtet. "
            "Kein Timing, kein häufiges Umschichten — stattdessen Geduld "
            "und Vertrauen in die eigene Titelauswahl. Die positive Entwicklung gibt diesem Weg recht."
        ),
        "EN": (
            "The portfolio is positioned for long-term wealth building. "
            "No timing, no frequent rebalancing — instead patience "
            "and trust in the chosen positions. The positive development validates this path."
        ),
    },
    ("buy_and_hold", "flat"): {
        "DE": (
            "Das Buy-and-Hold-Portfolio stagniert kurzfristig — "
            "das ist bei dieser Strategie normal und kein Alarmsignal. "
            "Langfristig belohnt der Markt Geduld; kurzfristige Seitwärtsphasen gehören dazu."
        ),
        "EN": (
            "The buy-and-hold portfolio is stagnating short-term — "
            "that's normal for this strategy and no cause for alarm. "
            "Long-term, the market rewards patience; short-term sideways phases are part of the journey."
        ),
    },
    ("buy_and_hold", "loss"): {
        "DE": (
            "Das Portfolio ist auf langfristigen Aufbau ausgerichtet — und befindet sich aktuell im Minus. "
            "Verluste sind bei einer Buy-and-Hold-Strategie keine Seltenheit, "
            "aber ein Moment um zu prüfen, ob die ursprünglichen Investitionsthesen noch stimmen."
        ),
        "EN": (
            "The portfolio is positioned for long-term building — and is currently in the red. "
            "Losses are not uncommon in a buy-and-hold strategy, "
            "but this is a moment to check whether the original investment theses still hold."
        ),
    },

    # ── Hochrisiko-Investor ───────────────────────────────────────────────────
    ("high_risk", "strong_pos"): {
        "DE": (
            "Das Portfolio trägt ein ausgeprägtes Hochrisikoprofil — und befindet sich aktuell "
            "in einer starken Phase. Solche Momente sind die Belohnung für diesen Ansatz. "
            "Gleichzeitig ist jetzt der richtige Zeitpunkt, "
            "einen Teil der Gewinne abzusichern, bevor die Volatilität dreht."
        ),
        "EN": (
            "The portfolio carries a pronounced high-risk profile — and is currently in a strong phase. "
            "Such moments are the reward for this approach. "
            "At the same time, now is the right moment to secure part of the gains "
            "before volatility turns."
        ),
    },
    ("high_risk", "pos"): {
        "DE": (
            "Hohes Risiko, positive Entwicklung — die Rechnung geht aktuell auf. "
            "Aber das Fundament ist fragil: hohe Schwankungen, enge Positionen, wenig Puffer. "
            "Die nächste Korrekturphase wird das Portfolio stärker treffen als ein ausgewogenes."
        ),
        "EN": (
            "High risk, positive development — the calculation is working out currently. "
            "But the foundation is fragile: high volatility, concentrated positions, little buffer. "
            "The next correction phase will hit this portfolio harder than a balanced one."
        ),
    },
    ("high_risk", "flat"): {
        "DE": (
            "Das Hochrisikoprofil zeigt keine Mehrrendite — das ist die kostspieligste Konstellation. "
            "Viel Risiko wird eingegangen, aber die Rendite entlohnt es nicht. "
            "Eine grundlegende Überprüfung der Strategie ist angebracht."
        ),
        "EN": (
            "The high-risk profile is generating no excess return — that's the most costly constellation. "
            "Much risk is being taken, but the return doesn't compensate for it. "
            "A fundamental review of the strategy is warranted."
        ),
    },
    ("high_risk", "loss"): {
        "DE": (
            "Hohes Risiko, aktuell im Verlust — das ist bei diesem Profil das wahrscheinlichste "
            "Szenario in einem schwachen Marktumfeld. "
            "Das ist kein Zeichen des Scheiterns, sondern Konsequenz des Risikoprofils. "
            "Wer hier bleibt, braucht einen klaren Plan und starke Nerven."
        ),
        "EN": (
            "High risk, currently at a loss — for this profile, that's the most likely "
            "scenario in a weak market. "
            "That's not a sign of failure, but a consequence of the risk profile. "
            "Staying the course here requires a clear plan and strong nerves."
        ),
    },

    # ── Vorsichtiger Altersvorsorge-Aufbauer ──────────────────────────────────
    ("retirement", "strong_pos"): {
        "DE": (
            "Das Portfolio ist konservativ ausgerichtet — und entwickelt sich erfreulich stark. "
            "Das zeigt, dass Kapitalschutz und solide Rendite kein Widerspruch sind. "
            "Eine Ausrichtung, die langfristig funktioniert."
        ),
        "EN": (
            "The portfolio is conservatively positioned — and developing impressively strongly. "
            "That shows that capital protection and solid return are not contradictory. "
            "An orientation that works long-term."
        ),
    },
    ("retirement", "pos"): {
        "DE": (
            "Das Portfolio zeigt das Profil eines vorsichtigen Altersvorsorge-Aufbauers: "
            "Defensiv, stabil, auf Kapitalerhalt ausgerichtet. "            "Die positive Entwicklung ist keine Überraschung — "
            "dieser Ansatz liefert verlässlich, wenn auch ohne Spektakel."
        ),
        "EN": (
            "The portfolio shows the profile of a cautious retirement builder: "
            "Defensive, stable, focused on capital preservation. "            "The positive development is no surprise — "
            "this approach delivers reliably, if without spectacle."
        ),
    },
    ("retirement", "flat"): {
        "DE": (
            "Das konservative Portfolio stagniert kurzfristig. "
            "Bei einem Altersvorsorge-Profil steht der Kapitalerhalt an erster Stelle — "
            "und der ist gewährleistet. Wer Wachstum sucht, braucht einen anderen Ansatz."
        ),
        "EN": (
            "The conservative portfolio is stagnating short-term. "
            "For a retirement profile, capital preservation comes first — "
            "and that is ensured. Those seeking growth need a different approach."
        ),
    },
    ("retirement", "loss"): {
        "DE": (
            "Das defensiv ausgerichtete Altersvorsorge-Portfolio ist im Verlust — "
            "das verdient Aufmerksamkeit. Bei einem Profil das auf Kapitalschutz zielt, "
            "ist das ein Signal, die Zusammensetzung zu prüfen. "
            "Breit aufgestellte defensive Positionen sollten gerade in solchen Phasen standhalten."
        ),
        "EN": (
            "The defensively positioned retirement portfolio is at a loss — "
            "that deserves attention. For a profile aimed at capital protection, "
            "this is a signal to review the composition. "
            "Broadly positioned defensive holdings should hold up precisely in such phases."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# MODUL 2 — Rendite-Risiko-Verhältnis (Beta × Sharpe × Alpha)
# beta_class:  low | medium | high
# sharpe_class: good | ok | poor
# alpha_class:  positive | neutral | negative
# ══════════════════════════════════════════════════════════════════════════════

M2 = {

    ("low", "good", "positive"): {
        "DE": (
            "Das Risiko-Rendite-Verhältnis ist ausgezeichnet: "
            "Geringe Marktempfindlichkeit, hohe Effizienz, und eine Titelauswahl die den Markt schlägt. "            "Diese Kombination ist selten — und spricht für echte Qualität im Portfolio."
        ),
        "EN": (
            "The risk-return ratio is excellent: "
            "Low market sensitivity, high efficiency, and stock selection that beats the market. "            "This combination is rare — and speaks to genuine quality in the portfolio."
        ),
    },
    ("low", "good", "neutral"): {
        "DE": (
            "Das Risiko-Rendite-Verhältnis ist gut: "
            "Das Portfolio schwankt wenig und die Rendite wird effizient erzielt — "            "auch wenn kein Mehrwert gegenüber dem Markt entsteht. Solide Basis."
        ),
        "EN": (
            "The risk-return ratio is good: "
            "The portfolio fluctuates little and returns are generated efficiently — "            "even without generating excess returns over the market. Solid base."
        ),
    },
    ("low", "good", "negative"): {
        "DE": (
            "Gute Effizienz, aber die Titelauswahl kostet Rendite: "
            "Das Portfolio schwankt wenig, schlägt den Markt aber nicht. "            "Passiv investierte Indexprodukte hätten denselben Ertrag mit weniger Aufwand gebracht."
        ),
        "EN": (
            "Good efficiency, but stock selection is costing returns: "
            "The portfolio fluctuates little, but doesn't beat the market. "            "Passively invested index products would have delivered the same return with less effort."
        ),
    },
    ("low", "ok", "positive"): {
        "DE": (
            "Positiv: Das Portfolio schlägt den Markt mit geringem Risiko. "
            "Die Effizienz könnte noch besser sein, aber Mehrrendite bei tiefem Beta "
            "ist ein starkes Signal — die Titelauswahl hat Substanz."
        ),
        "EN": (
            "Positive: the portfolio beats the market with low risk. "
            "Efficiency could be better, but excess return with low beta "
            "is a strong signal — the stock selection has substance."
        ),
    },
    ("low", "poor", "negative"): {
        "DE": (
            "Defensives Portfolio, aber wenig effizient: "
            "Trotz geringer Marktsensitivität ist die Rendite zu niedrig für das eingegangene Risiko. "            "Der Wechsel zu einem Indexprodukt wäre ernsthaft zu prüfen."
        ),
        "EN": (
            "Defensive portfolio, but inefficient: "
            "Despite low market sensitivity, the return is too low for the risk taken. "            "Switching to an index product would be seriously worth considering."
        ),
    },
    ("medium", "good", "positive"): {
        "DE": (
            "Das Risiko-Rendite-Verhältnis ist stark: "
            "Marktkonformes Risiko, hohe Effizienz, Mehrrendite gegenüber dem Markt. "            "Das deutet auf echte Qualität in der Titelauswahl — kein Glück, sondern Können."
        ),
        "EN": (
            "The risk-return ratio is strong: "
            "Market-level risk, high efficiency, excess return over the market. "            "That points to genuine quality in stock selection — not luck, but skill."
        ),
    },
    ("medium", "good", "neutral"): {
        "DE": (
            "Solide: Marktkonformes Risiko, gute Effizienz, Performance im Marktrahmen. "
            "Das Portfolio tut was es soll — kein Mehrwert, aber auch kein Mehrrisiko. "
            "Ein klassisches, gut geführtes Marktportfolio."
        ),
        "EN": (
            "Solid: market-level risk, good efficiency, performance within market range. "
            "The portfolio does what it should — no excess value, but no excess risk either. "
            "A classic, well-managed market portfolio."
        ),
    },
    ("medium", "good", "negative"): {
        "DE": (
            "Solide Effizienz, aber keine Überperformance: "
            "Das Portfolio bewegt sich effizient mit dem Markt, schlägt ihn aber nicht. "            "Für aktive Investoren ein Denkansatz — passives Investieren hätte denselben Ertrag gebracht."
        ),
        "EN": (
            "Solid efficiency, but no outperformance: "
            "The portfolio moves efficiently with the market but doesn't beat it. "            "Food for thought for active investors — passive investing would have delivered the same return."
        ),
    },
    ("medium", "ok", "neutral"): {
        "DE": (
            "Das Risiko-Rendite-Verhältnis ist solide aber unspektakulär: "
            "Marktkonformes Risiko, angemessene Effizienz, keine Über- oder Unterperformance. "            "Ein typisches Marktportfolio-Profil ohne besondere Stärken oder Schwächen."
        ),
        "EN": (
            "The risk-return ratio is solid but unspectacular: "
            "Market-level risk, adequate efficiency, no over- or underperformance. "            "A typical market portfolio profile without particular strengths or weaknesses."
        ),
    },
    ("medium", "poor", "negative"): {
        "DE": (
            "Das Risiko-Rendite-Verhältnis ist unbefriedigend: "
            "Mittleres Marktrisiko, aber die Rendite entschädigt dafür nicht. "            "Das Portfolio trägt Marktrisiko ohne Marktrendite. Handlungsbedarf."
        ),
        "EN": (
            "The risk-return ratio is unsatisfactory: "
            "Medium market risk, but the return doesn't compensate for it. "            "The portfolio carries market risk without market return. Action needed."
        ),
    },
    ("high", "good", "positive"): {
        "DE": (
            "Das Portfolio trägt hohes Marktrisiko — und wird dafür gut entlohnt. "
            "Alpha und Effizienz zeigen, dass die Titelauswahl funktioniert. "
            "Die entscheidende Frage: Wie verhält sich das Portfolio wenn der Wind dreht?"
        ),
        "EN": (
            "The portfolio carries high market risk — and is well compensated for it. "
            "Alpha and efficiency show that stock selection is working. "
            "The critical question: how will it behave when the wind turns?"
        ),
    },
    ("high", "good", "neutral"): {
        "DE": (
            "Hohes Marktrisiko, gute Effizienz — aber keine Mehrrendite. "
            "Das Risiko wird akzeptabel verwaltet, aber der Mehraufwand gegenüber "
            "einem einfachen Index-Invest wird nicht belohnt."
        ),
        "EN": (
            "High market risk, good efficiency — but no excess return. "
            "The risk is acceptably managed, but the extra effort compared to "
            "a simple index investment is not being rewarded."
        ),
    },
    ("high", "ok", "neutral"): {
        "DE": (
            "Hohes Marktrisiko, mittelmässige Effizienz: "
            "Das Portfolio schwankt stark mit dem Markt, schlägt ihn aber nicht. "            "Das Risiko ist höher als der Ertrag rechtfertigt."
        ),
        "EN": (
            "High market risk, mediocre efficiency: "
            "The portfolio swings strongly with the market but doesn't beat it. "            "The risk is higher than the return justifies."
        ),
    },
    ("high", "poor", "negative"): {
        "DE": (
            "Das ist die ungünstigste Kombination: "
            "Hohes Marktrisiko, schlechte Effizienz, keine Mehrrendite. "            "Das Portfolio trägt das volle Marktrisiko — und liefert nicht. "
            "Diese Struktur braucht eine grundlegende Überprüfung."
        ),
        "EN": (
            "This is the most unfavourable combination: "
            "High market risk, poor efficiency, no excess return. "            "The portfolio bears full market risk — and doesn't deliver. "
            "This structure needs a fundamental review."
        ),
    },
    ("high", "poor", "positive"): {
        "DE": (
            "Interessante Konstellation: Hohes Marktrisiko und eine Titelauswahl die den Markt schlägt — "
            "aber die Effizienz bleibt schlecht. Der Mehrwert wird durch übermässige Schwankungen aufgefressen. "
            "Weniger Risiko würde mehr aus dem vorhandenen Alpha machen."
        ),
        "EN": (
            "Interesting constellation: high market risk and stock selection that beats the market — "
            "but efficiency remains poor. The excess value is eaten up by excessive volatility. "
            "Less risk would make more of the existing alpha."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# MODUL 3 — Was ist wirklich passiert (Drawdown × Beta × RSI)
# dd_class:   low (<-15%) | medium (-15% bis -30%) | high (>-30%)
# beta_class: low | medium | high
# rsi_class:  overbought (>65) | neutral | oversold (<35)
# ══════════════════════════════════════════════════════════════════════════════

M3_drawdown = {

    ("low", "low"): {
        "DE": (
            "Das Bild ist konsistent: Geringes Marktrisiko, geringe Verlustphasen. "
            "Das Portfolio hat bewiesen was es verspricht — auch in schwierigen Phasen "
            "blieb die Kontrolle. Defensiv und belastbar."
        ),
        "EN": (
            "The picture is consistent: low market risk, low loss phases. "
            "The portfolio has proven what it promises — control was maintained "
            "even in difficult phases. Defensive and resilient."
        ),
    },
    ("high", "low"): {
        "DE": (
            "Achtung: Das geringe Beta täuscht. Trotz geringer Marktempfindlichkeit "
            "hat das Portfolio erhebliche Verlustphasen erlebt. "
            "Das deutet auf idiosynkratisches Risiko — einzelne Titel haben stark korrigiert, "
            "unabhängig vom Markt. Das ist schwerer zu diversifizieren als Marktrisiko."
        ),
        "EN": (
            "Warning: the low beta is misleading. Despite low market sensitivity, "
            "the portfolio has experienced significant loss phases. "
            "This points to idiosyncratic risk — individual positions corrected sharply, "
            "independently of the market. That is harder to diversify away than market risk."
        ),
    },
    ("low", "medium"): {
        "DE": (
            "Verlustphasen und Marktrisiko passen zusammen: "
            "Das Portfolio hat sich in Abschwüngen besser gehalten als der Markt. "            "Ein gutes Zeichen für die Qualität der Titelauswahl."
        ),
        "EN": (
            "Loss phases and market risk are aligned: "
            "The portfolio has held up better than the market during downturns. "            "A good sign for the quality of stock selection."
        ),
    },
    ("medium", "medium"): {
        "DE": (
            "Verlustphasen und Marktrisiko sind konsistent: Was das Beta verspricht, "
            "hat das Portfolio auch erlebt. Keine bösen Überraschungen, "
            "aber auch keine besondere Robustheit — ein ehrliches Profil."
        ),
        "EN": (
            "Loss phases and market risk are consistent: what the beta promises, "
            "the portfolio has experienced. No nasty surprises, "
            "but no particular resilience either — an honest profile."
        ),
    },
    ("high", "medium"): {
        "DE": (
            "Das Portfolio hat tiefere Verlustphasen erlebt als das Beta erwarten liesse. "
            "Das deutet auf Perioden erhöhter Korrelation aller Positionen — "
            "in Stressmomenten fallen oft auch defensivere Titel gemeinsam. "
            "Oder einzelne Positionen haben spezifische Probleme ausserhalb des Marktmusters gezeigt."
        ),
        "EN": (
            "The portfolio has experienced deeper loss phases than the beta would suggest. "
            "This points to periods of elevated correlation across all positions — "
            "in stress moments, even more defensive stocks often fall together. "
            "Or individual positions showed specific problems outside the normal market pattern."
        ),
    },
    ("low", "high"): {
        "DE": (
            "Bemerkenswert: Trotz hoher Marktsensitivität blieben die Verlustphasen moderat. "
            "Das kann auf gutes Timing, auf defensive Einzeltitel oder auf vorteilhafte Marktphasen "
            "zurückzuführen sein. Nicht zwingend Robustheit — aber bisher ein gutes Ergebnis."
        ),
        "EN": (
            "Noteworthy: despite high market sensitivity, loss phases remained moderate. "
            "This may be due to good timing, defensive individual stocks, or favourable market conditions. "
            "Not necessarily resilience — but a good result so far."
        ),
    },
    ("medium", "high"): {
        "DE": (
            "Hohes Beta, moderate Verluste — das ist besser als erwartet. "
            "Entweder hat die Titelauswahl geholfen, oder der Markt war bisher attraktiv bewertet. "
            "In einem Abschwung würde die hohe Marktsensitivität stärker spürbar werden."
        ),
        "EN": (
            "High beta, moderate losses — that's better than expected. "
            "Either stock selection has helped, or the market has been favourable so far. "
            "In a downturn, the high market sensitivity would become more noticeable."
        ),
    },
    ("high", "high"): {
        "DE": (
            "Hohes Beta, hohe Verluste — das ist konsequent. "
            "Wer dieses Risikoprofil wählt, muss mit solchen Verlustphasen leben können. "
            "Die Frage ist: war das eine bewusste Entscheidung — "
            "und gibt es ausreichend Stop-Loss-Schutz für die nächste Korrekturrunde?"
        ),
        "EN": (
            "High beta, high losses — that's consistent. "
            "Whoever chooses this risk profile must be able to live with such loss phases. "
            "The question is: was this a conscious choice — "
            "and is there sufficient stop-loss protection for the next correction round?"
        ),
    },
}

M3_rsi = {
    "overbought": {
        "DE": (
            "Technisch sind viele Positionen überkauft. "
            "Das bedeutet nicht zwingend einen Rückgang — aber die kurzfristige "
            "Aufwärtsdynamik ist ausgereizt. Neue Einstiege jetzt wären teuer bezahlt."
        ),
        "EN": (
            "Technically, many positions are overbought. "
            "That doesn't necessarily mean a decline — but short-term upward momentum "
            "is stretched. New entries now would be bought at a high price."
        ),
    },
    "oversold": {
        "DE": (
            "Technisch sind viele Positionen überverkauft. "
            "Das kann ein Zeichen für temporären Ausverkaufsdruck sein — "
            "oder für fundamentale Probleme in den Titeln. "
            "Historisch folgen auf überverkaufte Phasen oft Erholungen."
        ),
        "EN": (
            "Technically, many positions are oversold. "
            "This can be a sign of temporary selling pressure — "
            "or of fundamental problems in the underlying stocks. "
            "Historically, recovery phases often follow oversold conditions."
        ),
    },
    "neutral": {
        "DE": (
            "Die technischen Indikatoren zeigen ein neutrales Bild — "
            "keine extremen Über- oder Unterbewertungssignale. "
            "Das Portfolio ist technisch in einer stabilen Zone."
        ),
        "EN": (
            "Technical indicators show a neutral picture — "
            "no extreme over- or undervaluation signals. "
            "The portfolio is technically in a stable zone."
        ),
    },
}

M3_dd_perf = {
    ("low", "strong_pos"): {
        "DE": (
            "Das Beste aus beiden Welten: Starke Performance und gleichzeitig begrenzte Verlustphasen. "
            "Das Portfolio hat nicht nur gewonnen, sondern auch nach unten gut geschützt. "
            "Das ist ein starkes Qualitätsmerkmal."
        ),
        "EN": (
            "The best of both worlds: strong performance and limited loss phases. "
            "The portfolio has not only gained but also protected well on the downside. "
            "That is a strong quality indicator."
        ),
    },
    ("high", "strong_pos"): {
        "DE": (
            "Das Portfolio hat tiefe Verlustphasen erlebt — und sich stark erholt. "
            "Das zeigt Resilienz, aber auch Volatilität. "
            "Wer solche Schwankungen emotional durchhalten kann, profitiert von dieser Dynamik. "
            "Wer es nicht kann, sollte das Risikoprofil überdenken."
        ),
        "EN": (
            "The portfolio has experienced deep loss phases — and recovered strongly. "
            "This shows resilience, but also volatility. "
            "Those who can emotionally handle such swings benefit from this dynamic. "
            "Those who can't should reconsider the risk profile."
        ),
    },
    ("high", "loss"): {
        "DE": (
            "Tiefe Verlustphasen, aktuell noch im Minus — das Portfolio kämpft. "
            "Eine kritische Analyse ist jetzt wichtig: "
            "Was hat die Verluste verursacht, und hat sich die ursprüngliche Investitionsthese geändert?"        ),
        "EN": (
            "Deep loss phases, currently still in the red — the portfolio is struggling. "
            "A critical analysis is important now: "
            "What caused the losses, and has the original investment thesis changed?"        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# MODUL 4 — Struktur & Marktkontext (Sektor × ECY × Monte Carlo)
# ecy_class:    cheap (ECY>3%) | fair (1-3%) | expensive (<1%)
# mc_class:     high (>70% positiv) | medium (50-70%) | low (<50%)
# sector_type:  growth_heavy | defensive_heavy | tech_heavy | balanced
# ══════════════════════════════════════════════════════════════════════════════

M4_ecy_mc = {

    ("cheap", "high"): {
        "DE": (
            "Der Markt ist historisch attraktiv bewertet — das erhöht statistisch die "
            "Renditeerwartung für die nächsten Jahre. Monte Carlo-Simulationen bestätigen "
            "in der grossen Mehrheit der Szenarien positive Entwicklungen. "
            "Das ist eine gute Ausgangslage."
        ),
        "EN": (
            "The market is historically attractively valued — this statistically increases "
            "return expectations for the coming years. Monte Carlo simulations confirm "
            "positive developments in the vast majority of scenarios. "
            "That is a good starting position."
        ),
    },
    ("cheap", "medium"): {
        "DE": (
            "Günstige Marktbewertung — aber Monte Carlo zeigt gemischte Szenarien. "
            "Das attraktive Marktumfeld allein reicht nicht: "
            "Die Portfoliostruktur bestimmt mit, wie stark das Portfolio davon profitieren kann."        ),
        "EN": (
            "Attractive market valuation — but Monte Carlo shows mixed scenarios. "
            "A favourable market environment alone is not enough: "
            "The portfolio structure also determines how strongly the portfolio can benefit from it."        ),
    },
    ("fair", "high"): {
        "DE": (
            "Faire Marktbewertung, überwiegend positive Simulationsszenarien. "
            "Das ist eine solide Ausgangslage — keine teuren Bewertungen, "
            "die Risiken erhöhen, und die Simulationen zeigen mehr positive als negative Pfade."
        ),
        "EN": (
            "Fair market valuation, predominantly positive simulation scenarios. "
            "That is a solid starting position — no expensive valuations "
            "that increase risks, and simulations show more positive than negative paths."
        ),
    },
    ("fair", "medium"): {
        "DE": (
            "Faires Marktumfeld, gemischte Szenarien. "
            "Weder Rückenwind noch Gegenwind vom Markt — "
            "die Performance wird in erster Linie von der Portfoliostruktur abhängen."
        ),
        "EN": (
            "Fair market environment, mixed scenarios. "
            "Neither tailwind nor headwind from the market — "
            "performance will depend primarily on the portfolio structure."
        ),
    },
    ("fair", "low"): {
        "DE": (
            "Trotz fairer Marktbewertung zeigen Simulationen viele negative Szenarien. "
            "Das deutet auf portfoliospezifische Risiken — die Marktbewertung ist kein Problem, "
            "aber die aktuelle Portfoliostruktur erhöht die Anfälligkeit."
        ),
        "EN": (
            "Despite fair market valuation, simulations show many negative scenarios. "
            "This points to portfolio-specific risks — market valuation is not the problem, "
            "but the current portfolio structure increases vulnerability."
        ),
    },
    ("expensive", "high"): {
        "DE": (
            "Der Markt ist historisch hoch bewertet — "
            "Monte Carlo zeigt trotzdem überwiegend positive Szenarien. "
            "Das ist möglich in Bullmärkten, aber die Sicherheitsmarge ist gering. "
            "Höhere Bewertungen bedeuten: Wenig Puffer bei Enttäuschungen."
        ),
        "EN": (
            "The market is historically highly valued — "
            "yet Monte Carlo still shows predominantly positive scenarios. "
            "That's possible in bull markets, but the margin of safety is thin. "
            "Higher valuations mean: little buffer for disappointments."
        ),
    },
    ("expensive", "medium"): {
        "DE": (
            "Teures Marktumfeld, gemischte Simulationsszenarien — "
            "das ist eine Konstellation die Vorsicht erfordert. "
            "Hohe Bewertungen erhöhen das Rückschlagpotential; "
            "gemischte Szenarien zeigen, dass die Unsicherheit gross ist."
        ),
        "EN": (
            "Expensive market environment, mixed simulation scenarios — "
            "that is a constellation that requires caution. "
            "High valuations increase downside potential; "
            "mixed scenarios show that uncertainty is high."
        ),
    },
    ("expensive", "low"): {
        "DE": (
            "Ungünstige Kombination: Historisch teure Marktbewertung und Monte Carlo zeigt "
            "mehr negative als positive Szenarien. Das bedeutet nicht zwingend Verluste — "
            "aber die statistische Erwartungshaltung sollte realistisch sein. "
            "Jetzt ist nicht der Zeitpunkt für erhöhtes Risiko."
        ),
        "EN": (
            "Unfavourable combination: historically expensive market valuation and Monte Carlo "
            "shows more negative than positive scenarios. That doesn't necessarily mean losses — "
            "but statistical expectations should be realistic. "
            "Now is not the time for elevated risk."
        ),
    },
}

M4_sector_ecy = {

    ("tech_heavy", "expensive"): {
        "DE": (
            "Tech-Konzentration in einem historisch teuren Markt: "
            "Diese Kombination war historisch anfällig für scharfe Korrekturen. "            "Wachstumswerte verlieren bei steigenden Zinsen oder sinkenden Gewinnerwartungen "
            "überproportional — und der Spielraum ist aktuell gering."
        ),
        "EN": (
            "Tech concentration in a historically expensive market: "
            "This combination has historically been prone to sharp corrections. "            "Growth stocks lose disproportionately when interest rates rise or earnings expectations fall — "
            "and the current margin is thin."
        ),
    },
    ("tech_heavy", "cheap"): {
        "DE": (
            "Tech-Konzentration in einem attraktiv bewerteten Marktumfeld: "
            "Das ist eine bessere Ausgangslage als in teuren Märkten. "            "Attraktive Bewertungen bieten mehr Puffer — "
            "aber die Sektorkonzentration bleibt das Hauptrisiko."
        ),
        "EN": (
            "Tech concentration in an attractively valued market environment: "
            "That is a more favourable starting position than in expensive markets. "            "Attractive valuations provide more buffer — "
            "but sector concentration remains the main risk."
        ),
    },
    ("defensive_heavy", "expensive"): {
        "DE": (
            "Defensive Ausrichtung in einem teuren Markt: Eine bewusst konservative Positionierung. "
            "Defensive Sektoren bieten in Korrekturen Schutz — "
            "und bei hohen Bewertungen ist das eine vernünftige Überlegung. "
            "Das Upside-Potential ist dafür begrenzt."
        ),
        "EN": (
            "Defensive positioning in an expensive market: a consciously conservative stance. "
            "Defensive sectors offer protection during corrections — "
            "and at high valuations, that's a reasonable consideration. "
            "The upside potential is limited in return."
        ),
    },
    ("growth_heavy", "expensive"): {
        "DE": (
            "Wachstumsorientiertes Portfolio in einem teuren Markt: "
            "Das erhöht das Rückschlagpotential. "            "Wachstumswerte sind bei hohen Bewertungen stärker zinssensitiv — "
            "und haben in Korrekturen typischerweise mehr zu verlieren."
        ),
        "EN": (
            "Growth-oriented portfolio in an expensive market: "
            "This increases downside potential. "            "Growth stocks are more interest-rate sensitive at high valuations — "
            "and typically have more to lose in corrections."
        ),
    },
    ("balanced", "any"): {
        "DE": (
            "Die ausgewogene Sektorverteilung ist unabhängig vom Marktumfeld eine Stärke: "
            "Keine extreme Wette auf eine Richtung, "            "und damit weniger Anfälligkeit für sektorale Rotationen."
        ),
        "EN": (
            "The balanced sector distribution is a strength regardless of the market environment: "
            "No extreme bet in one direction, "            "and therefore less vulnerability to sector rotations."
        ),
    },
}

M4_mc_sl = {
    ("high", "good"): {
        "DE": (
            "Positiver Ausblick: Simulationen zeigen überwiegend gute Szenarien — "
            "und das Portfolio ist durch Stop-Loss-Orders gut abgesichert. "
            "Das ist eine solide Kombination: Chancen nutzen, Verluste begrenzen."
        ),
        "EN": (
            "Positive outlook: simulations show predominantly good scenarios — "
            "and the portfolio is well protected by stop-loss orders. "
            "That is a solid combination: capturing opportunities, limiting losses."
        ),
    },
    ("low", "poor"): {
        "DE": (
            "Kritisch: Simulationen zeigen viele negative Szenarien — "
            "und das Portfolio ist kaum durch Stop-Loss-Orders geschützt. "
            "Das ist eine Konstellation mit erhöhtem Verlustpotential ohne Sicherheitsnetz."
        ),
        "EN": (
            "Critical: simulations show many negative scenarios — "
            "and the portfolio is barely protected by stop-loss orders. "
            "This is a constellation with elevated loss potential and no safety net."
        ),
    },
    ("high", "poor"): {
        "DE": (
            "Positive Simulationsszenarien — aber ohne Stop-Loss-Schutz. "
            "Das ist ein unnötiges Risiko: Die guten Aussichten könnten durch einen "
            "unerwarteten Schock stark in Mitleidenschaft gezogen werden, "
            "ohne Absicherung nach unten."
        ),
        "EN": (
            "Positive simulation scenarios — but without stop-loss protection. "
            "That's an unnecessary risk: the good prospects could be severely impacted "
            "by an unexpected shock, without downside protection."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# MODUL 5 — Abschluss (Risiko + Chance + Gesamtfazit)
# Wird komponiert aus: top_risk_key + top_opp_key + fazit_key
# ══════════════════════════════════════════════════════════════════════════════

M5_risks = {
    "position_concentration": {
        "DE": (
            "Das grösste Risiko ist die Positionskonzentration: "
            "Ein starker Rückgang in {top_sym} würde das gesamte Portfolio überproportional belasten. "            "Das ist der wichtigste Punkt für die nächste Überprüfung."
        ),
        "EN": (
            "The biggest risk is position concentration: "
            "A sharp decline in {top_sym} would disproportionately impact the entire portfolio. "            "This is the most important point for the next review."
        ),
    },
    "sector_concentration": {
        "DE": (
            "Das grösste strukturelle Risiko ist die Sektorkonzentration in {sector}. "
            "Sektorrotationen können schnell und schmerzhaft sein — "
            "ein ausgewogeneres Bild würde die Verwundbarkeit deutlich reduzieren."
        ),
        "EN": (
            "The biggest structural risk is sector concentration in {sector}. "
            "Sector rotations can be fast and painful — "
            "a more balanced picture would significantly reduce vulnerability."
        ),
    },
    "no_stop_loss": {
        "DE": (
            "Das grösste unmittelbare Risiko ist der fehlende Stop-Loss-Schutz "
            "für einen Grossteil des Portfolios. "
            "In einem plötzlichen Markteinbruch fehlt das Sicherheitsnetz."
        ),
        "EN": (
            "The biggest immediate risk is the lack of stop-loss protection "
            "for a large portion of the portfolio. "
            "In a sudden market downturn, the safety net is missing."
        ),
    },
    "high_crypto": {
        "DE": (
            "Der hohe Krypto-Anteil ist das dominante Risiko: "
            "Kryptomärkte können in kurzer Zeit extrem einbrechen "
            "und korrelieren in Krisen typischerweise mit anderen risikoreichen Anlagen — "
            "genau dann, wenn Diversifikation am meisten gebraucht würde."
        ),
        "EN": (
            "The high crypto allocation is the dominant risk: "
            "Crypto markets can collapse extremely rapidly "            "and typically correlate with other risky assets during crises — "
            "precisely when diversification would be needed most."
        ),
    },
    "high_beta_unprotected": {
        "DE": (
            "Hohes Marktrisiko ohne ausreichende Schutzebene: "
            "Bei einem breiten Marktabschwung würde dieses Portfolio "            "überproportional verlieren — und das ohne Sicherheitsnetz."
        ),
        "EN": (
            "High market risk without adequate protection layer: "
            "In a broad market downturn, this portfolio would lose disproportionately — "            "and without a safety net."
        ),
    },
    "expensive_market_growth": {
        "DE": (
            "Das grösste externe Risiko ist die Marktkonstellation: "
            "Teures Marktumfeld kombiniert mit wachstumsorientierten Titeln "            "schafft wenig Spielraum für Enttäuschungen."
        ),
        "EN": (
            "The biggest external risk is the market constellation: "
            "Expensive market environment combined with growth-oriented positions "            "leaves little room for disappointments."
        ),
    },
    "no_defensive": {
        "DE": (
            "Das Fehlen defensiver Positionen ist ein strukturelles Risiko: "
            "Consumer Staples, Healthcare und Utilities bieten in Abschwungphasen "
            "wichtigen Schutz — den dieses Portfolio aktuell nicht hat."
        ),
        "EN": (
            "The absence of defensive positions is a structural risk: "
            "Consumer Staples, Healthcare and Utilities provide important protection "
            "during downturns — which this portfolio currently lacks."
        ),
    },
}

M5_opportunities = {
    "add_defensive": {
        "DE": (
            "Die grösste ungenutzte Chance: Defensive Sektoren ({counter_sector}) "
            "als Gegengewicht. Das würde die Schwankungsanfälligkeit senken, "
            "ohne die Renditeerwartung stark zu beeinflussen."
        ),
        "EN": (
            "The biggest untapped opportunity: defensive sectors ({counter_sector}) "
            "as a counterweight. That would reduce volatility "
            "without significantly impacting return expectations."
        ),
    },
    "rebalance_concentration": {
        "DE": (
            "Die grösste Chance liegt im Rebalancing: "
            "Durch Reduktion der grössten Positionen und Aufbau weiterer Titel "            "würde das Risiko-Rendite-Verhältnis deutlich verbessert."
        ),
        "EN": (
            "The biggest opportunity lies in rebalancing: "
            "By reducing the largest positions and building additional ones, "            "the risk-return ratio would be significantly improved."
        ),
    },
    "add_stop_loss": {
        "DE": (
            "Stop-Loss-Orders für die grössten ungeschützten Positionen "
            "würden das Verlustpotential signifikant begrenzen — "
            "ohne die Gewinnchancen einzuschränken."
        ),
        "EN": (
            "Stop-loss orders for the largest unprotected positions "
            "would significantly limit loss potential — "
            "without constraining profit opportunities."
        ),
    },
    "reduce_crypto": {
        "DE": (
            "Eine schrittweise Reduktion des Krypto-Anteils "
            "würde die Volatilität des Gesamtportfolios merklich senken "
            "und das Fundament stabiler machen."
        ),
        "EN": (
            "A gradual reduction in the crypto allocation "
            "would noticeably reduce overall portfolio volatility "
            "and make the foundation more stable."
        ),
    },
    "leverage_alpha": {
        "DE": (
            "Die positive Alpha-Generierung ist eine echte Stärke — "
            "diese Titelauswahl-Kompetenz könnte durch bessere Diversifikation "
            "noch effektiver eingesetzt werden."
        ),
        "EN": (
            "The positive Alpha generation is a real strength — "
            "this stock selection competence could be deployed "
            "even more effectively through better diversification."
        ),
    },
    "cheap_market_opportunity": {
        "DE": (
            "Das attraktive Marktumfeld bietet eine seltene Gelegenheit: "
            "In historisch fair bis attraktiv bewerteten Märkten zahlt sich "            "eine erhöhte Investitionsquote langfristig aus."
        ),
        "EN": (
            "The attractive market environment offers a rare opportunity: "
            "In historically fair to cheap markets, "            "an increased investment ratio pays off long-term."
        ),
    },
    "protect_momentum": {
        "DE": (
            "Das Portfolio hat echten Momentum — die Chance liegt darin, "
            "diesen Momentum mit besserer Absicherung zu schützen, "
            "statt ihn dem nächsten Marktschock zu überlassen."
        ),
        "EN": (
            "The portfolio has genuine momentum — the opportunity lies in "
            "protecting this momentum with better hedging, "
            "rather than leaving it exposed to the next market shock."
        ),
    },
}

M5_fazit = {
    "strong": {
        "DE": (
            "Gesamtfazit: Das Portfolio ist gut bis sehr gut aufgestellt. "
            "Die beschriebenen Anpassungen würden aus einem starken "
            "ein noch robusteres Portfolio machen."
        ),
        "EN": (
            "Overall: The portfolio is well to very well positioned. "
            "The described adjustments would turn an already strong "
            "portfolio into an even more robust one."
        ),
    },
    "solid": {
        "DE": (
            "Gesamtfazit: Das Portfolio ist solide aufgestellt mit echten Stärken. "
            "Die beschriebenen Anpassungen würden aus einem guten ein sehr gutes Portfolio machen."
        ),
        "EN": (
            "Overall: The portfolio is well-positioned with genuine strengths. "
            "The described adjustments would turn a good into a very good portfolio."
        ),
    },
    "mixed": {
        "DE": (
            "Gesamtfazit: Das Portfolio hat klare Stärken — aber auch klare Schwachstellen, "
            "die über kurz oder lang adressiert werden sollten. "
            "Der Handlungsbedarf ist überschaubar und konkret."
        ),
        "EN": (
            "Overall: The portfolio has clear strengths — but also clear weaknesses "
            "that should be addressed sooner or later. "
            "The required action is manageable and concrete."
        ),
    },
    "needs_work": {
        "DE": (
            "Gesamtfazit: Das Portfolio steht unter Druck und braucht Überarbeitung — "
            "nicht panikartiges Handeln, aber eine klare Richtungsentscheidung "
            "in den nächsten Wochen."
        ),
        "EN": (
            "Overall: The portfolio is under pressure and needs revision — "
            "not panicked action, but a clear directional decision "
            "in the coming weeks."
        ),
    },
    "critical": {
        "DE": (
            "Gesamtfazit: Die aktuelle Portfoliostruktur trägt zu viele Risiken gleichzeitig. "
            "Eine grundlegende Überprüfung ist empfohlen — "
            "schrittweise, nicht alles auf einmal, aber mit klarem Plan."
        ),
        "EN": (
            "Overall: The current portfolio structure carries too many risks simultaneously. "
            "A fundamental review is recommended — "
            "step by step, not everything at once, but with a clear plan."
        ),
    },
    "speculative_winning": {
        "DE": (
            "Gesamtfazit: Die aktuelle Phase ist gut — aber das Fundament ist fragil. "
            "Jetzt ist der richtige Zeitpunkt, Gewinne zu schützen "
            "und die Struktur schrittweise zu festigen."
        ),
        "EN": (
            "Overall: The current phase is good — but the foundation is fragile. "
            "Now is the right time to protect gains "
            "and gradually strengthen the structure."
        ),
    },
    "defensive_stable": {
        "DE": (
            "Gesamtfazit: Das Portfolio ist konservativ und stabil — "
            "was es verspricht, hält es. "
            "Die Erwartungshaltung sollte entsprechend moderat sein."
        ),
        "EN": (
            "Overall: The portfolio is conservative and stable — "
            "it delivers what it promises. "
            "Expectations should be appropriately moderate."
        ),
    },
    "well_structured": {
        "DE": (
            "Gesamtfazit: Das Portfolio ist gut strukturiert. "
            "Regelmässige Überprüfung der beschriebenen Punkte reicht als nächster Schritt."
        ),
        "EN": (
            "Overall: The portfolio is well-structured. "
            "Regular monitoring of the described points is sufficient as the next step."
        ),
    },
}
