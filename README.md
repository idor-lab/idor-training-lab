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
