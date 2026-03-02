#!/usr/bin/env python3
"""
QSL Card Generator - генератор QSL карточек подтверждения радиосвязи
Поддержка нескольких QSO на одной карточке
"""

from datetime import datetime
import os
import webbrowser


def generate_qsl_html(my_call: str, qso_list: list) -> str:
    """Генерирует HTML код QSL карточки с несколькими QSO"""

    # Генерируем строки таблицы для каждого QSO
    qso_rows = ""
    for i, qso in enumerate(qso_list, 1):
        sat_name = qso.get('sat_name', '') or '-'
        prop_mode = qso.get('prop_mode', '') or '-'
        my_callsign = qso.get('my_callsign', '') or '-'
        my_gridsquare = qso.get('my_gridsquare', '') or '-'
        qso_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td class="their-call">{qso['their_call'].upper()}</td>
                        <td>{qso['date']}</td>
                        <td>{qso['time']}</td>
                        <td>{qso['band']}</td>
                        <td>{qso['mode'].upper()}</td>
                        <td>{qso['rst']}</td>
                        <td>{prop_mode}</td>
                        <td>{sat_name}</td>
                        <td>{my_callsign}</td>
                        <td>{my_gridsquare}</td>
                    </tr>"""

    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QSL Card - {my_call}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .card-container {{
            perspective: 1000px;
        }}

        .qsl-card {{
            width: 850px;
            background: linear-gradient(145deg, #ffffff 0%, #f0f0f0 100%);
            border-radius: 20px;
            box-shadow:
                0 25px 50px rgba(0, 0, 0, 0.3),
                0 0 0 3px #e94560,
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            overflow: hidden;
            position: relative;
        }}

        .card-header {{
            background: linear-gradient(90deg, #e94560 0%, #0f3460 100%);
            padding: 25px 20px;
            text-align: center;
            position: relative;
        }}

        .header-text {{
            color: rgba(255, 255, 255, 0.8);
            font-size: 11px;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: 400;
        }}

        .my-callsign {{
            font-family: 'Roboto', sans-serif;
            font-size: 36px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 3px;
        }}

        .qso-info {{
            padding: 20px;
        }}

        .qso-table {{
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .qso-table thead {{
            background: linear-gradient(90deg, #0f3460 0%, #16213e 100%);
        }}

        .qso-table th {{
            color: #fff;
            padding: 10px 6px;
            text-align: center;
            font-weight: 500;
            font-size: 9px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .qso-table th:first-child {{
            width: 30px;
        }}

        .qso-table td {{
            padding: 10px 6px;
            border-bottom: 1px solid #eee;
            font-family: 'Roboto', sans-serif;
            font-size: 11px;
            color: #333;
            font-weight: 500;
            text-align: center;
            letter-spacing: 0.5px;
        }}

        .qso-table tr:last-child td {{
            border-bottom: none;
        }}

        .qso-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .qso-table tbody tr:hover {{
            background: #e8f4f8;
        }}

        .their-call {{
            font-size: 12px !important;
            color: #e94560 !important;
            font-weight: 700 !important;
        }}

        .card-footer {{
            background: #0f3460;
            padding: 12px;
            text-align: center;
            color: #fff;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1px;
        }}

        .qso-count {{
            text-align: center;
            margin-bottom: 10px;
            color: #0f3460;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 1px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .qsl-card {{
                box-shadow: none;
                border: 2px solid #e94560;
            }}
        }}

        @media (max-width: 870px) {{
            .qsl-card {{
                width: 100%;
                max-width: 100%;
            }}
            .my-callsign {{
                font-size: 28px;
            }}
            .qso-table {{
                font-size: 8px;
            }}
            .qso-table th, .qso-table td {{
                padding: 4px 2px;
            }}
        }}
    </style>
</head>
<body>
    <div class="card-container">
        <div class="qsl-card">
            <div class="card-header">
                <div class="my-callsign">{my_call.upper()}</div>
            </div>

            <div class="qso-info">
                <div class="qso-count">Confirmed QSO: {len(qso_list)}</div>
                <table class="qso-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Call</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Band</th>
                            <th>Mode</th>
                            <th>RST</th>
                            <th>Prop.</th>
                            <th>Satellite</th>
                            <th>My Call</th>
                            <th>Gridsq</th>
                        </tr>
                    </thead>
                    <tbody>
                        {qso_rows}
                    </tbody>
                </table>
            </div>

            <div class="card-footer">
                QSL CONFIRMED — 73
            </div>
        </div>
    </div>
</body>
</html>'''

    return html


def get_user_input(prompt: str, default: str = "") -> str:
    """Получает ввод от пользователя с опциональным значением по умолчанию"""
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    return input(f"{prompt}: ").strip()


def add_qso() -> dict:
    """Запрашивает данные для одного QSO"""
    print("  --- New QSO ---")
    their_call = get_user_input("  Correspondent callsign")
    date = get_user_input("  Date (DD.MM.YYYY)", datetime.now().strftime("%d.%m.%Y"))
    time = get_user_input("  Time (HH:MM UTC)", datetime.now().strftime("%H:%M"))
    band = get_user_input("  Band (e.g. 14 MHz, 2m, 70 cm)", "14 MHz")
    mode = get_user_input("  Mode (SSB, CW, FT8, etc.)", "SSB")
    rst = get_user_input("  RST report", "59")
    prop_mode = get_user_input("  Propagation mode (e.g. ES, F2, Tropo, Aer) - leave empty if normal", "")
    sat_name = get_user_input("  Satellite name (e.g. SO-50, FO-29) - leave empty if not satellite", "")
    my_callsign = get_user_input("  Your callsign (for QSL)", "")
    my_gridsquare = get_user_input("  Your gridsquare (e.g. KO85, IO91)", "")

    return {
        'their_call': their_call,
        'date': date,
        'time': time,
        'band': band,
        'mode': mode,
        'rst': rst,
        'prop_mode': prop_mode,
        'sat_name': sat_name,
        'my_callsign': my_callsign,
        'my_gridsquare': my_gridsquare
    }


def main():
    print("=" * 50)
    print("==> QSL Card Generator (Multiple QSO) <==")
    print("=" * 50)
    print()

    # Ввод своего позывного
    my_call = get_user_input("Your callsign", "RK3A")

    qso_list = []

    # Цикл добавления QSO
    while True:
        print()
        qso = add_qso()
        qso_list.append(qso)

        print()
        more = input("Add another QSO? (y/n): ").strip().lower()
        if more not in ('y', 'yes', 'y', 'yes'):
            break

    if not qso_list:
        print("No QSO added. Exiting.")
        return

    print()
    print("==> Generating QSL card...")

    # Генерация HTML
    html_content = generate_qsl_html(my_call, qso_list)

    # Сохранение в файл
    output_file = f"qsl_{my_call.upper()}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[OK] Card saved to: {output_file}")
    print(f"[OK] Total QSO: {len(qso_list)}")
    print()

    # Открытие в браузере
    try:
        abs_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{abs_path}')
        print("[OK] Card opened in browser")
    except Exception as e:
        print(f"[!] Could not open browser: {e}")

    print()
    print("=" * 50)
    print("Card is ready!")
    print("=" * 50)


if __name__ == "__main__":
    main()
