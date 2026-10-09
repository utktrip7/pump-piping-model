from friction import turbulent_friction_factor

# Valid cases
print(turbulent_friction_factor(25349, 0.0254, 0.0000015))     # about 0.0245
print(turbulent_friction_factor(100000, 0.0254, 0.0000254))    # about 0.0223
print(turbulent_friction_factor(1000000, 0.0254, 0.00000254))  # about 0.0135

# Each of these should raise a different error message
bad_cases = [
    (3000, 0.0254, 0.0000254),    # Re too low for turbulent
    (100000, 0, 0.0000254),       # zero diameter
    (100000, 0.0254, -1),         # negative roughness
    (-5, 0.0254, 0.0000254),      # negative Re
]
for re, d, eps in bad_cases:
    try:
        turbulent_friction_factor(re, d, eps)
        print("NO ERROR RAISED for", re, d, eps)
    except ValueError as e:
        print("OK:", e)