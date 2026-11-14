import FifoCoverage.Limit

namespace FifoCoverage
open Filter Finset
open scoped Topology

/-- The paper's parameters give exactly the product weights on the attempt outcomes. -/
theorem paper_weights (initial : List Bool) {u v : ℝ} (ha : u + v ≠ 0) (T : ℕ) :
    absenceProbability initial (u + v) (1 - u / (u + v)) T = iidAbsence initial u v T := by
  rw [absenceProbability_eq_iid]
  have hu : (u + v) * (1 - (1 - u / (u + v))) = u := by
    field_simp [ha]
    ring
  have hv : (u + v) * (1 - u / (u + v)) = v := by
    field_simp [ha]
    ring
  rw [hu, hv]

/-- The E005 reference law in the paper's parameterization. When u + v > 0,
the three attempt weights are u, v, and 1 - u - v. -/
noncomputable def paperAbsence (initial : List Bool) (u v : ℝ) (T : ℕ) : ℝ :=
  absenceProbability initial (u + v) (1 - u / (u + v)) T

theorem paper_finite (initial : List Bool) (positive : 0 < initial.length)
    (u v : ℝ) (T : ℕ) :
    paperAbsence initial u v T = ∑ n ∈ range (T + 1),
      if lastFocal initial ≤ n then
        (T.choose n : ℝ) * (u + v) ^ n * (1 - (u + v)) ^ (T - n) *
          (1 - u / (u + v)) ^ min n initial.length
      else 0 := by
  exact absenceProbability_eq_sum initial positive _ _ T

theorem paper_no_admission (initial : List Bool) {u v : ℝ}
    (zero : u + v = 0) (T : ℕ) :
    paperAbsence initial u v T = if lastFocal initial = 0 then 1 else 0 := by
  unfold paperAbsence
  rw [zero, absenceProbability_zero_admission]

theorem paper_limit (initial : List Bool) (positive : 0 < initial.length)
    {u v : ℝ} (ha : 0 < u + v) (ha' : u + v ≤ 1) :
    Tendsto (paperAbsence initial u v) atTop
      (𝓝 ((1 - u / (u + v)) ^ initial.length)) :=
  absenceProbability_tendsto initial positive ha ha'

/-- The finite formula applied directly to the product-weighted i.i.d. law. -/
theorem iid_finite (initial : List Bool) (positive : 0 < initial.length)
    {u v : ℝ} (ha : 0 < u + v) (T : ℕ) :
    iidAbsence initial u v T = ∑ n ∈ range (T + 1),
      if lastFocal initial ≤ n then
        (T.choose n : ℝ) * (u + v) ^ n * (1 - (u + v)) ^ (T - n) *
          (1 - u / (u + v)) ^ min n initial.length
      else 0 := by
  rw [← paper_weights initial ha.ne' T]
  exact paper_finite initial positive u v T

theorem iid_no_admission (initial : List Bool) (T : ℕ) :
    iidAbsence initial 0 0 T = if lastFocal initial = 0 then 1 else 0 := by
  have h := absenceProbability_eq_iid initial 0 0 T
  simp only [zero_mul] at h
  rw [← h, absenceProbability_zero_admission]

/-- Under valid probability weights, rate zero forces both admission weights to zero. -/
theorem iid_no_admission_of_rate_zero (initial : List Bool) {u v : ℝ}
    (hu : 0 ≤ u) (hv : 0 ≤ v) (ha : u + v = 0) (T : ℕ) :
    iidAbsence initial u v T = if lastFocal initial = 0 then 1 else 0 := by
  have uz : u = 0 := by linarith
  have vz : v = 0 := by linarith
  rw [uz, vz, iid_no_admission]

theorem iid_absent_before_last (initial : List Bool) (positive : 0 < initial.length)
    {u v : ℝ} (ha : 0 < u + v) {T : ℕ} (horizon : T < lastFocal initial) :
    iidAbsence initial u v T = 0 := by
  rw [iid_finite initial positive ha T]
  apply sum_eq_zero
  intro n hn
  have bound := mem_range.mp hn
  have tooEarly : ¬ lastFocal initial ≤ n := by omega
  simp only [if_neg tooEarly]

theorem iid_limit (initial : List Bool) (positive : 0 < initial.length)
    {u v : ℝ} (ha : 0 < u + v) (ha' : u + v ≤ 1) :
    Tendsto (iidAbsence initial u v) atTop
      (𝓝 ((1 - u / (u + v)) ^ initial.length)) := by
  convert paper_limit initial positive ha ha' using 1
  funext T
  exact (paper_weights initial ha.ne' T).symm

end FifoCoverage
