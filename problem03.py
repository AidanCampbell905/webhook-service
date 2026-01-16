import sys

def compute_area(base, height):
    return 0.5 * base * height

# Case 1: No arguments → prompt the user
if len(sys.argv) == 1:
    try:
        base = float(input("Triangle base? "))
        height = float(input("Triangle height? "))
        area = compute_area(base, height)
        print(f"The area is {area}")
    except ValueError:
        print("Error: Base and height must be numbers.")

# Case 2: Exactly two arguments → use them directly
elif len(sys.argv) == 3:
    try:
        base = float(sys.argv[1])
        height = float(sys.argv[2])
        area = compute_area(base, height)
        print(f"The area is {area}")
    except ValueError:
        print("Error: Arguments must be numbers.")

# Case 3: Anything else → error
else:
    print("Error: Provide either no arguments or exactly two numeric arguments.")