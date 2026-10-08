"""Small math helpers used by the sample project. Contains one deliberate bug."""


def average(nums):
    # BUG: dividing by (len - 1) gives the wrong mean. Should divide by len(nums).
    return sum(nums) / (len(nums) - 1)


def is_even(n):
    return n % 2 == 0
