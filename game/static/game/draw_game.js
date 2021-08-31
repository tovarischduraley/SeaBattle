function change_field(x, y, state) {
    ws.send(JSON.stringify({
        'message': {
            'x': x,
            'y': y,
            'state': state,
        },
        'commands': ['change_state']
    }))
}

function can_be_placed(ship, my_bf) {
    // if (ship.is_rotated){
    //
    // }
    console.log(ship.x, ship.y, ship.length)
}

function draw_ships(not_placed_ships, my_bf) {
    let id_counter = 0
    for (let i = 0; i < 4; i++) {
        for (let j = 0; j < not_placed_ships[i]; j++) {
            ship = document.createElement("table");
            ship.className = 'ship';
            ship.id = id_counter
            tr = document.createElement('tr');
            ship.appendChild(tr)
            ships.appendChild(ship);
            len_counter = 0
            for (let k = 0; k < i + 1; k++) {
                len_counter++
                let cell = document.createElement('td');
                cell.className = 'cell ship__not__shoted';
                tr.appendChild(cell);
            }
            ship.length = len_counter


            ship.onclick = function () {
                newShip = new Ship(this.id, this.length)

                $('.my_bf').off('click').on('click', function () {
                    let row = $(this).closest('tr').index();
                    let col = $(this).index()
                    newShip.x = col
                    newShip.y = row

                    can_be_placed(newShip, my_bf)
                })

                $('.my_bf').off('mouseover').on('mouseover', function () {
                    let row = $(this).closest('tr').index();
                    let col = $(this).index()
                    if (newShip.is_rotated) {
                        for (let i = 0; i < newShip.length; i++) {
                            try {
                                get_cell(row + i, col).style.backgroundColor = 'lightgoldenrodyellow'
                            } catch (e) {
                                return;
                            }
                        }

                    } else {
                        for (let i = 0; i < newShip.length; i++) {
                            try {
                                get_cell(row, col + i).style.backgroundColor = 'lightgoldenrodyellow'
                            } catch (e) {
                                return;
                            }
                        }
                    }
                });

                $('.my_bf').off('mouseout').on('mouseout', function () {
                    let row = $(this).closest('tr').index();
                    let col = $(this).index()
                    if (newShip.is_rotated) {
                        for (let i = 0; i < newShip.length; i++) {
                            try {
                                get_cell(row + i, col).style.backgroundColor = 'cadetblue'
                            } catch (e) {
                                return;
                            }
                        }
                    } else {
                        for (let i = 0; i < newShip.length; i++) {
                            try {
                                get_cell(row, col + i).style.backgroundColor = 'cadetblue'

                            } catch (e) {
                                return;
                            }
                        }
                    }
                })
            }


            id_counter++
        }
    }
}

function get_cell(row, col) {
    return my_field.getElementsByTagName('tr')[row].getElementsByTagName('td')[col]
}

function Ship(id, length) {
    this.id = id
    this.length = length
    this.is_rotated = false
    this.x = null
    this.y = null
}


function draw_my_bf(my_bf) {
    for (let i = 0; i < 10; i++) {
        let tr = document.createElement("tr")
        my_field.appendChild(tr);
        for (let j = 0; j < 10; j++) {
            let cell = document.createElement("td");
            $(cell).click(function () {
                let $this = $(this);
                let col = $this.index();
                let row = $this.closest('tr').index()
                change_field(row, col, "SHIP_SHOTED");
            })
            switch (my_bf[i][j]) {
                case 'EMPTY_NOT_SHOTED':
                    cell.className = 'cell my_bf';
                    break;

                case 'EMPTY_SHOTED':
                    cell.className = 'cell empty__shoted';
                    break;

                case 'SHIP_NOT_SHOTED':
                    cell.className = 'cell ship__not__shoted';
                    break;

                case 'SHIP_SHOTED':
                    cell.className = 'cell ship__shoted';
                    break;

                case 'SHIP_DEAD':
                    cell.className = 'cell ship__dead';
                    break;
            }
            tr.appendChild(cell);


        }
    }
}

function draw_enemy_bf(enemy_bf) {
    for (let i = 0; i < 10; i++) {
        let tr = document.createElement("tr");
        enemy_field.appendChild(tr);
        for (let j = 0; j < 10; j++) {
            let cell = document.createElement("td");
            switch (enemy_bf[i][j]) {
                case 'EMPTY_NOT_SHOTED':
                    cell.className = 'cell';
                    break;
                case 'EMPTY_SHOTED':
                    cell.className = 'cell empty__shoted';
                    break;

                case 'SHIP_NOT_SHOTED':
                    cell.className = 'cell';
                    break;

                case 'SHIP_SHOTED':
                    cell.className = 'cell ship__shoted';
                    break;

                case 'SHIP_DEAD':
                    cell.className = 'cell ship__dead';
                    break;
            }
            tr.appendChild(cell);
        }
    }
}