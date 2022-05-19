function change_kind(electiveId, kindId) {
    $.post(electivesChangeKindURL,
        {'kind_id': kindId, 'elective_id': electiveId, 'csrfmiddlewaretoken': csrftoken},
        function(data) {
            $(`#statistic-${electiveId}-${kindId}`)[0].innerHTML = data['students_count'][false];
            $(`#statistic-potential-${electiveId}-${kindId}`)[0].innerHTML = data['students_count'][true];
            if (data['move'] !== null && data['other_language_kind'] !== null) {
                $(`#statistic-${electiveId}-${data['other_language_kind']}`)[0].innerHTML = data['other_kind_counts'][false];
                $(`#statistic-potential-${electiveId}-${data['other_language_kind']}`)[0].innerHTML = data['other_kind_counts'][true];
                $(`#button-${data['other_short_name']}-${electiveId}`)[0].checked = false;
            }
            const counter = $(`#row-${electiveId}`)[0];
            counter.dataset.fall = data['fall_count'];
            counter.dataset.spring = data['spring_count'];
        });
}

function switchThematic(thematic_name) {
    $.post(saveOpenedThematicURL,
        {'thematic_name': thematic_name, 'csrfmiddlewaretoken': csrftoken},
        function(data) {}
    )
}

function saveOpenedAllThematics(is_opened) {
    $.post(saveOpenedThematicURL,
        {'is_opened': is_opened, 'all': true, 'csrfmiddlewaretoken': csrftoken},
        function(data) {}
    )
}

function saveCookie(cookie_field, cookie_value) {
    $.post(saveCookieURL,
        {'cookie_field': cookie_field, 'cookie_value': cookie_value, 'csrfmiddlewaretoken': csrftoken},
        function(data) {}
    )
}

function clickSwitch(input) {
    const is_opened = input.hasAttribute('opened');
    saveOpenedAllThematics(is_opened);
    if (is_opened) {
        input.removeAttribute('opened');
        $('.accordion-collapse').removeClass('show');
        let accordionButton = $('.accordion-button')
        accordionButton.attr('aria-expanded', 'false');
        accordionButton.addClass('collapsed');
        input.innerText = gettext('Unroll');
    } else {
        input.setAttribute('opened', true);
        $('.accordion-collapse').addClass('show');
        let accordionButton = $('.accordion-button')
        accordionButton.attr('aria-expanded', 'true');
        accordionButton.removeClass('collapsed');
        input.innerText = gettext('Roll');
    }
}

function sortColumn(columnName, thematicId, direction = 1) {
    let self = $(`#sort-${columnName}-${thematicId}`)[0];
    if (self.hasAttribute('sorted')) {
        self.removeAttribute('sorted');
        $(self).prop('checked', false);
        columnName = 'title';
    } else {
        self.setAttribute('sorted', true);
    }
    if (columnName === 'title') {
        direction = -1;
    }
    const parent = $(`.thematic-${thematicId}`);
    const items = parent.children(`.row-${thematicId}`).sort(function(a, b) {
        let vA = a.dataset[columnName];
        let vB = b.dataset[columnName];
        return direction * ((vA > vB) ? -1 : (vA < vB) ? 1 : 0);
    });
    parent.append(items);
}

function filterElectives() {
    const filter = document.getElementById('filterInput').value.toLowerCase().trim();
    const parents = $('.accordion-body');
    for (let parent of parents) {
        const items = $(parent).children('.elective-row');
        items.map(function(number, elective) {
            const dataset = elective.dataset;
            let include =
                dataset['title'].toLowerCase().includes(filter) ||
                dataset['russianName'].toLowerCase().includes(filter) ||
                dataset['englishName'].toLowerCase().includes(filter) ||
                dataset['teachers'].toLowerCase().includes(filter);
            if (include) {
                $(elective).show();
            } else {
                $(elective).removeAttr("style").hide();
            }
        });
    }
}

function switchOptions() {
    let switchButton = $('#switch-button')[0];
    let searchColumn = $('.search-button-col');
    let rollColumn = $('.roll-button-col');
    if (switchButton.dataset['open'] === 'true') {
        switchButton.dataset['open'] = 'false';
        searchColumn.hide();
        rollColumn.hide();
        switchButton.setAttribute('title', gettext('Show menu'));
        saveCookie('show_menu', false);
    } else {
        switchButton.dataset['open'] = 'true';
        searchColumn.show();
        rollColumn.show();
        switchButton.setAttribute('title', gettext('Hide menu'));
        saveCookie('show_menu', true);
    }
}
