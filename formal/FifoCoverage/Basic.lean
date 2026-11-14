import Lean

/-! A full FIFO buffer, represented oldest first. True marks the focal family. -/

namespace FifoCoverage

def admit (memory : List Bool) (label : Bool) : List Bool :=
  memory.drop 1 ++ [label]

def retain (capacity : Nat) (entries : List Bool) : List Bool :=
  entries.drop (entries.length - capacity)

/-- Repeated FIFO updates keep exactly the newest capacity-many entries. -/
theorem foldl_admit_eq_retain (initial labels : List Bool)
    (positive : 0 < initial.length) :
    labels.foldl admit initial = retain initial.length (initial ++ labels) := by
  induction labels generalizing initial with
  | nil => simp [retain]
  | cons label labels ih =>
    have length_admit : (admit initial label).length = initial.length := by
      simp only [admit, List.length_append, List.length_drop, List.length_singleton]
      omega
    simp only [List.foldl_cons]
    rw [ih _ (length_admit ▸ positive), length_admit]
    have drop_one : (initial ++ label :: labels).drop 1 =
        initial.drop 1 ++ label :: labels :=
      List.drop_append_of_le_length (by omega)
    simp only [retain, admit, List.length_append, List.length_drop, List.length_cons,
      List.singleton_append, List.append_assoc]
    rw [← drop_one, List.drop_drop]
    congr 1
    omega

/-- Index of the last focal entry, counted from one, with zero for absence. -/
def lastFocal : List Bool → Nat
  | [] => 0
  | label :: rest =>
    match lastFocal rest with
    | 0 => if label then 1 else 0
    | n + 1 => n + 2

theorem drop_absent_iff (initial : List Bool) (n : Nat) :
    true ∉ initial.drop n ↔ lastFocal initial ≤ n := by
  induction initial generalizing n with
  | nil => simp [lastFocal]
  | cons label rest ih =>
    have zero_iff := ih 0
    simp only [List.drop_zero, Nat.le_zero] at zero_iff
    cases n with
    | zero =>
      cases label <;> cases h : lastFocal rest <;>
        simp_all [lastFocal, List.mem_cons]
    | succ n =>
      simp only [List.drop_succ_cons, ih]
      cases h : lastFocal rest <;> cases label <;> simp [lastFocal, h] <;> omega

theorem lastFocal_le_length (initial : List Bool) : lastFocal initial ≤ initial.length :=
  (drop_absent_iff initial initial.length).mp (by simp)

/-- A focal example survives iff the initial suffix or the admitted suffix contains one. -/
theorem foldl_admit_absent_iff (initial labels : List Bool)
    (positive : 0 < initial.length) :
    true ∉ labels.foldl admit initial ↔
      lastFocal initial ≤ labels.length ∧
      true ∉ retain initial.length labels := by
  rw [foldl_admit_eq_retain initial labels positive]
  simp only [retain, List.length_append, Nat.add_sub_cancel_left, List.drop_append,
    List.mem_append, not_or, drop_absent_iff]

/-- If no focal admission arrives, the initial family disappears at its last slot. -/
theorem no_replenishment (initial labels : List Bool) (positive : 0 < initial.length)
    (nonfocal : true ∉ labels) :
    true ∉ labels.foldl admit initial ↔ lastFocal initial ≤ labels.length := by
  rw [foldl_admit_absent_iff initial labels positive]
  have absent : true ∉ retain initial.length labels := fun member =>
    nonfocal (List.mem_of_mem_drop member)
  simp [absent]

/-- Once the initial memory has been flushed, the last capacity-many admissions
alone determine coverage, for any history of admission decisions. -/
theorem absent_after_flush (initial labels : List Bool) (positive : 0 < initial.length)
    (flushed : initial.length ≤ labels.length) :
    true ∉ labels.foldl admit initial ↔ true ∉ retain initial.length labels := by
  rw [foldl_admit_absent_iff initial labels positive]
  simp [Nat.le_trans (lastFocal_le_length initial) flushed]

end FifoCoverage
