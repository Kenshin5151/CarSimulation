# ============================================================

# Author: Edmun Lau
# Date: 20250315

# This Python script simulates car movements and collisions.
# It accepts input data for car names, positions, and movement commands.
# The program tracks the position of each car and detects collisions.

# ============================================================

import sys

DIRECTIONS = ['N', 'E', 'S', 'W']
MOVES = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}
COMMANDS = ['L', 'R', 'F']


class Car:
    def __init__(self, name, x, y, direction, commands):
        self.name = name
        self.x = x
        self.y = y
        self.direction = direction
        self.commands = list(commands)
        self.step = 0
        self.collided = False
        self.collision_record = list() # create empty list.

    def rotate_left(self):
        self.direction = DIRECTIONS[(DIRECTIONS.index(self.direction) - 1) % 4]
        if 'pydevd' in sys.modules:
            print(f"Car {self.name} stays at ({self.x}, {self.y})")

    def rotate_right(self):
        self.direction = DIRECTIONS[(DIRECTIONS.index(self.direction) + 1) % 4]
        if 'pydevd' in sys.modules:
            print(f"Car {self.name} stays at ({self.x}, {self.y})")

    def move_forward(self, width, height):
        if not self.collided:
            dx, dy = MOVES[self.direction]
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < width and 0 <= new_y < height:
                self.x, self.y = new_x, new_y
                if 'pydevd' in sys.modules:
                    print(f"Car {self.name} moves to ({self.x}, {self.y}) in direction {self.direction}")
            else:
                if 'pydevd' in sys.modules:
                    print(f"Car {self.name} stays at ({self.x}, {self.y})")

    def process_command(self, command, width, height):
        if not self.collided:

            if 'pydevd' in sys.modules:
                print(f"Car {self.name} processes command {command}")

            if command == 'L':
                self.rotate_left()
            elif command == 'R':
                self.rotate_right()
            elif command == 'F':
                self.move_forward(width, height)

    def __str__(self):
        return f'- {self.name}, ({self.x},{self.y}) {self.direction}, {"".join(self.commands)}'



class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cars = []
        self.cars_original = []

    def add_car(self, name, x, y, direction, commands):
        self.cars.append(Car(name, x, y, direction, commands))

    def add_car_original(self, name, x, y, direction, commands):
        self.cars_original.append(Car(name, x, y, direction, commands))

    def run(self):

        # Run and move every car for each step
        step = 0

        while True:

            active_commands = False

            # Creates an empty dictionary
            positions = {}

            # Check every car
            for car in self.cars:
                # If there is a command and not yet collided, move it.
                if car.commands and not car.collided:

                    active_commands = True

                    if 'pydevd' in sys.modules:
                        print(f"Step {step + 1} - Car {car.name}: {car.x}, {car.y}, {car.direction}")

                    # Pull the current command from the command list.
                    car.process_command(car.commands.pop(0), self.width, self.height)
                    # Record the current position
                    pos = (car.x, car.y, step)

                    # This position at this step has no car, add it.
                    if not pos in positions:
                        positions[pos] = [car]
                    else:
                        # Meaning collision occurs !
                        # print(f'- {positions[pos].name}, collides with {car.name} at {(positions[pos].x, positions[pos].y)} at step {step + 1}')
                        # print(f'- {car.name}, collides with {positions[pos].name} at {(car.x, car.y)} at step {step + 1}')

                        # get each previous car at pos
                        for c in positions[pos]:
                            c.collided = True
                            # append its collision list.
                            c.collision_record.append(f'- {c.name}, collides with {car.name} at {(car.x, car.y)} at step {step + 1}')
                            # append the current car's collision list.
                            car.collision_record.append(f'- {car.name}, collides with {c.name} at {(c.x, c.y)} at step {step + 1}')

                        car.collided = True
                        positions[pos].append(car)

            if not active_commands:
                break

            step += 1

    def display_original_position(self):
        print("Your current list of cars are:")
        for car in self.cars_original:
            print(str(car))

    def display_new_position(self):
        print("\nAfter simulation, the result is:")
        for car in self.cars:
            if car.collided:
                # Show all its collision records.
                print("\n".join(car.collision_record))
            else:
                # Show the final position of the car
                print(f'- {car.name}, ({car.x},{car.y}) {car.direction}')

    def reset(self):
        self.cars.clear()
        self.cars_original.clear()



class ValidInput:
    @staticmethod
    def get_valid_input(car_name, width, height):
        try:
            x, y, direction = input(f"Please enter initial position of car {car_name} in x y Direction format:\n").split()
        except ValueError as e:
            raise ValueError(e)

        # Check if x and y are integers
        if not (x.isdigit() and y.isdigit()):
            raise ValueError("Error: X and Y must be integers. Please enter valid values.")

        x, y = int(x), int(y)

        # Check coordinates
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"Error: The coordinates ({x}, {y}) are outside the valid range. Please enter values between 0 and {width - 1} for x and 0 and {height - 1} for y.")

        # Check direction
        if not (direction in DIRECTIONS):
            raise ValueError(f"Error: The direction {direction} is not valid. Please select from: {', '.join(DIRECTIONS)}.")

        return x, y, direction


    @staticmethod
    def get_valid_commands(car_name):
        commands = input(f"Please enter the commands for car {car_name}:\n").strip()
        if not all(command in COMMANDS for command in commands):
            raise ValueError(f"Error: Invalid command. Please enter only 'L', 'R', or 'F'.")
        return commands


class VerifyFieldSize:
    @staticmethod
    def verify_width_height():

        user_input = input("Please enter the width and height of the simulation field in x y format:\n").strip()
        values = user_input.split()

        # Ensure exactly two values are entered
        if len(values) != 2:
            raise ValueError("Error: Please enter exactly two numbers separated by a space.")

        # Check if both values are positive integers
        if not all(val.isdigit() for val in values):
            raise ValueError("Error: Width and height must be positive integers.")

        # Convert to integers
        width, height = map(int, values)

        # Ensure width and height are greater than 0
        if width <= 0 or height <= 0:
            raise ValueError("Error: Width and height must be greater than zero.")

        return width, height



if __name__ == '__main__':
    print("Welcome to Auto Driving Car Simulation!")

    while True:

        while True:
            try:
                width, height = VerifyFieldSize.verify_width_height()
                break
            except ValueError as e:
                print(e)
                continue

        # Create the field
        simulation = Simulation(width, height)
        print(f"You have created a field of {width} x {height}.\n")

        while True:
            print("Please choose from the following options:")
            print("[1] Add a car to field")
            print("[2] Run simulation")
            choice = input().strip()

            if choice == '1':

                car_name = input("Please enter the name of the car:\n").strip()

                # Loop if car_name is empty
                while not car_name:
                    print("Error: Car name cannot be an empty string.")
                    car_name = input("Please enter the name of the car:\n").strip()

                while True:
                    try:
                        x, y, direction = ValidInput.get_valid_input(car_name, width, height)
                        break
                    except ValueError as e:
                        print(e)
                        continue

                while True:
                    try:
                        commands = ValidInput.get_valid_commands(car_name)
                        break
                    except ValueError as e:
                        print(e)
                        continue

                simulation.add_car_original(car_name, x, y, direction, commands)
                simulation.add_car(car_name, x, y, direction, commands)
                simulation.display_original_position()

            elif choice == '2':

                simulation.display_original_position()
                simulation.run()
                simulation.display_new_position()
                break

        print("\nPlease choose from the following options:")

        while True:
            try:
                print("[1] Start over")
                print("[2] Exit")
                choice = input().strip()

                if choice not in {'1', '2'}:
                    raise ValueError("Invalid choice")

                if choice == '1':
                    print("\nWelcome to Auto Driving Car Simulation!\n")
                    simulation.reset()
                    break  # Restart loop

                elif choice == '2':
                    print("Thank you for running the simulation. Goodbye!")
                    sys.exit()

            except ValueError as e:
                print(f"❌ Error: {e}. Please enter 1 or 2.")  # Custom error message



