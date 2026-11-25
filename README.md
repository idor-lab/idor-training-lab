# IDOR Training Lab PRO

Profesionálněji uspořádaná výuková webová laboratoř pro studium IDOR/BOLA.

## Důležité zabezpečení
Aplikace obsahuje záměrně zranitelné demonstrační endpointy. Používejte ji pouze jako vlastní výukovou laboratoř s fiktivními daty. Nevkládejte skutečné osobní údaje.

Před nasazením na Render nastavte v **Environment**:
- `LAB_ACCESS_KEY` – dlouhý náhodný přístupový klíč do laboratoře. Bez něj je vstup do laboratoře uzavřen.
- `SECRET_KEY` – dlouhý náhodný tajný klíč Flask session.

Tyto hodnoty nikdy nevkládejte do GitHub zdrojového kódu.

## Spuštění na Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Runtime: Python 3

## Demo účty
Po vstupu do chráněné laboratoře jsou k dispozici fiktivní identity:
`wiener`, `carlos`, `alice`, `admin`.
Nejde o skutečné přihlašovací účty ani hesla.

## Rozsah
Všechny záměrně zranitelné cesty jsou pod `/lab/` nebo `/api/` a vyžadují nejprve přístup do chráněné laboratoře.


## Write IDOR training module
The order detail page includes a deliberately vulnerable form that sends POST requests to `/api/orders/<order_id>`. It can change the fictional order status and delivery address. The endpoint intentionally omits an object-ownership check so learners can observe a Write IDOR in Burp Repeater. Keep the service protected by a strong `LAB_ACCESS_KEY` and `SECRET_KEY`; use only fictional lab data. Do not deploy this vulnerable training app publicly without the access gate.
