import FifoCoverage.Basic
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Algebra.Module.Pi
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

namespace FifoCoverage
open Finset

noncomputable section

private abbrev Observable := List Bool → ℝ
private abbrev Kernel := Module.End ℝ Observable

/-- An admitted label is nonfocal with weight b and focal with weight 1 - b. -/
private def admission (b : ℝ) : Kernel where
  toFun g labels := b * g (false :: labels) + (1 - b) * g (true :: labels)
  map_add' g h := by
    ext labels
    simp only [Pi.add_apply]
    ring
  map_smul' c g := by
    ext labels
    simp only [RingHom.id_apply, Pi.smul_apply, smul_eq_mul]
    ring

/-- Build histories newest first. At the oldest end of the recursion,
rejections leave the history untouched and admissions add their label. -/
private def attempt (a b : ℝ) : Kernel :=
  a • admission b + (1 - a) • 1

private theorem attempt_apply (a b : ℝ) (g : Observable) (labels : List Bool) :
    attempt a b g labels =
      a * b * g (false :: labels) + a * (1 - b) * g (true :: labels) +
      (1 - a) * g labels := by
  change a * (b * g (false :: labels) + (1 - b) * g (true :: labels)) +
    (1 - a) * g labels = _
  ring

private def absenceIndicator (initial labels : List Bool) : ℝ :=
  if true ∈ labels.reverse.foldl admit initial then 0 else 1

/-- Finite product weighting of the absence event. Each branch has
weights (other, focal, rejected) = (a*b, a*(1-b), 1-a). -/
def absenceProbability (initial : List Bool) (a b : ℝ) (T : ℕ) : ℝ :=
  (attempt a b ^ T) (absenceIndicator initial) []

private theorem weightedRecurrence (a b : ℝ) (T : ℕ) (g : Observable)
    (labels : List Bool) :
    (attempt a b ^ (T + 1)) g labels =
      a * b * (attempt a b ^ T) g (false :: labels) +
      a * (1 - b) * (attempt a b ^ T) g (true :: labels) +
      (1 - a) * (attempt a b ^ T) g labels := by
  rw [pow_succ', Module.End.mul_apply, attempt_apply]

/-- Outcomes are independently weighted by multiplying the branch weights
as each additional attempt is prepended to the observed history. -/
private def weightedAttempts (u v : ℝ) (g : Observable) : ℕ → List Bool → ℝ
  | 0, labels => g labels
  | T + 1, labels =>
    v * weightedAttempts u v g T (false :: labels) +
    u * weightedAttempts u v g T (true :: labels) +
    (1 - u - v) * weightedAttempts u v g T labels

private theorem attempt_pow_eq_weighted (a b : ℝ) (T : ℕ) (g : Observable) (labels : List Bool) :
    (attempt a b ^ T) g labels = weightedAttempts (a * (1 - b)) (a * b) g T labels := by
  induction T generalizing labels with
  | zero => simp [weightedAttempts]
  | succ T ih =>
    rw [weightedRecurrence]
    simp only [weightedAttempts, ih]
    have rejected : 1 - a = 1 - a * (1 - b) - a * b := by ring
    rw [rejected]

/-- Direct product-weighted absence probability with focal and other weights
u and v. Each recursive level is one new independent attempt. -/
def iidAbsence (initial : List Bool) (u v : ℝ) (T : ℕ) : ℝ :=
  weightedAttempts u v (absenceIndicator initial) T []

theorem absenceProbability_eq_iid (initial : List Bool) (a b : ℝ) (T : ℕ) :
    absenceProbability initial a b T = iidAbsence initial (a * (1 - b)) (a * b) T :=
  attempt_pow_eq_weighted a b T _ []

private def checkPrefix (k : ℕ) (labels : List Bool) : ℝ :=
  if true ∈ labels.take k then 0 else 1

private theorem admission_checkPrefix (b : ℝ) (k : ℕ) :
    admission b (checkPrefix (k + 1)) = b • checkPrefix k := by
  ext labels
  by_cases h : true ∈ labels.take k <;>
    simp [admission, checkPrefix, List.mem_cons, h]

private theorem admission_one (b : ℝ) : admission b (fun _ => 1) = fun _ => 1 := by
  ext labels
  change b * 1 + (1 - b) * 1 = 1
  ring

private theorem prefix_mass (b : ℝ) (n k : ℕ) :
    (admission b ^ n) (checkPrefix k) [] = b ^ min n k := by
  induction n generalizing k with
  | zero => simp [checkPrefix]
  | succ n ih =>
    cases k with
    | zero =>
      have constant : checkPrefix 0 = fun _ => 1 := by ext labels; simp [checkPrefix]
      rw [pow_succ, Module.End.mul_apply, constant, admission_one, ← constant]
      simpa only [Nat.min_zero, pow_zero] using ih 0
    | succ k =>
      rw [pow_succ, Module.End.mul_apply, admission_checkPrefix,
        LinearMap.map_smul, Pi.smul_apply, smul_eq_mul, ih, Nat.succ_min_succ, pow_succ']

private theorem admission_pow_congr (b : ℝ) (g h : Observable) (n : ℕ)
    (labels : List Bool)
    (eqOn : ∀ xs : List Bool, xs.length = n + labels.length → g xs = h xs) :
    (admission b ^ n) g labels = (admission b ^ n) h labels := by
  induction n generalizing labels with
  | zero => simpa using eqOn labels (by simp)
  | succ n ih =>
    rw [pow_succ', Module.End.mul_apply, Module.End.mul_apply]
    change b * (admission b ^ n) g (false :: labels) +
      (1 - b) * (admission b ^ n) g (true :: labels) =
      b * (admission b ^ n) h (false :: labels) +
      (1 - b) * (admission b ^ n) h (true :: labels)
    have extend (label : Bool) :
        (admission b ^ n) g (label :: labels) =
          (admission b ^ n) h (label :: labels) := by
      apply ih
      intro xs length
      apply eqOn
      simp only [List.length_cons] at length
      omega
    rw [extend false, extend true]

private theorem admitted_mass (initial : List Bool) (positive : 0 < initial.length)
    (b : ℝ) (n : ℕ) :
    (admission b ^ n) (absenceIndicator initial) [] =
      if lastFocal initial ≤ n then b ^ min n initial.length else 0 := by
  have event (labels : List Bool) (length : labels.length = n) :
      true ∉ labels.reverse.foldl admit initial ↔
        lastFocal initial ≤ n ∧ true ∉ labels.take initial.length := by
    rw [foldl_admit_absent_iff _ _ positive, List.length_reverse, length]
    unfold retain
    rw [List.length_reverse, ← List.reverse_take]
    simp
  by_cases threshold : lastFocal initial ≤ n
  · rw [if_pos threshold, ← prefix_mass b n initial.length]
    apply admission_pow_congr
    intro labels length
    have eq := event labels (by simpa using length)
    simp only [threshold, true_and] at eq
    unfold absenceIndicator checkPrefix
    by_cases member : true ∈ labels.take initial.length
    · have member' : true ∈ labels.reverse.foldl admit initial := by
        by_contra h
        exact (eq.mp h) member
      simp only [if_pos member, if_pos member']
    · have absent : true ∉ labels.reverse.foldl admit initial := eq.mpr member
      simp only [if_neg member, if_neg absent]
  · rw [if_neg threshold]
    change (admission b ^ n) (absenceIndicator initial) [] = (0 : Observable) []
    rw [← LinearMap.map_zero (admission b ^ n)]
    apply admission_pow_congr
    intro labels length
    have member : true ∈ labels.reverse.foldl admit initial := by
      by_contra absent
      exact threshold ((event labels (by simpa using length)).mp absent).1
    simp only [absenceIndicator, if_pos member, Pi.zero_apply]

def binomialMass (a : ℝ) (T n : ℕ) : ℝ :=
  (T.choose n : ℝ) * a ^ n * (1 - a) ^ (T - n)

private theorem scalar_step_pow (c : ℝ) (f : Kernel) (n : ℕ) :
    (c • f) ^ n = c ^ n • f ^ n := by
  induction n with
  | zero => simp
  | succ n ih => rw [pow_succ, ih, smul_mul_smul_comm, ← pow_succ, ← pow_succ]

theorem absenceProbability_eq_sum (initial : List Bool) (positive : 0 < initial.length)
    (a b : ℝ) (T : ℕ) :
    absenceProbability initial a b T = ∑ n ∈ range (T + 1),
      if lastFocal initial ≤ n then binomialMass a T n * b ^ min n initial.length else 0 := by
  have commute : Commute (a • admission b) ((1 - a) • (1 : Kernel)) := by
    change (a • admission b) * ((1 - a) • (1 : Kernel)) =
      ((1 - a) • (1 : Kernel)) * (a • admission b)
    simp only [smul_mul_smul_comm, mul_one, one_mul, mul_comm a (1 - a)]
  unfold absenceProbability
  change (((a • admission b + (1 - a) • (1 : Kernel)) ^ T)
    (absenceIndicator initial) []) = _
  rw [commute.add_pow]
  simp only [LinearMap.sum_apply, Finset.sum_apply]
  apply sum_congr rfl
  intro n _
  rw [scalar_step_pow, scalar_step_pow]
  simp only [one_pow, smul_mul_smul_comm, mul_one]
  simp only [Module.End.mul_apply, LinearMap.smul_apply, Pi.smul_apply, smul_eq_mul,
    Module.End.natCast_apply, ← Nat.cast_smul_eq_nsmul ℝ, LinearMap.map_smul]
  rw [admitted_mass initial positive]
  by_cases h : lastFocal initial ≤ n
  · simp only [if_pos h, binomialMass]
    ring
  · simp [h]

theorem absenceProbability_zero_admission (initial : List Bool) (b : ℝ) (T : ℕ) :
    absenceProbability initial 0 b T = if lastFocal initial = 0 then 1 else 0 := by
  simp only [absenceProbability, attempt, zero_smul, sub_zero, one_smul, zero_add,
    one_pow, Module.End.one_apply, absenceIndicator, List.reverse_nil, List.foldl_nil]
  have h := drop_absent_iff initial 0
  simp only [List.drop_zero, Nat.le_zero] at h
  by_cases member : true ∈ initial
  · have ne : lastFocal initial ≠ 0 := fun eq => h.mpr eq member
    simp [member, ne]
  · simp [member, h.mp member]

end

end FifoCoverage
