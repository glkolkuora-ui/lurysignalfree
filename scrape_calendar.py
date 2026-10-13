#!/usr/bin/env python3
"""Atualiza calendar-data.json a partir do Calendário Econômico do Investing.com BR."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "calendar-data.json"
URL = "https://br.investing.com/economic-calendar/"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def scrape() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=UA, locale="pt-BR", timezone_id="America/Sao_Paulo"
        )
        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(8000)
        try:
            page.wait_for_selector('tr.datatable-v2_row__hkEus[id*="-"]', timeout=30000)
        except Exception:
            pass
        try:
            btn = page.locator("#onetrust-accept-btn-handler").first
            if btn.count():
                btn.click(timeout=2000)
                page.wait_for_timeout(1000)
        except Exception:
            pass

        events = page.evaluate(
            """() => {
          const rows = [...document.querySelectorAll('tr.datatable-v2_row__hkEus')]
            .filter(tr => tr.id && /-\\d+$/.test(tr.id));
          const day = new Intl.DateTimeFormat('en-CA', {
            timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit'
          }).format(new Date());
          return rows.map(tr => {
            const cells = [...tr.querySelectorAll('td')].map(td =>
              (td.innerText || '').trim().replace(/\\s+/g, ' ')
            );
            const linkEl = tr.querySelector('a[href*="economic-calendar"]');
            let time = (cells[1] || '00:00').split(' ').pop();
            if (!/^\\d{1,2}:\\d{2}$/.test(time)) time = '00:00';
            const [hh, mm] = time.split(':');
            const iso = `${day}T${String(hh).padStart(2,'0')}:${mm}:00-03:00`;
            const title = (linkEl?.innerText || cells[3] || '').trim();
            let impact = 'Low';
            if (/FOMC|Fed|Taxa-alvo|juros|Payroll|CPI|IPCA|PIB|GDP|NFP/i.test(title)) impact = 'High';
            else if (/MBA|Leilão|ZEW|hipotec|Emprego|CAGED|Desemprego/i.test(title)) impact = 'Medium';
            return {
              title, country: cells[2] || '—', date: iso,
              time: `${String(hh).padStart(2,'0')}:${mm}`,
              impact, actual: cells[5] || '', forecast: cells[6] || '', previous: cells[7] || '',
              link: linkEl?.href || 'https://br.investing.com/economic-calendar/'
            };
          }).filter(e => e.title);
        }"""
        )
        browser.close()
        return events


def main() -> None:
    events = scrape()
    payload = {
        "source": URL,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "events": events,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK · {len(events)} eventos → {OUT.name}")


if __name__ == "__main__":
    main()
