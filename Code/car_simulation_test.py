import unittest
from unittest.mock import patch
from io import StringIO
import sys

from car_simulation import Car, Simulation, DIRECTIONS, MOVES, ValidInput

class TestCar(unittest.TestCase):
    def setUp(self):
        """Set up the initial conditions for testing."""
        # Initializing car instance
        self.car = Car("TestCar", 0, 0, 'N', ['F', 'R', 'F'])

    def test_initial_position(self):
        """Test if the car starts at the correct position."""
        self.assertEqual(self.car.x, 0)
        self.assertEqual(self.car.y, 0)
        self.assertEqual(self.car.direction, 'N')

    def test_rotate_left(self):
        """Test if the car rotates left correctly."""
        self.car.rotate_left()
        self.assertEqual(self.car.direction, 'W')

    def test_rotate_right(self):
        """Test if the car rotates right correctly."""
        self.car.rotate_right()
        self.assertEqual(self.car.direction, 'E')

    def test_move_forward_within_bounds(self):
        """Test if the car moves forward within the grid bounds."""
        self.car.move_forward(5, 5)  # Grid is 5x5
        self.assertEqual(self.car.x, 0)
        self.assertEqual(self.car.y, 1)

    def test_move_forward_out_of_bounds_x_only(self):
        """Test if the car stops moving when out of bounds."""
        self.car.x = 4
        self.car.move_forward(5, 5)  # Grid is 5x5
        self.assertEqual(self.car.x, 4)  # Should not change

    def test_move_forward_out_of_bounds(self):
        """Test if the car stops moving when out of bounds."""
        self.car.x = 4
        self.car.y = 4
        self.car.move_forward(5, 5)  # Grid is 5x5
        self.assertEqual(self.car.x, 4)  # Should not change
        self.assertEqual(self.car.y, 4)  # Should not change

    def test_process_command(self):
        """Test if the car processes commands correctly."""
        self.car.process_command('F', 5, 5)  # Move forward in a 5x5 grid
        self.assertEqual(self.car.x, 0)
        self.assertEqual(self.car.y, 1)

        # Rotate right and move forward
        self.car.process_command('R', 5, 5)
        self.car.process_command('F', 5, 5)
        self.assertEqual(self.car.x, 1)
        self.assertEqual(self.car.y, 1)

    def test_process_multiple_commands(self):
        """Test if the car processes multiple commands correctly."""
        self.car.process_command('F', 5, 5)  # Move forward (0, 0) -> (0, 1)
        self.car.process_command('R', 5, 5)  # Rotate right (North -> East)
        self.car.process_command('F', 5, 5)  # Move forward (0, 1) -> (1, 1)
        self.car.process_command('R', 5, 5)  # Rotate right (East -> South)
        self.car.process_command('F', 5, 5)  # Move forward (1, 1) -> (1, 0)

        self.assertEqual(self.car.x, 1)  # x should be 1
        self.assertEqual(self.car.y, 0)  # y should be 0


class TestSimulation(unittest.TestCase):
    def setUp(self):
        """Set up the initial conditions for the simulation."""
        self.simulation = Simulation(5, 5)  # Create a 5x5 grid
        # Add cars to both lists using both methods
        self.simulation.add_car("Car1", 0, 0, 'N', ['F', 'R', 'F'])
        self.simulation.add_car_original("Car1", 0, 0, 'N', ['F', 'R', 'F'])
        self.simulation.add_car("Car2", 1, 0, 'E', ['F', 'R', 'F'])
        self.simulation.add_car_original("Car2", 1, 0, 'E', ['F', 'R', 'F'])

    def test_car_added_to_simulation(self):
        """Test if cars are properly added to the simulation."""
        self.assertEqual(len(self.simulation.cars), 2)  # Ensure two cars in self.cars
        self.assertEqual(len(self.simulation.cars_original), 2)  # Ensure two cars in self.cars_original

    def test_run_simulation_no_collision(self):
        """Test if the simulation runs without collision."""
        self.simulation.run()

        # Assert no cars have collided
        self.assertFalse(self.simulation.cars[0].collided)
        self.assertFalse(self.simulation.cars[1].collided)

    def test_run_simulation_with_collision(self):
        """Test if the simulation handles collisions correctly."""

        # Clear previous cars if any
        self.simulation.reset()

        # Adding cars so that they collide:
        # Car3: starts at (0,1), moves North to (0,2)
        self.simulation.add_car("Car3", 0, 1, 'N', ['F'])
        # Car4: starts at (0,3), moves South to (0,2)
        self.simulation.add_car("Car4", 0, 3, 'S', ['F'])

        self.simulation.run()

        # Check if both cars have been marked as collided.
        self.assertTrue(self.simulation.cars[0].collided)
        self.assertTrue(self.simulation.cars[1].collided)

    def test_reset_simulation(self):
        """Test if the reset method clears cars."""
        self.simulation.reset()
        self.assertEqual(len(self.simulation.cars), 0)
        self.assertEqual(len(self.simulation.cars_original), 0)


class TestValidInput(unittest.TestCase):
    def test_get_valid_input_valid(self):
        """Test valid input for car setup."""
        # Mocking user input for car setup
        user_input = "1 1 N"
        with unittest.mock.patch('builtins.input', return_value=user_input):
            x, y, direction = ValidInput.get_valid_input("TestCar", 5, 5)
            self.assertEqual(x, 1)
            self.assertEqual(y, 1)
            self.assertEqual(direction, 'N')

    # highlight   CTRL / for    block comment / uncomment
    @patch('builtins.input')
    def test_get_valid_input_invalid_then_valid(self, mock_input):
        """Test invalid input for car setup followed by valid input on second try."""

        # Set up side_effect to return different values on each call
        # First input is invalid, second input is valid
        mock_input.side_effect = ["10 10 N", "3 3 N"]

        # First input is invalid, should raise ValueError
        with self.assertRaises(ValueError):
            ValidInput.get_valid_input("TestCar", 5, 5)  # 5x5 grid, invalid position

        # Second input is valid, should return valid coordinates
        x, y, direction = ValidInput.get_valid_input("TestCar", 5, 5)  # 5x5 grid, valid position

        self.assertEqual(x, 3)
        self.assertEqual(y, 3)
        self.assertEqual(direction, 'N')


    @patch('builtins.input')
    def test_get_valid_input_loop(self, mock_input):
        """Test that get_valid_input eventually returns a valid input after several invalid ones."""

        # Create a sequence of inputs—any number of invalid ones, then a valid one.
        # In this example, the first four inputs are invalid, and the fifth is valid.
        inputs = [
            "10 10 N",  # invalid: coordinates out-of-bounds for a 5x5 grid
            "19 19 N",  # invalid: coordinates out-of-bounds
            "abc 2 N",  # invalid: non-numeric x-coordinate
            "2 2 X",  # invalid: direction "X" is not allowed
            "3 3 N"  # valid input for a 5x5 grid
        ]
        mock_input.side_effect = inputs

        # Loop until valid input is returned.
        while True:
            try:
                x, y, direction = ValidInput.get_valid_input("TestCar", 5, 5)
                break  # valid input obtained, exit loop
            except ValueError:
                # The function is expected to raise ValueError for invalid input.
                # We simply let the loop continue until valid input is provided.
                continue

        # Verify that we got the valid input from the side_effect.
        self.assertEqual(x, 3)
        self.assertEqual(y, 3)
        self.assertEqual(direction, 'N')

        # Optionally, verify that input() was called the expected number of times.
        # Here, we expect all inputs to have been consumed.
        self.assertEqual(mock_input.call_count, len(inputs))


if __name__ == "__main__":
    unittest.main()
