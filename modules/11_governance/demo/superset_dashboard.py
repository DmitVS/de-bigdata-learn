"""Учебный дашборд Superset модуля 11: последнее звено графа lineage.

Создаёт через API Superset (идемпотентно — повторный запуск ничего не дублирует):
    подключение «Trino lake»   trino://superset@trino:8080/iceberg
    датасет                     governance_demo.mart_city_oos_daily, метрика oos_share
    чарт «Доля часов без товара по городам» и дашборд «Наличие по городам»
Сбор Superset в OpenMetadata (openmetadata/superset.yaml) свяжет дашборд с витриной.

Запуск (в make shell, нужен слой serving): python modules/11_governance/demo/superset_dashboard.py
"""

import json
import os

import requests

API = "http://superset:8088/api/v1"
DB_NAME = "Trino lake"
DASHBOARD = "Наличие по городам"
CHART = "Доля часов без товара по городам"


def session() -> requests.Session:
    s = requests.Session()
    login = s.post(
        f"{API}/security/login",
        json={
            "username": "admin",
            "password": os.environ["SUPERSET_ADMIN_PASSWORD"],
            "provider": "db",
            "refresh": True,
        },
        timeout=30,
    )
    login.raise_for_status()
    s.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
    s.headers["X-CSRFToken"] = s.get(f"{API}/security/csrf_token/", timeout=30).json()["result"]
    s.headers["Referer"] = "http://superset:8088"
    return s


def find(s: requests.Session, resource: str, column: str, value: str) -> int | None:
    q = json.dumps({"filters": [{"col": column, "opr": "eq", "value": value}]})
    rows = s.get(f"{API}/{resource}/", params={"q": q}, timeout=30).json()["result"]
    return rows[0]["id"] if rows else None


def main() -> None:
    s = session()
    db = (
        find(s, "database", "database_name", DB_NAME)
        or s.post(
            f"{API}/database/",
            json={
                "database_name": DB_NAME,
                "sqlalchemy_uri": "trino://superset@trino:8080/iceberg",
            },
            timeout=60,
        ).json()["id"]
    )

    ds = find(s, "dataset", "table_name", "mart_city_oos_daily")
    if ds is None:
        ds = s.post(
            f"{API}/dataset/",
            json={"database": db, "schema": "governance_demo", "table_name": "mart_city_oos_daily"},
            timeout=60,
        ).json()["id"]
        metrics = s.get(f"{API}/dataset/{ds}", timeout=30).json()["result"]["metrics"]
        keep = [
            {"id": m["id"], "metric_name": m["metric_name"], "expression": m["expression"]}
            for m in metrics
        ]
        s.put(
            f"{API}/dataset/{ds}",
            json={
                "metrics": keep
                + [
                    {
                        "metric_name": "oos_share",
                        "verbose_name": "Доля часов без товара",
                        "expression": "SUM(oos_hours) * 1.0 / SUM(shelf_hours)",
                        "d3format": ".1%",
                    }
                ]
            },
            timeout=60,
        ).raise_for_status()

    dash = (
        find(s, "dashboard", "dashboard_title", DASHBOARD)
        or s.post(
            f"{API}/dashboard/", json={"dashboard_title": DASHBOARD, "published": True}, timeout=30
        ).json()["id"]
    )

    chart = find(s, "chart", "slice_name", CHART)
    if chart is None:
        params = {
            "viz_type": "echarts_timeseries_bar",
            "x_axis": "city_id",
            "metrics": ["oos_share"],
            "groupby": [],
            "row_limit": 100,
        }
        chart = s.post(
            f"{API}/chart/",
            json={
                "slice_name": CHART,
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": ds,
                "datasource_type": "table",
                "params": json.dumps(params),
                "dashboards": [dash],
            },
            timeout=60,
        ).json()["id"]

    # Раскладка дашборда: без неё чарт привязан, но не показан. Сбор Superset в OpenMetadata
    # тоже берёт чарты дашборда из раскладки (position_json).
    position = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["ROW-1"], "parents": ["ROOT_ID"]},
        "ROW-1": {
            "type": "ROW",
            "id": "ROW-1",
            "children": [f"CHART-{chart}"],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        },
        f"CHART-{chart}": {
            "type": "CHART",
            "id": f"CHART-{chart}",
            "children": [],
            "parents": ["ROOT_ID", "GRID_ID", "ROW-1"],
            "meta": {"chartId": chart, "width": 12, "height": 60, "sliceName": CHART},
        },
    }
    s.put(
        f"{API}/dashboard/{dash}",
        json={"position_json": json.dumps(position)},
        timeout=60,
    ).raise_for_status()
    print(f"Superset: подключение {db}, датасет {ds}, дашборд {dash} «{DASHBOARD}»")


if __name__ == "__main__":
    main()
