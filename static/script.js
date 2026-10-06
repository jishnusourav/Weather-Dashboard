const weatherForm =
    document.getElementById("weatherForm");

const cityInput =
    document.getElementById("cityInput");

const weatherResult =
    document.getElementById("weatherResult");

const loading =
    document.getElementById("loading");

const errorMessage =
    document.getElementById("errorMessage");


/* ---------------------------------------
   SEARCH WEATHER
--------------------------------------- */

weatherForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const city =
            cityInput.value.trim();

        if (!city) {

            showError(
                "Please enter a city name."
            );

            return;
        }


        weatherResult.classList.add(
            "hidden"
        );

        errorMessage.classList.add(
            "hidden"
        );

        loading.classList.remove(
            "hidden"
        );


        try {

            const response =
                await fetch("/weather", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        city: city
                    })
                });


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to get weather."
                );
            }


            displayWeather(data);


        } catch (error) {

            showError(
                error.message
            );

        } finally {

            loading.classList.add(
                "hidden"
            );

        }

    }
);


/* ---------------------------------------
   DISPLAY WEATHER
--------------------------------------- */

function displayWeather(data) {

    const location =
        data.location;

    const current =
        data.current;


    /* LOCATION */

    document.getElementById(
        "cityName"
    ).textContent =
        location.city;


    let locationText =
        location.country;


    if (location.state) {

        locationText =
            location.state +
            ", " +
            location.country;

    }


    document.getElementById(
        "locationDetails"
    ).textContent =
        locationText;


    document.getElementById(
        "coordinates"
    ).textContent =
        `${location.latitude.toFixed(3)},
         ${location.longitude.toFixed(3)}`;


    /* CURRENT */

    document.getElementById(
        "weatherIcon"
    ).textContent =
        current.icon;


    document.getElementById(
        "temperature"
    ).textContent =
        roundValue(
            current.temperature
        );


    document.getElementById(
        "description"
    ).textContent =
        current.description;


    document.getElementById(
        "dataTime"
    ).textContent =
        formatDateTime(
            current.time
        );


    document.getElementById(
        "feelsLike"
    ).textContent =
        roundValue(
            current.feels_like
        );


    document.getElementById(
        "humidity"
    ).textContent =
        roundValue(
            current.humidity
        );


    document.getElementById(
        "rain"
    ).textContent =
        numberValue(
            current.rain
        );


    document.getElementById(
        "cloudCover"
    ).textContent =
        roundValue(
            current.cloud_cover
        );


    document.getElementById(
        "windSpeed"
    ).textContent =
        numberValue(
            current.wind_speed
        );


    document.getElementById(
        "windDirection"
    ).textContent =
        current.wind_direction_text;


    document.getElementById(
        "windGusts"
    ).textContent =
        numberValue(
            current.wind_gusts
        );


    /* VISIBILITY */

    const visibilityKm =
        current.visibility != null
            ? current.visibility / 1000
            : null;


    document.getElementById(
        "visibility"
    ).textContent =
        visibilityKm !== null
            ? visibilityKm.toFixed(1)
            : "--";


    /* PRESSURE */

    document.getElementById(
        "pressure"
    ).textContent =
        numberValue(
            current.pressure
        );


    /* LOCATION INFO */

    document.getElementById(
        "timezone"
    ).textContent =
        location.timezone ||
        "--";


    document.getElementById(
        "elevation"
    ).textContent =
        location.elevation != null
            ? `${Math.round(location.elevation)} m`
            : "--";


    /* TODAY */

    if (data.forecast.length > 0) {

        const today =
            data.forecast[0];


        document.getElementById(
            "todayMax"
        ).textContent =
            today.max_temp;


        document.getElementById(
            "todayMin"
        ).textContent =
            today.min_temp;


        document.getElementById(
            "sunrise"
        ).textContent =
            formatTime(
                today.sunrise
            );


        document.getElementById(
            "sunset"
        ).textContent =
            formatTime(
                today.sunset
            );

    }


    /* 7 DAY FORECAST */

    createForecast(
        data.forecast
    );


    weatherResult.classList.remove(
        "hidden"
    );

}


/* ---------------------------------------
   CREATE FORECAST
--------------------------------------- */

function createForecast(forecast) {

    const forecastContainer =
        document.getElementById(
            "forecast"
        );


    forecastContainer.innerHTML = "";


    forecast.forEach(
        function (day, index) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "forecast-card";


            const dayName =
                getDayName(
                    day.date,
                    index
                );


            card.innerHTML = `

                <div class="forecast-date">
                    ${dayName}
                </div>

                <div class="forecast-icon">
                    ${day.icon}
                </div>

                <div class="forecast-description">
                    ${day.description}
                </div>

                <div class="forecast-temp">
                    ${day.max_temp}°C
                    <span class="forecast-min">
                        ${day.min_temp}°C
                    </span>
                </div>

                <div class="forecast-rain">
                    💧 ${day.precipitation_probability}%
                </div>

                <div class="forecast-uv">
                    UV ${day.uv_index}
                </div>

            `;


            forecastContainer.appendChild(
                card
            );

        }
    );

}


/* ---------------------------------------
   DAY NAME
--------------------------------------- */

function getDayName(
    dateString,
    index
) {

    if (index === 0) {

        return "Today";

    }


    const date =
        new Date(
            dateString + "T12:00:00"
        );


    return date.toLocaleDateString(
        "en-IN",
        {
            weekday: "short"
        }
    );

}


/* ---------------------------------------
   FORMAT DATE + TIME
--------------------------------------- */

function formatDateTime(
    dateString
) {

    if (!dateString) {

        return "--";

    }


    const date =
        new Date(dateString);


    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


/* ---------------------------------------
   FORMAT TIME
--------------------------------------- */

function formatTime(
    dateString
) {

    if (!dateString) {

        return "--";

    }


    const date =
        new Date(dateString);


    return date.toLocaleTimeString(
        "en-IN",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* ---------------------------------------
   ROUND NUMBER
--------------------------------------- */

function roundValue(value) {

    if (value === null ||
        value === undefined) {

        return "--";

    }


    return Math.round(value);

}


/* ---------------------------------------
   DECIMAL NUMBER
--------------------------------------- */

function numberValue(value) {

    if (value === null ||
        value === undefined) {

        return "--";

    }


    return Number(value).toFixed(1);

}


/* ---------------------------------------
   ERROR
--------------------------------------- */

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );

    weatherResult.classList.add(
        "hidden"
    );

}