document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("id_latitude")) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById("id_latitude").value = position.coords.latitude;
                document.getElementById("id_longitude").value = position.coords.longitude;
            },
            (error) => {
                console.warn("Location access denied or unavailable");
            }
        );
    }
});
