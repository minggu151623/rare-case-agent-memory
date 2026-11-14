import FifoCoverage.Probability
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Data.Nat.Choose.Bounds
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith

namespace FifoCoverage
open Filter Finset
open scoped Topology

private theorem sum_binomialMass (a : ℝ) (T : ℕ) :
    ∑ n ∈ range (T + 1), binomialMass a T n = 1 := by
  calc
    _ = (a + (1 - a)) ^ T := by
      rw [add_pow]
      apply sum_congr rfl
      intro n _
      unfold binomialMass
      ring
    _ = 1 := by rw [show a + (1 - a) = 1 by ring, one_pow]

private theorem binomialMass_nonneg {a : ℝ} (ha : 0 ≤ a) (ha' : a ≤ 1) (T n : ℕ) :
    0 ≤ binomialMass a T n := by
  unfold binomialMass
  exact mul_nonneg (mul_nonneg (Nat.cast_nonneg _) (pow_nonneg ha _))
    (pow_nonneg (sub_nonneg.mpr ha') _)

private theorem binomialMass_tendsto_zero {a : ℝ} (ha : 0 < a) (ha' : a ≤ 1) (n : ℕ) :
    Tendsto (fun T => binomialMass a T n) atTop (𝓝 0) := by
  apply (tendsto_add_atTop_iff_nat n).mp
  have geom := tendsto_pow_const_mul_const_pow_of_lt_one n
    (sub_nonneg.mpr ha') (show 1 - a < 1 by linarith)
  -- Shift the horizon by n to remove the truncated subtraction in the exponent.
  have bound_limit : Tendsto (fun T : ℕ => ((T + n : ℕ) : ℝ) ^ n * a ^ n *
        (1 - a) ^ T) atTop (𝓝 0) := by
    by_cases hw : 1 - a = 0
    · apply tendsto_const_nhds.congr'
      filter_upwards [eventually_ge_atTop (1 : ℕ)] with T ht
      simp [hw, Nat.ne_of_gt (lt_of_lt_of_le Nat.zero_lt_one ht)]
    · have heq (T : ℕ) :
          ((T + n : ℕ) : ℝ) ^ n * a ^ n * (1 - a) ^ T =
            (a ^ n / (1 - a) ^ n) * (((T + n : ℕ) : ℝ) ^ n * (1 - a) ^ (T + n)) := by
        rw [pow_add]
        field_simp [hw]
      simp_rw [heq]
      have h := (tendsto_add_atTop_iff_nat n).mpr geom
      simpa only [mul_zero] using h.const_mul (a ^ n / (1 - a) ^ n)
  refine squeeze_zero (fun T => binomialMass_nonneg ha.le ha' (T + n) n) ?_ bound_limit
  intro T
  unfold binomialMass
  rw [Nat.add_sub_cancel]
  have hc : ((T + n).choose n : ℝ) ≤ ((T + n : ℕ) : ℝ) ^ n := by
    exact_mod_cast Nat.choose_le_pow (T + n) n
  exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right hc (pow_nonneg ha.le _))
    (pow_nonneg (sub_nonneg.mpr ha') _)

/-- Positive admission rate gives the paper's asymptotic FIFO absence probability. -/
theorem absenceProbability_tendsto (initial : List Bool) (positive : 0 < initial.length)
    {a b : ℝ} (ha : 0 < a) (ha' : a ≤ 1) :
    Tendsto (absenceProbability initial a b) atTop (𝓝 (b ^ initial.length)) := by
  let K := initial.length
  let weight : ℕ → ℝ := fun n => if lastFocal initial ≤ n then b ^ min n K else 0
  have eventual (T : ℕ) (ht : K ≤ T + 1) :
      absenceProbability initial a b T - b ^ K =
        ∑ n ∈ range K, binomialMass a T n * (weight n - b ^ K) := by
    have total : ∑ n ∈ range (T + 1), binomialMass a T n * b ^ K = b ^ K := by
      rw [← sum_mul, sum_binomialMass, one_mul]
    rw [absenceProbability_eq_sum initial positive]
    conv_lhs => rw [← total]
    rw [← sum_sub_distrib]
    refine (sum_congr rfl ?_).trans (sum_subset (range_mono ht) ?_).symm
    · intro n _
      by_cases h : lastFocal initial ≤ n <;> simp [weight, h, mul_sub, K]
    · intro n _ outside
      have hkn : K ≤ n := Nat.le_of_not_lt (fun h => outside (mem_range.mpr h))
      have hrn : lastFocal initial ≤ n := (lastFocal_le_length initial).trans hkn
      simp [weight, hrn, min_eq_right hkn]
  have vanish : Tendsto (fun T : ℕ =>
      ∑ n ∈ range K, binomialMass a T n * (weight n - b ^ K)) atTop (𝓝 0) := by
    have hsum : Tendsto (fun T : ℕ =>
        ∑ n ∈ range K, binomialMass a T n * (weight n - b ^ K)) atTop
        (𝓝 (∑ _n ∈ range K, (0 : ℝ))) := by
      apply tendsto_finset_sum
      intro n _
      simpa only [zero_mul] using
        (binomialMass_tendsto_zero ha ha' n).mul_const (weight n - b ^ K)
    simpa using hsum
  have diff : Tendsto (fun T => absenceProbability initial a b T - b ^ K) atTop (𝓝 0) :=
    vanish.congr' (by
      filter_upwards [eventually_ge_atTop K] with T ht
      exact (eventual T (by omega)).symm)
  simpa using diff.add_const (b ^ K)

end FifoCoverage
