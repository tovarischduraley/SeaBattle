// x, y onhover
// onClick
// onHover
//             cell.addEventListener("click", () => {
//                 onClick(i, j, bf[i][j])
//             })

function draw_my_bf(bf, onClick, onHover) {
    for (let i = 0; i < 10; i++) {
        let tr = document.createElement("tr")
        my_field.appendChild(tr);
        for (let j = 0; j < 10; j++) {
            let cell = document.createElement("td")
            switch (my_bf[i][j]) {
                case 'EMPTY_NOT_SHOTED':
                    cell.className = 'cell'
                    break;

                case 'EMPTY_SHOTED':
                    cell.className = 'cell empty__shoted'
                    break

                case 'SHIP_NOT_SHOTED':
                    cell.className = 'cell ship__not__shoted'
                    break

                case 'SHIP_SHOTED':
                    cell.className = 'cell ship__shoted'
                    break

                case 'SHIP_DEAD':
                    cell.className = 'cell ship__dead'
                    break
            }
            tr.appendChild(cell)
        }
    }
}

function draw_opponent_bf(bf){

}