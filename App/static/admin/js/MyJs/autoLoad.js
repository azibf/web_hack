

function GetAdminData(admin, token) {
    fetch(`/api/GetAdminData/${admin}/${token}`)
        .then(function (response) {
            return response.json();
        }).then(function (text) {
        text = text.status;
        console.log(text);
    });
}