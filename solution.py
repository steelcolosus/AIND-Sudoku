assignments = []


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'

#Inverted columns to cross with rows for diagonals
cols_inv = cols[::-1]

boxes = cross(rows, cols)
row_units    = [cross(row, cols) for row in rows]
column_units = [cross(rows, col) for col in cols]
square_units = [cross(sqr_row, sqr_col) for sqr_row in ('ABC', 'DEF', 'GHI') for sqr_col in ('123', '456', '789')]

diagonal1_units = [[rows[x]+cols[x] for x in range(len(cols))]]
diagonal2_units = [[rows[x]+cols_inv[x] for x in range(len(cols))]]

#Adding diagonals as a new scenario
unitlist = row_units + column_units + square_units + diagonal1_units + diagonal2_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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
    pair_values = []
    for box in values.keys():
        if len(values[box]==2):
            pair_values.append(values[box])


    
    # Eliminate the naked twins as possibilities for their peers



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
    labels = [box for box in values.keys() if len(values[box]) == 1]
    for box in labels:
        box_value = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(box_value, ''))
    return values

def only_choice(values):
    posibilities = '123456789'
    for unit in unitlist:
        for posibility in posibilities:
            count = 0
            value = ''
            for box in unit:
                if posibility in values[box]:
                    count += 1
                    if count == 1:
                        value = box
            if count == 1:
                values = assign_value(values, value, posibility)

    return values

def reduce_puzzle(values):
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
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
