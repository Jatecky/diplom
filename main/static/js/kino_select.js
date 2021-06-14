const select_kino = document.getElementById('select_kino_');

if(select_kino) {
    const films = document.getElementById('films_select');
    if(films) {
        select_kino.addEventListener('change', function() {
            var req = new XMLHttpRequest();
            req.onload = function() {
                if(this.status === 200 && this.responseText.search('error_007') == -1) {
                    json_data = JSON.parse(this.responseText);
                    const frameMap = document.getElementById('map_');
                    if(frameMap) {
                        frameMap.src = json_data.map;
                    }
                    films.innerHTML = json_data.html;
                    updateWindows(true);
                    updateVars();
                    updateWindows();
                }
            };
            req.open('GET', 'films?id=' + select_kino.value.toString(), true);
            req.send();
        });
    }
}