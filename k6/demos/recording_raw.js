// Creator: Chrome DevTools 128.0.0.0

import { sleep, group } from 'k6'
import http from 'k6/http'

export const options = {}

export default function main() {
  let response

  group('page_1 - QuickPizza - Fresh Pizza Ordering', function () {
    response = http.get('https://quickpizza.grafana.com/', {
      headers: {
        Accept: 'text/html,application/xhtml+xml',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      },
    })

    response = http.get('https://www.google-analytics.com/analytics.js', {
      headers: {
        Accept: '*/*',
      },
    })

    response = http.post(
      'https://quickpizza.grafana.com/api/pizza',
      '{"maxCalories":800,"isVegetarian":false}',
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.EXPIRED_RECORDED_TOKEN',
        },
      }
    )
  })

  // Automatically added sleep
  sleep(1)
}
