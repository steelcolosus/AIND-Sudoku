assignments = []


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
row_units = [cross(row, cols) for row in rows]
column_units = [cross(rows, col) for col in cols]
square_units = [cross(sqr_row, sqr_col) for sqr_row in ('ABC', 'DEF', 'GHI') for sqr_col in ('123', '456', '789')]

diagonal1_units = [[rows[x] + cols[x] for x in range(len(cols))]]
diagonal2_units = [[rows[x] + cols[-x - 1] for x in range(len(cols))]]

# Adding diagonals as a new scenario
unitlist = row_units + column_units + square_units + diagonal1_units + diagonal2_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins

    # Get all possible pair boxes with the same value and assign the unit to it
    possible_naked_twins = []
    for unit in unitlist:
        possible_naked_twins += [[[box1, box2], unit] for box1 in unit \
                                 for box2 in unit \
                                 if box1 != box2 \
                                 and len(values[box1]) == 2 and len(values[box2]) == 2 \
                                 and values[box1] == values[box2]]
    # Get all naked twins
    # for each naked twin value as key of the dictionary add the affected units to a list
    naked_twins_dic = {}
    for possible_naked_twin, unit in possible_naked_twins:
        for possible_naked_twin2, unit2 in possible_naked_twins:
            value = values[possible_naked_twin2[0]]
            twin_unit = naked_twins_dic.get(value)
            if twin_unit == None:
                naked_twins_dic[value] = [unit2]
            elif unit2 not in twin_unit:
                naked_twins_dic[value] = twin_unit + [unit2]

    # Eliminate naked twins
    for naked_value, units in naked_twins_dic.items():
        for unit in units:
            for box in unit:
                if naked_value != values[box]:
                    for digit in naked_value:
                        values = assign_value(values, box, values[box].replace(digit, ''))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    start_value = '123456789'
    new_grid = []
    for v in grid:
        if v == ".":
            new_grid.append(start_value)
        elif v in start_value:
            new_grid.append(v)
    assert len(new_grid) == 81
    return dict(zip(boxes, new_grid))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    :param values:  Sudoku in dictionary form.
    :return: Resulting Sudoku in dictionary form after eliminating values.
    """
    labels = [box for box in values.keys() if len(values[box]) == 1]
    for box in labels:
        box_value = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(box_value, ''))
    return values


def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    :param values: Sudoku in dictionary form.
    :return: Resulting Sudoku in dictionary form after filling in only choices.
    """
    possibilities = '123456789'
    for unit in unitlist:
        for possibility in possibilities:
            count = 0
            value = ''
            for box in unit:
                if possibility in values[box]:
                    count += 1
                    if count == 1:
                        value = box
            if count == 1:
                values = assign_value(values, value, possibility)

    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    :param values :A sudoku in dictionary form.
    :return: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Eliminate Strategy
        values = eliminate(values)
        # Only Choice Strategy
        values = only_choice(values)
        # Naked twins strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[b]) == 1 for b in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    min_length = 9
    min_box = ''

    for b in boxes:
        if len(values[b]) > 1:
            current_length = len(values[b])
            if current_length < min_length:
                min_length = current_length
                min_box = b

    min_box_values = values[min_box]

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!

    for value in min_box_values:
        sudoku_branch = values.copy()
        sudoku_branch[min_box] = value
        solved = search(sudoku_branch)
        if solved:
            return solved


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)

    values = search(values)

    return values


if __name__ == '__main__':

    """
        values = {"G7": "1569", "G6": "134568", "G5": "13568", "G4": "134568", "G3":
            "2", "G2": "34589", "G1": "7", "G9": "5689", "G8": "15", "C9": "56",
                  "C8": "3", "C3": "7", "C2": "1245689", "C1": "1245689", "C7": "2456",
                  "C6": "1245689", "C5": "12568", "C4": "1245689", "E5": "4", "E4":
                      "135689", "F1": "1234589", "F2": "12345789", "F3": "34589", "F4":
                      "123589", "F5": "12358", "F6": "123589", "F7": "14579", "F8": "6",
                  "F9": "3579", "B4": "1234567", "B5": "123567", "B6": "123456", "B7":
                      "8", "B1": "123456", "B2": "123456", "B3": "345", "B8": "9", "B9":
                      "567", "I9": "578", "I8": "27", "I1": "458", "I3": "6", "I2": "458",
                  "I5": "9", "I4": "124578", "I7": "3", "I6": "12458", "A1": "2345689",
                  "A3": "34589", "A2": "2345689", "E9": "2", "A4": "23456789", "A7":
                      "24567", "A6": "2345689", "A9": "1", "A8": "4", "E7": "159", "E6":
                      "7", "E1": "135689", "E3": "3589", "E2": "135689", "E8": "15", "A5":
                      "235678", "H8": "27", "H9": "4", "H2": "3589", "H3": "1", "H1":
                      "3589", "H6": "23568", "H7": "25679", "H4": "235678", "H5": "235678",
                  "D8": "8", "D9": "3579", "D6": "123569", "D7": "14579", "D4":
                      "123569", "D5": "12356", "D2": "12345679", "D3": "3459", "D1":
                      "1234569"}

        display(values)

        values = naked_twins(values)
        print("==============================================================================================")
        display(values)
        """

    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = "9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................"
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
