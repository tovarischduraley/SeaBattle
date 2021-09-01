function can_be_placed(ship, my_bf) {

    // MY_BF(ROW, COL)
    // X - COL, Y - ROW
    // ----------------
    // MY_BF(Y, X)


    if (!ship.is_rotated) {
        if (ship.x + ship.length - 1 > 9) {
            return false
        }

        let start_x = ship.x
        let stop_x = ship.x + ship.length - 1

        if (start_x > 0) {
            start_x--
            if (my_bf[ship.y][start_x] === 'SHIP_NOT_SHOTED') {
                return false
            }
        }
        if (stop_x < 9) {
            stop_x++
            if (my_bf[ship.y][stop_x] === 'SHIP_NOT_SHOTED') {
                return false
            }
        }

        if (my_bf[ship.y - 1]) {
            for (let t = start_x; t <= stop_x; t++) {
                if (my_bf[ship.y - 1][t] === 'SHIP_NOT_SHOTED') {
                    return false
                }
            }
        }

        if (my_bf[ship.y + 1]) {
            for (let t = start_x; t <= stop_x; t++) {
                if (my_bf[ship.y + 1][t] === 'SHIP_NOT_SHOTED') {
                    return false
                }
            }
        }
    } else {

        if (ship.y + ship.length - 1 > 9) {
            return false
        }

        let start_y = ship.y
        let stop_y = ship.y + ship.length - 1


        if (start_y > 0) {
            start_y--
            if (my_bf[start_y][ship.x] === 'SHIP_NOT_SHOTED') {
                return false
            }
        }
        if (stop_y < 9) {
            stop_y++
            if (my_bf[stop_y][ship.x] === 'SHIP_NOT_SHOTED') {
                return false
            }
        }
        console.log(my_bf[ship.y][ship.x - 1])
        if (my_bf[ship.y][ship.x - 1]) {
            for (let j = start_y; j <= stop_y; j++) {
                if (my_bf[j][ship.x - 1] === 'SHIP_NOT_SHOTED') {
                    return false
                }
            }
        }
        if (my_bf[ship.y][ship.x + 1]) {
            for (let j = start_y; j <= stop_y; j++) {
                if (my_bf[j][ship.x + 1] === 'SHIP_NOT_SHOTED') {
                    return false
                }
            }
        }
    }
    return true
}

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
                    newShip.y = $(this).closest('tr').index();
                    newShip.x = $(this).index()

                    let cell = get_cell(newShip.x, newShip.y)

                    if (cell.style.backgroundColor !== 'darkred') {
                        document.onkeypress = function () {
                        }

                        if (newShip.is_rotated) {
                            for (let i = 0; i < newShip.length; i++) {
                                my_bf[newShip.y + i][newShip.x] = 'SHIP_NOT_SHOTED'
                            }
                        } else {
                            for (let i = 0; i < newShip.length; i++) {
                                my_bf[newShip.y][newShip.x + i] = 'SHIP_NOT_SHOTED'
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
                    }
                })

                $('.my_bf').off('mouseover').on('mouseover', function () {
                    newShip.y = $(this).closest('tr').index();
                    newShip.x = $(this).index()
                    draw(newShip, my_bf)
                    $(function () {

                        document.onkeypress = function (event) {
                            event.preventDefault();
                            if (event.code === 'KeyR') {
                                redraw(newShip)
                                newShip.is_rotated = !newShip.is_rotated
                                draw(newShip, my_bf)
                            }
                        }
                    })
                });

                $('.my_bf').off('mouseout').on('mouseout', function () {
                    newShip.y = $(this).closest('tr').index();
                    newShip.x = $(this).index()
                    redraw(newShip)
                    document.onkeypress = function (event) {
                        event.preventDefault();
                    }
                })

            }
        }
    }
}


function get_cell(col, row) {
    return my_field.getElementsByTagName('tr')[row].getElementsByTagName('td')[col]
}

function draw(newShip, my_bf) {
    let flag = can_be_placed(newShip, my_bf)
    if (!newShip.is_rotated) {
        for (let i = 0; i < newShip.length; i++) {

            if (!flag) {
                if (newShip.x + i < 10) {
                    get_cell(newShip.x + i, newShip.y).style.backgroundColor = 'darkred'
                }
            } else {
                get_cell(newShip.x + i, newShip.y).style.backgroundColor = 'lightgoldenrodyellow'
            }

        }

    } else {
        for (let i = 0; i < newShip.length; i++) {

            if (!flag) {
                if (newShip.y + i < 10) {
                    get_cell(newShip.x, newShip.y + i).style.backgroundColor = 'darkred'
                }
            } else {
                get_cell(newShip.x, newShip.y + i).style.backgroundColor = 'lightgoldenrodyellow'
            }

        }
    }
}

function redraw(newShip) {
    if (!newShip.is_rotated) {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.x + i > 9) break;
            get_cell(newShip.x + i, newShip.y).style.backgroundColor = ''
        }
    } else {
        for (let i = 0; i < newShip.length; i++) {
            if (newShip.y + i > 9) break;
            get_cell(newShip.x, newShip.y + i).style.backgroundColor = ''
        }
    }
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