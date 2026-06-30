// Helpers for the housing-pressure "family of measures" (MET-1 / VIZ-4).
//
// The headline index — rent as a share of income — hides one assumption
// (m²/person). MET-1 makes that assumption selectable and shows it alongside
// two assumption-free measures of the same idea ("rent runs ahead of income"):
// a z-score gap and a percentile gap. When all three rank the same barrios as
// most-stressed, the message is robust rather than an artefact of the 30 m².

/** Rent as a share of one resident's income, given m²/person (the headline,
 * assumption-bearing measure). rent is €/m²/month, income is €/year. */
export function shareOfIncome(rent: number, income: number, m2: number): number {
  return (rent * 12 * m2) / income * 100;
}

/** Sample z-scores (ddof=1). Returns zeros if there is no spread. */
export function zScores(values: number[]): number[] {
  const n = values.length;
  if (n === 0) return [];
  const mean = values.reduce((a, b) => a + b, 0) / n;
  const variance = n > 1
    ? values.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1)
    : 0;
  const sd = Math.sqrt(variance);
  if (sd === 0) return values.map(() => 0);
  return values.map((v) => (v - mean) / sd);
}

/** Percentile rank of each value in [0, 1] (midrank for ties). */
export function percentileRanks(values: number[]): number[] {
  const n = values.length;
  if (n <= 1) return values.map(() => 0);
  return values.map((v) => {
    let less = 0;
    let equal = 0;
    for (const w of values) {
      if (w < v) less++;
      else if (w === v) equal++;
    }
    const rank = less + (equal - 1) / 2; // 0-based midrank
    return rank / (n - 1);
  });
}

/** The two assumption-free pressure gaps from aligned rent/income arrays.
 * Positive = rent runs ahead of income (more pressure on the resident). */
export function pressureGaps(rent: number[], income: number[]): {
  zGap: number[];
  pctGap: number[];
} {
  const zr = zScores(rent);
  const zi = zScores(income);
  const pr = percentileRanks(rent);
  const pi = percentileRanks(income);
  return {
    zGap: zr.map((v, i) => v - zi[i]),
    pctGap: pr.map((v, i) => (v - pi[i]) * 100), // percentile points
  };
}
