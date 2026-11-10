from datetime import datetime
import wetterdaten
from util import *
import wetter_diagram_temperature


def fetch_weather_and_save(date: datetime = get_default_issue_date_time()) -> str:
    """ Fetches the weather data for the given date and saves it to a tex file.
        @return: Filename of the saved tex file."""
    # Hole Wetter für heute und morgen
    weather = wetterdaten.get_data_for_day(date)

    # alles zu float machen
    weather = wetterdaten.make_all_float(weather)

    # min. und max. Temp. aller Tage für Diagramm-Y-Achse ermitteln
    tmin, tmax = wetterdaten.getMinMax(weather, 'id_temp_hourly_mean')
    pmin, pmax = wetterdaten.getMinMax(weather, 'id_precip_hourly_total')
    p10min, p10max = wetterdaten.getMinMax(weather, 'id_precip_hourly_quant10')
    p90min, p90max = wetterdaten.getMinMax(weather, 'id_precip_hourly_quant90')
    pmax = max(pmax, p10max, p90max, 5)  # don't zoom too much

    folder = getCreateFolderFromDate(date)
    weather_filename = os.path.join(folder, "wetter.tex")
    with open(weather_filename, "w", encoding="utf-8") as f:
        f.write(f"\\section{{Wetter}}\n")
        for day in weather:
            d = weather[day]
            f.write(
                f"\\textbf{{{day}}} {d['id_symbol']}, min. {d['id_temp_min'][0]}°C, max. {d['id_temp_max'][0]}°C, Niederschlag {d['id_niederschlag'][0]}mm\\\\ \n\n")
            image_tex = wetter_diagram_temperature.generate_tikz(d['id_temp_hourly_mean'], tmin, tmax,
                                                                 d['id_precip_hourly_total'], pmax,
                                                                 d['id_precip_hourly_quant10'],
                                                                 d['id_precip_hourly_quant90'])
            f.write(image_tex + "\n")
        f.write(
            " (Quelle: \\href{https://www.meteoschweiz.admin.ch/service-und-publikationen/service.html}{MeteoSchweiz})\n")
    return weather_filename

