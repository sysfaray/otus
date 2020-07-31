$('#brand').on('change', function (e) {
    var brand = e.target.value;
    $.get('/model?brand=' + brand, function (data) {
        $('#model').empty();
        $('#model').append('<option value="" disable="true" selected="true">Модель</option>');
        $('#model').append(data);
        $('#fuel').empty();
        $('#capacity').empty();
        $('#year').empty();
    });
});
$('#model').on('change', function (e) {
    var model = e.target.value;
    $.get('/fuel?model=' + model, function (data) {
        $('#fuel').empty();
        $('#fuel').append('<option value="" disable="true" selected="true">Топливо</option>');
        $('#fuel').append(data);
        $('#capacity').empty();
        $('#year').empty();
    });
});
$('#fuel').on('change', function (e) {
    var fuel = e.target.value;
    var model = $("#model").val();
    $.get('/capacity?fuel=' + fuel + '&model=' + model, function (data) {
        $('#capacity').empty();
        $('#capacity').append('<option value="" disable="true" selected="true">Объем</option>');
        $('#capacity').append(data);
        $('#year').empty();
        $('#type_work').empty();
        $('#works').empty();
    });
});
$('#capacity').on('change', function (e) {
    var capacity = e.target.value;
    var model = $("#model").val();
    var fuel = $("#fuel").val();
    var url = '/year?fuel=' + fuel + '&model=' + model + '&capacity=' + capacity
    $.ajax({
        url: url,
        type: 'GET',
        contentType: 'application/json',
        success: function (data) {
            $('#year').empty();
            $('#year').append('<option value="" disable="true" selected="true">Год</option>');
            $('#type_work').empty();
            $('#works').empty();
            $.map(data["result"]["date"], function (value) {
                window.car = data["result"]['car']
                $('#year').append($('<option>', {
                    value: value,
                    text: value
                }));
            });
        }
    });
});


$('#year').on('change', function (e) {
    var url = '/type_work_search?car=' + window.car
    $.ajax({
        url: url,
        type: 'GET',
        contentType: 'application/json',
        success: function (data) {
            $('#type_work').empty();
            $('#type_work').append('<option value="" disable="true" selected="true">Раздел</option>');
            $.each(data["result"], function (index, value) {
                window.works = data["result"]
                $('#type_work').append($('<option>', {
                    value: index,
                    text: index
                }));
            });
        }
    });
});

$('#type_work').on('change', function (e) {
    var type_work = e.target.value;
    var works = window.works;
    $('#works').empty();
    $('#works').append('<option value="" disable="true" selected="true">Работы</option>');
    $.map(works[type_work], function (value) {
        $('#works').append($('<option>', {
            value: value.id,
            text: value.name
        }));
    });
});

$('#works').on('change', function (e) {
    var work = e.target.value;
    var url = '/spares_search?id=' + work + '&car=' + window.car + "&original=" + true
    $.get(url, function (data) {
        window.data = data
        $('#result').empty();
        $('#result').append(data)
    });
});

$('#button').click(function (e) {
    var work = $("#works").val();
    var url = '/spares_search?id=' + work + '&car=' + window.car + "&original=" + true
    $.get(url, function (data) {
        window.data = data
        $('#result').empty();
        $('#result').append(data)
    });
});


$('#button2').click(function () {
    var id = window.car;
    if (id) {
    var url = '/spares_view?car=' + id
    $.get(url, function (data) {
        $('#result').empty();
        $('#result').append(data)
    });}
    else {
        alert("Выбирите модель автомобиля")
    }
});

$('#checkbox1').toggle(
    function () {
        var value = 0;
        //you can put the checkbox in a variable,
        //this way you do not need to do a javascript query every time you access the value of the checkbox
        var checkbox1 = document.getElementById("checkbox1")
        checkbox1.checked = value
        document.getElementById("checkbox1").addEventListener("change", function(element){
            var work = $("#works").val();
            console.log(checkbox1.checked)
            if (checkbox1.checked == true) {
                if (work) {
                var url = '/spares_search?id=' + work + '&car=' + window.car + "&original=" + false
                $.get(url, function (data) {
                    window.data = data
                    $('#result').empty();
                    $('#result').append(data)
                });
                }
                else {
                    checkbox1.checked = 0
                    alert("Выбирите модель автомобиля и вид работ")
                };
            }
            else {
                if (work) {
                    var url = '/spares_search?id=' + work + '&car=' + window.car + "&original=" + true
                    $.get(url, function (data) {
                    window.data = data
                    $('#result').empty();
                    $('#result').append(data)
                    })};
            };
        });
    }
);