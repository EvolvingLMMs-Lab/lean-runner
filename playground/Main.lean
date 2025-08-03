import Mathlib
import Aesop

open Real Nat Topology Rat BigOperators

theorem simple_theorem (a b : ℝ) (h : a = b) : a = b := by rw [h]
