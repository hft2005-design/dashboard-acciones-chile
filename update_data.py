# update_data.py - versión completa y corregida
import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta
import ta
import numpy as np
import time

# -------------------------------------------------------------
# LISTA DE ACCIONES (TICKER .SN -> NOMBRE EMPRESA)
# -------------------------------------------------------------
TICKERS = {
    "AGUAS-A.SN": "Aguas Andinas",
    "ANDINA-B.SN": "CCU",
    "BCI.SN": "Banco BCI",
    "BSANTANDER.SN": "Banco Santander",
    "CHILE.SN": "CMPC",
    "CAP.SN": "CAP",
    "CCU.SN": "CCU",
    "CENCOSUD.SN": "Cencosud",
    "COPEC.SN": "Empresas Copec",
    "ENELAM.SN": "Enel Américas",
    "ENELCHILE.SN": "Enel Chile",
    "ENTEL.SN": "Entel",
    "FALABELLA.SN": "Falabella",
    "IAM.SN": "IAM",
    "ITAUCL.SN": "Itaú Corpbanca",
    "LTM.SN": "Latam Airlines",
    "MALLPLAZA.SN": "Mall Plaza",
    "PARAUCO.SN": "Parque Arauco",
    "RIPLEY.SN": "Ripley",
    "SMU.SN": "SMU",
    "SONDA.SN": "Sonda",
    "SQM-B.SN": "SQM",
    "VAPORES.SN": "Vapores",
    "COLBUN.SN": "Colbún",
    "CONCHATORO.SN": "Viña Concha y Toro",
    "ECL.SN": "ECL",
    "ILC.SN": "Inversiones La Construcción",
    "QUINENCO.SN": "Quiñenco",
    "SECURITY.SN": "Grupo Security"
}

# -------------------------------------------------------------
# SECTORES PARA CADA TICKER
# -------------------------------------------------------------
SECTORES = {
    "AGUAS-A.SN": "Servicios",
    "ANDINA-B.SN": "Bebidas",
    "BCI.SN": "Financiero",
    "BSANTANDER.SN": "Financiero",
    "CHILE.SN": "Industrial",
    "CAP.SN": "Industrial",
    "CCU.SN": "Bebidas",
    "CENCOSUD.SN": "Retail",
    "COPEC.SN": "Energía",
    "ENELAM.SN": "Energía",
    "ENELCHILE.SN": "Energía",
    "ENTEL.SN": "Telecomunicaciones",
    "FALABELLA.SN": "Retail",
    "IAM.SN": "Servicios",
    "ITAUCL.SN": "Financiero",
    "LTM.SN": "Transporte",
    "MALLPLAZA.SN": "Retail",
    "PARAUCO.SN": "Retail",
    "RIPLEY.SN": "Retail",
    "SMU.SN": "Retail",
    "SONDA.SN": "Tecnología",
    "SQM-B.SN": "Minería",
    "VAPORES.SN": "Transporte",
    "COLBUN.SN": "Energía",
    "CONCHATORO.SN": "Bebidas",
    "ECL.SN": "Energía",
    "ILC.SN": "Financiero",
    "QUINENCO.SN": "Industrial",
    "SECURITY.SN": "Financiero"
}

# -------------------------------------------------------------
# FUNCIONES DE ANÁLISIS
# -------------------------------------------------------------
def get_technical_indicators(df):
    """Calcula RSI, MACD, volumen promedio, rendimientos"""
    if len(df) < 30:
        return None
    
    rsi = ta.momentum.RSIIndicator(df['Close'], window=14).rsi().iloc[-1]
    macd = ta.trend.MACD(df['Close'])
    macd_line = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    macd_hist = macd.macd_diff().iloc[-1]
    sma_20 = df['Close'].rolling(20).mean().iloc[-1]
    sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
    avg_volume = df['Volume'].rolling(20).mean().iloc[-1] if 'Volume' in df else 0
    ret_1d = (df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100 if len(df) > 1 else 0
    ret_1w = (df['Close'].iloc[-1] / df['Close'].iloc[-6] - 1) * 100 if len(df) >= 6 else 0
    ret_1m = (df['Close'].iloc[-1] / df['Close'].iloc[-22] - 1) * 100 if len(df) >= 22 else 0
    
    return {
        "rsi": round(rsi, 1),
        "macd_line": round(macd_line, 2),
        "macd_signal": round(macd_signal, 2),
        "macd_histogram": round(macd_hist, 2),
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2) if sma_50 else None,
        "avg_volume": int(avg_volume),
        "return_1d": round(ret_1d, 2),
        "return_1w": round(ret_1w, 2),
        "return_1m": round(ret_1m, 2)
    }

def get_fundamental_mock(ticker):
    """Simula ratios fundamentales (demo)"""
    base_per = {
        "CHILE.SN": 12.5, "SQM-B.SN": 8.2, "BSANTANDER.SN": 10.1,
        "ENELAM.SN": 9.7, "CENCOSUD.SN": 15.3, "CAP.SN": 6.8,
        "FALABELLA.SN": 22.4, "LTM.SN": 18.9, "PARAUCO.SN": 11.2,
        "AGUAS-A.SN": 14.3, "ANDINA-B.SN": 13.1, "BCI.SN": 9.5,
        "COPEC.SN": 11.0, "ENELCHILE.SN": 8.5, "ENTEL.SN": 16.2,
        "IAM.SN": 12.0, "ITAUCL.SN": 10.8, "MALLPLAZA.SN": 12.4,
        "RIPLEY.SN": 20.1, "SMU.SN": 18.3, "SONDA.SN": 15.7,
        "VAPORES.SN": 14.2, "COLBUN.SN": 9.9, "CONCHATORO.SN": 12.9,
        "ECL.SN": 10.2, "ILC.SN": 8.7, "QUINENCO.SN": 11.3,
        "SECURITY.SN": 9.2, "CCU.SN": 13.4
    }
    base_debt = {
        "CHILE.SN": 2.1, "SQM-B.SN": 1.2, "BSANTANDER.SN": 3.5,
        "ENELAM.SN": 2.8, "CENCOSUD.SN": 4.2, "CAP.SN": 1.9,
        "FALABELLA.SN": 5.1, "LTM.SN": 6.3, "PARAUCO.SN": 2.5,
        "AGUAS-A.SN": 1.7, "ANDINA-B.SN": 2.0, "BCI.SN": 2.9,
        "COPEC.SN": 2.3, "ENELCHILE.SN": 3.1, "ENTEL.SN": 3.8,
        "IAM.SN": 1.5, "ITAUCL.SN": 3.2, "MALLPLAZA.SN": 2.6,
        "RIPLEY.SN": 4.5, "SMU.SN": 5.0, "SONDA.SN": 2.2,
        "VAPORES.SN": 4.0, "COLBUN.SN": 2.4, "CONCHATORO.SN": 2.1,
        "ECL.SN": 1.8, "ILC.SN": 1.6, "QUINENCO.SN": 2.7,
        "SECURITY.SN": 1.9, "CCU.SN": 2.0
    }
    return {
        "pe_ratio": base_per.get(ticker, 12.0),
        "debt_to_ebitda": base_debt.get(ticker, 2.5),
        "dividend_yield": round(3.5 + np.random.uniform(-1, 1), 1)
    }

def get_sentiment_mock(ticker):
    """Mock de sentimiento de noticias (valores más variados)"""
    sent = {
        "CHILE.SN": 65, "SQM-B.SN": 85, "BSANTANDER.SN": 45,
        "ENELAM.SN": 55, "CENCOSUD.SN": 35, "CAP.SN": 50,
        "FALABELLA.SN": 25, "LTM.SN": 30, "PARAUCO.SN": 60,
        "AGUAS-A.SN": 72, "ANDINA-B.SN": 68, "BCI.SN": 55,
        "COPEC.SN": 60, "ENELCHILE.SN": 52, "ENTEL.SN": 42,
        "IAM.SN": 70, "ITAUCL.SN": 48, "MALLPLAZA.SN": 62,
        "RIPLEY.SN": 28, "SMU.SN": 32, "SONDA.SN": 55,
        "VAPORES.SN": 48, "COLBUN.SN": 56, "CONCHATORO.SN": 63,
        "ECL.SN": 55, "ILC.SN": 70, "QUINENCO.SN": 60,
        "SECURITY.SN": 58, "CCU.SN": 66
    }
    return sent.get(ticker, 50)

def generate_recommendation(tech_score, fund_score, sent_score):
    """Nuevos umbrales más flexibles"""
    final = tech_score * 0.3 + fund_score * 0.4 + sent_score * 0.3
    if final >= 55:
        rec = "COMPRAR"
        risk = "Bajo" if final >= 70 else "Medio"
    elif final >= 40:
        rec = "MANTENER"
        risk = "Medio"
    else:
        rec = "VENDER"
        risk = "Alto"
    return int(final), rec, risk

def fetch_historical_prices(ticker, days=30):
    """Devuelve lista plana de precios de cierre (últimos 'days' días)."""
    end = datetime.now()
    start = end - timedelta(days=days)
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
        if df.empty:
            return []
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
        prices = close_series.tolist()
        if prices and isinstance(prices[0], (list, np.ndarray)):
            prices = [p[0] if isinstance(p, (list, np.ndarray)) else p for p in prices]
        return prices
    except Exception as e:
        print(f"    Advertencia: no se pudieron obtener precios históricos para {ticker}: {e}")
        return []

# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------
def main():
    stocks_data = []
    historical = {}
    
    for ticker, company in TICKERS.items():
        print(f"Procesando {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if hist.empty:
                print(f"  ⚠️ Sin datos para {ticker}")
                continue
            current_price = hist['Close'].iloc[-1]
            
            full_hist = stock.history(period="3mo")
            if full_hist.empty or len(full_hist) < 30:
                print(f"  ⚠️ Pocos datos históricos para {ticker}, usando valores por defecto")
                tech_indicators = {"rsi": 50, "macd_histogram": 0, "avg_volume": 0,
                                   "return_1d": 0, "return_1w": 0, "return_1m": 0}
                tech_score = 50
            else:
                tech_indicators = get_technical_indicators(full_hist)
                # Puntaje técnico más sensible
                tech_score = 50
                if tech_indicators['rsi'] < 35:
                    tech_score += 30
                elif tech_indicators['rsi'] > 65:
                    tech_score -= 30
                if tech_indicators['macd_histogram'] > 0:
                    tech_score += 20
                else:
                    tech_score -= 15
                tech_score = max(0, min(100, tech_score))
            
            fundamental = get_fundamental_mock(ticker)
            sent_score = get_sentiment_mock(ticker)
            
            # Puntaje fundamental basado en PER (rangos)
            pe = fundamental['pe_ratio']
            if pe < 10:
                fund_score = 80
            elif pe < 15:
                fund_score = 60
            elif pe < 20:
                fund_score = 40
            else:
                fund_score = 20
            
            final_score, rec, risk = generate_recommendation(tech_score, fund_score, sent_score)
            
            if rec == "COMPRAR":
                summary = "Fundamentos sólidos, RSI favorable, tendencia alcista."
            elif rec == "MANTENER":
                summary = "Valoración justa, esperar catalizadores."
            else:
                summary = "Deterioro de márgenes, alta deuda, RSI sobrecomprado."
            
            prices_30 = fetch_historical_prices(ticker, 30)
            if prices_30:
                historical[ticker] = prices_30
            
            stocks_data.append({
                "ticker": ticker.replace(".SN", ""),
                "company": company,
                "price": round(current_price, 2),
                "recommendation": rec,
                "risk": risk,
                "score": final_score,
                "confidence": "Alto" if final_score >= 70 else "Medio" if final_score >= 40 else "Bajo",
                "sector": SECTORES.get(ticker, "Otros"),
                "summary": summary,
                "indicators": tech_indicators,
                "fundamentals": fundamental,
                "sentiment_score": sent_score
            })
            print(f"  ✅ {ticker} procesado correctamente")
        except Exception as e:
            print(f"  ❌ Error procesando {ticker}: {e}")
            continue
        time.sleep(2)   # Pausa de 2 segundos
    
    # Guardar JSON
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": stocks_data,
        "historical_prices": historical
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ data.json generado con {len(stocks_data)} acciones de {len(TICKERS)} posibles.")

if __name__ == "__main__":
    main()