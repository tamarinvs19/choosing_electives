function changeKind(kindId, electiveId) {
    $.post(electivesChangeKindURL,
        {'kind_id': kindId, 'elective_id': electiveId, 'csrfmiddlewaretoken': csrftoken},
        function(data) {
            $(`#statistic-${electiveId}-${kindId}`)[0].innerHTML = data['students_count'][false];
            $(`#statistic-potential-${electiveId}-${kindId}`)[0].innerHTML = data['students_count'][true];
            if (data['move'] !== null && data['other_language_kind'] !== null) {
                $(`#statistic-${electiveId}-${data['other_language_kind']}`)[0].innerHTML = data['other_kind_counts'][false];
                $(`#statistic-potential-${electiveId}-${data['other_language_kind']}`)[0].innerHTML = data['other_kind_counts'][true];
                $(`#${data['other_short_name']}`)[0].checked = false;
            }
            if (data['move'] === false) {
                for (let kind of data['current_short_names']) {
                    let checkbox = $(`#${kind[0]}`);
                    checkbox.prop('checked', true);
                }
                for (let kind of data['current_unused_names']) {
                    let checkbox = $(`#${kind}`);
                    checkbox.prop('checked', false);
                }
            }
            $(`.info-counter`).innerText = data['students_count'][true];
            if (data['student_name'] !== null) {
                let kindBox = $(`.kind-box-${data['user_id']}`);
                if (kindBox.length === 0) {
                    let studentList = $(`.students-list`);
                    studentList.append(
                        `<li class="list-group-item"> ${data['student_name']} <div class='kind-box kind-box-${data['user_id']}'</div></li>`
                    );
                    kindBox = $(`.kind-box-${data['user_id']}`);
                }
                kindBox.empty();
                for (let kind of data['current_short_names']) {
                    let newKind;
                    if (kind[1] === true) {
                        newKind = `<div class='elective-kind elective-kind-${data["user_id"]} applied-application'>${kind[0]}</div>`;
                    } else {
                        newKind = `<div class='elective-kind elective-kind-${data["user_id"]}'>${kind[0]}</div>`;
                    }
                    kindBox.append(newKind);
                }
            }
        });
}
