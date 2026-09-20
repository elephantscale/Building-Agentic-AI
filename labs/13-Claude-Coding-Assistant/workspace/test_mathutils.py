"""Runnable test script (no pytest needed): prints ALL TESTS PASSED or raises."""

from mathutils import average, is_even

assert average([2, 4, 6]) == 4, f"average([2,4,6]) should be 4, got {average([2, 4, 6])}"
assert average([10, 20]) == 15, f"average([10,20]) should be 15, got {average([10, 20])}"
assert is_even(4) and not is_even(3), "is_even is wrong"

print("ALL TESTS PASSED")
