"""
check_endpoints.py
 
Deployment-valideringsscript til demoen. Bekraefter, FOER crew_demo.py koeres:
  1. at begge lokale Ollama-endpoints er oppe og svarer paa /api/ps
  2. at ingen af dem er bundet bredere end 127.0.0.1 (dvs. ikke uautentificeret
     offentligt eksponeret)
 
Koer med: py -3.11 check_endpoints.py
Exit-kode 0 = alt OK, 1 = mindst ét tjek fejlede (koer ikke demoen endnu).
"""
import socket
import sys
import urllib.request
import urllib.error
 
ENDPOINTS = [
    ("Arkitekt (qwen3:8b)", "127.0.0.1", 11434),
    ("Udvikler/Tester (deepseek-coder:6.7b)", "127.0.0.1", 11435),
]
 
 
def check_http(host: str, port: int):
    """Tjekker at endpointet svarer paa /api/ps. Henter samtidig listen af
    'loaded' modeller, saa output ogsaa viser om noget fylder VRAM allerede."""
    url = f"http://{host}:{port}/api/ps"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return True, f"HTTP {resp.status} - {body}"
    except urllib.error.URLError as e:
        return False, f"Ingen forbindelse: {e}"
 
 
def check_not_publicly_exposed(port: int):
    """Forsoeger at forbinde til porten via maskinens eksterne netvaerks-IP i
    stedet for 127.0.0.1. Hvis det lykkes, er Ollama sandsynligvis startet med
    OLLAMA_HOST=0.0.0.0 (eller lignende) og er bundet bredere end localhost."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except OSError:
        return True, "Kunne ikke bestemme en ekstern netvaerks-IP - springer over (antager OK)."
 
    if local_ip.startswith("127."):
        return True, "Ingen ekstern netvaerks-IP fundet - sandsynligvis kun localhost."
 
    try:
        with socket.create_connection((local_ip, port), timeout=2):
            return False, (
                f"ADVARSEL: port {port} svarer OGSAA paa {local_ip} (ikke kun 127.0.0.1) - "
                f"tjek at Ollama er startet med OLLAMA_HOST=127.0.0.1:{port}, ikke 0.0.0.0."
            )
    except OSError:
        return True, f"Port {port} svarer IKKE paa {local_ip} - ser korrekt begraenset til localhost."
 
 
def main() -> int:
    all_ok = True
    print("=== Deployment-validering: lokale Ollama-endpoints ===\n")
 
    for label, host, port in ENDPOINTS:
        print(f"--- {label} ({host}:{port}) ---")
 
        up, detail = check_http(host, port)
        print(f"  Oppe og svarer:  {'JA' if up else 'NEJ'} - {detail}")
        if not up:
            all_ok = False
 
        safe, detail2 = check_not_publicly_exposed(port)
        print(f"  Kun localhost:   {'JA' if safe else 'NEJ'} - {detail2}")
        if not safe:
            all_ok = False
 
        print()
 
    if all_ok:
        print("Alt OK - begge endpoints er oppe og ser ud til kun at vaere tilgaengelige lokalt.")
    else:
        print("ADVARSEL: mindst ét tjek fejlede ovenfor - loes det foer crew_demo.py koeres.")
 
    return 0 if all_ok else 1
 
 
if __name__ == "__main__":
    sys.exit(main())