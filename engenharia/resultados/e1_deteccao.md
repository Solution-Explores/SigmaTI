| cenario | detector | taxa_deteccao | atraso_medio_amostras | atraso_dp | falsos_positivos_por_serie | f1_medio |
|---|---|---|---|---|---|---|
| degrau | EWMA(a=0.1,k=4) | 1.0 | 0.0 | 0.0 | 1.37 | 0.908 |
| degrau | MAD(w=60,k=5) | 1.0 | 0.0 | 0.0 | 0.23 | 0.998 |
| pico | EWMA(a=0.1,k=4) | 1.0 | 0.0 | 0.0 | 1.9 | 0.783 |
| pico | MAD(w=60,k=5) | 1.0 | 0.0 | 0.0 | 0.2 | 0.971 |
| deriva | EWMA(a=0.1,k=4) | 0.2 | 12.5 | 5.86 | 52.07 | 0.002 |
| deriva | MAD(w=60,k=5) | 0.167 | 17.6 | 4.93 | 0.3 | 0.005 |
