function copyCodes(semester) {
    const codes = $(`.codes-${semester}`)[0].innerText;
    navigator.clipboard.writeText(codes)
        .then(() => {
            navigator.clipboard.writeText(codes);
            addToast('Copied', codes);
        })
        .catch(err => {
            console.log('Something went wrong', err);
        });
}

function changeExam(applicationId) {
    $.post(electivesChangeExamURL,
        {'student_on_elective_id': applicationId, 'csrfmiddlewaretoken': csrftoken},
        function(data) {
            if (data['OK'] === true) {
                $(`#credits-${applicationId}`)[0].innerHTML = data['credit_units'];
                updateCodes();
            } else {
                let checkbox = $(`#exam-${applicationId}`)[0];
                checkbox.checked = !checkbox.checked;
            }
            if (data['message']) {
                addToast('', data['message'])
            }
        }
    );
}

function changeKind(applicationId, kindId) {
    $.post(electivesChangeKindURL,
        {
            'student_on_elective_id': applicationId,
            'kind_id': kindId,
            'csrfmiddlewaretoken': csrftoken,
        },
        function(data) {
            if (data['OK'] === true) {
                for (let updatedApplicationId of data['all_applications']) {
                    let examTag = $(`#exam-${updatedApplicationId}`)[0];
                    $(`#kind-${updatedApplicationId}`)[0].innerHTML = data['full_kind'];
                    $(`#credits-${updatedApplicationId}`)[0].innerHTML = data['credit_units'];
                    if (updatedApplicationId === applicationId) {
                        examTag.checked = data['with_exam'];
                    }
                    examTag.disabled = data['only_without_exam'] === true || data['only_with_exam'] === true;
                    if (data['only_without_exam']) {
                        examTag.checked = false;
                    } else if (data['only_with_exam']) {
                        examTag.checked = true;
                    }
                }
                updateCodes();
            }
            if (data['message']) {
                addToast('', data['message'])
            }
        }
    );
}

function applyApplication(application, target, newIndex) {
    const applicationId = application.id.split('-')[1];
    console.log(applicationId, target, newIndex);
    $.post(electivesApplyApplicationURL,
        {
            'student_on_elective_id': applicationId,
            'target': target,
            'new_index': newIndex,
            'csrfmiddlewaretoken': csrftoken,
        },
        function(data) {
            if (data['OK'] === true) {
                if (data['semester'] === 1) {
                    $('.fall-kind').css('display', 'list-item');
                    $('.spring-kind').css('display', 'none');
                } else {
                    $('.spring-kind').css('display', 'list-item');
                    $('.fall-kind').css('display', 'none');
                }
                updateCodes();
            } else {
                return false;
            }
            if (data['message']) {
                addToast('', data['message'])
            }
        }
    );
}

function removeApplication(applicationId) {
    $.post(electivesRemoveApplicationURL,
        {
            'student_on_elective_id': applicationId,
            'csrfmiddlewaretoken': csrftoken,
        },
        function(data) {
            if (data['OK'] === true) {
                $(`#application-${applicationId}-1`).remove()
                $(`#application-${applicationId}-12`).remove()
                $(`#application-${applicationId}-2`).remove()
                updateCodes();
            }
            if (data['message']) {
                addToast('', data['message'])
            }
        }
    );
}

function updateCreditCounters(data) {
    let fallWindow = $('#fall-window')[0];
    let springWindow = $('#spring-window')[0];
    fallWindow.dataset.tooFewCredits = data['credit_units_fall']['is_too_few'];
    springWindow.dataset.tooFewCredits = data['credit_units_spring']['is_too_few'];
}

function updateCodes() {
    $.get(electivesUpdateCodesURL,
        {},
        function (data) {
            if (data['code_fall'] !== null) {
                $('.codes-fall').html(data['codes_fall']);
            }
            if (data['code_spring'] !== null) {
                $('.codes-fall').html(data['codes_spring']);
            }
            $('.fall-credits').html(data['credit_units_fall']['sum']);
            $('.spring-credits').html(data['credit_units_spring']['sum']);
            $('.potential-fall-credits').html(data['credit_units_potential_fall']['sum']);
            $('.potential-spring-credits').html(data['credit_units_potential_spring']['sum']);
            updateCreditCounters(data);
        }
    );
}

function duplicateApplication(applicationId) {
    $.post(electivesDuplicateApplicationURL,
        {
            'student_on_elective_id': applicationId,
            'csrfmiddlewaretoken': csrftoken,
        },
        function(data) {
            if (data['OK'] === true) {
                let application = data['application'];
                $(data['prev_id']).after(application);
                updateCodes();
            }
        }
    );
}
