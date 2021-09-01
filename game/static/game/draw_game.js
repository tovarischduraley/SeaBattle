function draw_ships(not_placed_ships, my_bf) {
    document.getElementById('ships').innerHTML = ''
    for (let i = 0; i < 4; i++) {
        for (let j = 0; j < not_placed_ships[i]; j++) {
            ship = document.createElement("table");
            ship.className = 'ship';
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
                let newShip = new Ship(this.length)

                $('.my_bf').off('click').on('click', function () {

                    document.onkeypress = function () {}

                    newShip.x = $(this).closest('tr').index();
                    newShip.y = $(this).index()
                    if (!newShip.is_rotated) {
                        for (let i = 0; i < newShip.length; i++) {
                            my_bf[newShip.x][newShip.y + i] = 'SHIP_NOT_SHOTED'
                        }
                    } else {
                        for (let i = 0; i < newShip.length; i++) {
                            my_bf[newShip.x + i][newShip.y] = 'SHIP_NOT_SHOTED'
                        }
                    }
                    ws.send(JSON.stringify({
                        "commands": ["place_ship"],
                        "message":
                            {
                                "my_bf": my_bf,
                                "placed_ship_len": newShip.length
                            }
                    }))

                })

                $('.my_bf').off('mouseover').on('mouseover', function () {
                    newShip.y = $(this).closest('tr').index();
                    newShip.x = $(this).index()
                    draw(newShip)
                });

                $('.my_bf').off('mouseout').on('mouseout', function () {
                    newShip.y = $(this).closest('tr').index();
                    newShip.x = $(this).index()
                    redraw(newShip)
                })

                document.onkeypress = function (event) {
                    event.preventDefault();
                    if (event.code === 'KeyR') {
                        redraw(newShip)
                        newShip.is_rotated = !newShip.is_rotated
                        draw(newShip)
                    }
                }
            }
        }
    }
}

function can_be_placed(ship, my_bf) {

}

function draw(newShip) {
    if (newShip.is_rotated) {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.y + newShip.length - 1 > 9) {
                if (newShip.y + i < 10) {
                    get_cell(newShip.y + i, newShip.x).style.backgroundColor = 'darkred'
                }
            } else {
                get_cell(newShip.y + i, newShip.x).style.backgroundColor = 'lightgoldenrodyellow'
            }
        }

    } else {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.x + newShip.length - 1 > 9) {
                if (newShip.x + i < 10) {
                    get_cell(newShip.y, newShip.x + i).style.backgroundColor = 'darkred'
                }
            } else {
                get_cell(newShip.y, newShip.x + i).style.backgroundColor = 'lightgoldenrodyellow'
            }
        }
    }
}

function redraw(newShip) {
    if (newShip.is_rotated) {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.y + i > 9) break;
            get_cell(newShip.y + i, newShip.x).style.backgroundColor = ''
        }
    } else {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.x + i > 9) break;
            get_cell(newShip.y, newShip.x + i).style.backgroundColor = ''
        }
    }
}

function get_cell(row, col) {
    return my_field.getElementsByTagName('tr')[row].getElementsByTagName('td')[col]
}

function Ship(length) {
    this.length = length
    this.is_rotated = false
    this.x = null
    this.y = null
}

function draw_my_bf(my_bf) {
    document.getElementById('my_field').innerHTML = ''
    for (let i = 0; i < 10; i++) {
        let tr = document.createElement("tr")
        my_field.appendChild(tr);
        for (let j = 0; j < 10; j++) {
            let cell = document.createElement("td");
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
    document.getElementById('enemy_field').innerHTML = ''

    for (let i = 0; i < 10; i++) {
        let tr = document.createElement("tr");
        enemy_field.appendChild(tr);
        for (let j = 0; j < 10; j++) {
            let cell = document.createElement("td");
            switch (enemy_bf[i][j]) {
                case 'EMPTY_NOT_SHOTED':
                    cell.className = 'cell op_bf';
                    break;
                case 'EMPTY_SHOTED':
                    cell.className = 'cell empty__shoted';
                    break;

                case 'SHIP_NOT_SHOTED':
                    cell.className = 'cell op_bf';
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