import sys

def circle_area(radius):
    return 3.14 * radius * radius

# Case 1: No command-line arguments → interactive loop
if len(sys.argv) == 1:
    while True:
        try:
            r = input("Radius? ")
            if r == "":
                continue
            radius = float(r)
            area = circle_area(radius)
            print(f"Area is {area} for radius {radius}")
        except EOFError:
            break
        except ValueError:
            print("Error: Radius must be a number.")

# Case 2: Arguments provided → loop over them
else:
    for arg in sys.argv[1:]:
        try:
            radius = float(arg)
            area = circle_area(radius)
            print(f"Area is {area} for radius {radius}")
        except ValueError:
            print(f"Error: '{arg}' is not a valid number.")