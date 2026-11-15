import FifoCoverage.Paper
import Mathlib.Tactic.NormNum

/-! Conversion of a long-run absence target into admitted-share and
proposal-share thresholds, as used after the proposition in Section 4. -/

namespace FifoCoverage

/-- The long-run absence value decreases in the admitted focal share. With
`δ = (1 - q⋆) ^ K`, absence is at most `δ` exactly when the share is at least `q⋆`. -/
theorem absence_limit_le_iff {q qs : ℝ} (hq : q ≤ 1) (hqs : qs ≤ 1) {K : ℕ} (hK : K ≠ 0) :
    (1 - q) ^ K ≤ (1 - qs) ^ K ↔ qs ≤ q := by
  rw [pow_le_pow_iff_left₀ (sub_nonneg.mpr hq) (sub_nonneg.mpr hqs) hK]
  constructor <;> intro h <;> linarith

private theorem mixture_pos {p x y : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hx : 0 < x)
    (hy : 0 < y) : 0 < p * x + (1 - p) * y := by
  rcases hp0.lt_or_eq with positive | zero
  · have first := mul_pos positive hx
    have second := mul_nonneg (sub_nonneg.mpr hp1) hy.le
    linarith
  · rw [← zero]
    simpa using hy

/-- Proposal share `p`, focal pass rate `α`, other pass rate `β`. The admitted
focal share is at least `q⋆` exactly when `p` reaches the printed threshold. -/
theorem admitted_share_ge_iff {p α β qs : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (hα : 0 < α) (hβ : 0 < β) (hq0 : 0 ≤ qs) (hq1 : qs ≤ 1) :
    qs ≤ p * α / (p * α + (1 - p) * β) ↔
      qs * β / (α * (1 - qs) + qs * β) ≤ p := by
  have admitted : 0 < p * α + (1 - p) * β := mixture_pos hp0 hp1 hα hβ
  have threshold : 0 < α * (1 - qs) + qs * β := by
    have h := mixture_pos hq0 hq1 hβ hα
    linarith
  rw [le_div_iff₀ admitted, div_le_iff₀ threshold]
  constructor <;> intro h <;> nlinarith [h]

/-- The admitted focal share never exceeds one. -/
theorem admitted_share_le_one {p α β : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (hα : 0 < α) (hβ : 0 < β) : p * α / (p * α + (1 - p) * β) ≤ 1 := by
  have admitted : 0 < p * α + (1 - p) * β := mixture_pos hp0 hp1 hα hβ
  rw [div_le_one admitted]
  have other := mul_nonneg (sub_nonneg.mpr hp1) hβ.le
  linarith

/-- Section 4's threshold. With admission weights `u = p α` and `v = (1 - p) β`,
the limit in `iid_limit` is at most `(1 - q⋆) ^ K` exactly when the proposal
share is at least `q⋆ β / (α (1 - q⋆) + q⋆ β)`. -/
theorem long_run_absence_le_iff {p α β qs : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (hα : 0 < α) (hβ : 0 < β) (hq0 : 0 ≤ qs) (hq1 : qs ≤ 1) {K : ℕ} (hK : K ≠ 0) :
    (1 - p * α / (p * α + (1 - p) * β)) ^ K ≤ (1 - qs) ^ K ↔
      qs * β / (α * (1 - qs) + qs * β) ≤ p := by
  rw [absence_limit_le_iff (admitted_share_le_one hp0 hp1 hα hβ) hq1 hK]
  exact admitted_share_ge_iff hp0 hp1 hα hβ hq0 hq1

/-- Worked example: six slots, ten percent focal proposals, equal pass rates.
The long-run absence value is 0.531441. -/
theorem example_equal_rates :
    (1 - (1 / 10 : ℝ) * (4 / 5) / ((1 / 10) * (4 / 5) + (1 - 1 / 10) * (4 / 5))) ^ 6 =
      531441 / 1000000 := by
  norm_num

/-- Worked example: focal pass rate 0.2 and other pass rate 0.8. The admitted
share is 1/37 (about 2.7%) and the long-run absence value lies in (0.84, 0.85). -/
theorem example_unequal_rates :
    (1 / 10 : ℝ) * (1 / 5) / ((1 / 10) * (1 / 5) + (1 - 1 / 10) * (4 / 5)) = 1 / 37 ∧
      (21 / 25 : ℝ) < (1 - 1 / 37) ^ 6 ∧ (1 - 1 / 37 : ℝ) ^ 6 < 17 / 20 := by
  norm_num

end FifoCoverage
