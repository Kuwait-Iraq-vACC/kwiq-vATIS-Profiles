# kwiq-vATIS-Profiles

vATIS profiles for the Kuwait & Iraq vACC. They update automatically: import a profile once and vATIS installs new versions every time it starts.

> Requires **vATIS 4.1.0-beta.21 or newer**. The profiles use conditional messages, regex patterns, digit formatting (`{wind_spd:#}`, `{temp:#}`) and trend templates, which older versions don't support.

## Install

1. Download the profile you need (right-click the link, then **Save link as**):
   - **OKAC – Kuwait**: [`OKAC/OKAC.json`](https://raw.githubusercontent.com/Kuwait-Iraq-vACC/kwiq-vATIS-Profiles/refs/heads/main/OKAC/OKAC.json)
   - **ORBB – Baghdad**: [`ORBB/ORBB.json`](https://raw.githubusercontent.com/Kuwait-Iraq-vACC/kwiq-vATIS-Profiles/refs/heads/main/ORBB/ORBB.json)
2. In vATIS, open **Profiles → Import** and select the file.
3. That's it. Later changes merged into `main` are installed the next time vATIS starts.

## Stations

| Profile | ICAO | Airport | ATIS freq | Presets |
|-|-|-|-|-|
| OKAC | OKKK | Kuwait International | 126.225 | 34 ARR / 33L DEP, 16 ARR / 15R DEP, SRO 34 / 16 / 33L / 15R, dual 34/33L, dual 16/15R |
| OKAC | OKAS | Ali Al Salem | 133.000 | 30L / 12R, ILS or RNAV |
| ORBB | ORBI | Baghdad International | 126.925 | Modes A–D |
| ORBB | ORER | Erbil International | 130.400 | 36, 18, LVP 18 |
| ORBB | ORMM | Basra International | 124.525 | 32, 14 |
| ORBB | ORNI | Al Najaf International | 123.900 | Modes A–B |

## OKKK matches the real D-ATIS

The OKKK text ATIS copies the real Kuwait D-ATIS (ACARS uplinks archived on [airframes.io](https://app.airframes.io/messages/historical?text=OKKK+ARR) and [atis.guru](https://atis.guru/atis/OKKK)). Real broadcast:

```
OKKK ARR ATIS B
0852Z ARR RWY34 DEP RWY33L TRL FL150
WIND 010/11KT CAVOK T41 DP11 QNH 1010HPA
NOSIG
CONFIRM ATIS B
```

The OKKK presets are built to produce exactly this from the same METAR. The one known difference: visibility below 9999 is shown as METAR digits (`VIS 8000`) where the real D-ATIS writes `VIS 8KM`, because vATIS has no option for that.

## ORBB uses a standard ICAO layout

Iraq has no real-world D-ATIS, so ORBI, ORER, ORMM and ORNI follow the ICAO Doc 4444 (6.5) element order, written in the same style as the real Saudi (OERK, OEJN, OEDF) and Kuwait D-ATIS:

```
ORBI ATIS INFO K 0300Z
EXPECT ILS APCH RWY33R OR RNP APCH RWY33L
DEP RWY33R OR RWY33L
TRL FL160
WIND 140/12KT
VIS 4000M DU
CLD SCT 4000 BKN 10000 CB
T22 DP09
QNH 1004HPA
TEMPO 3000 TSRA
CONFIRM ATIS K
```

Airport conditions and NOTAMs go on their own lines after the transition level.

The transition level follows AIP Iraq ENR 1.7: TA 14 000 ft, **TL FL160, or FL170 when QNH is below 980 hPa**, for the whole Baghdad FIR.

## OKKK automatic messages

These messages switch on and off by themselves. Leave them ticked.

| Message | Shown when |
|-|-|
| `ATC CLEARANCE WITH GND 121.7` | A Kuwait Ground is online and Delivery is not (`OKKK_*GND NOT OKKK_*DEL`) |
| `ATC CLEARANCE WITH TWR FREQ 118.3` | Tower is online and neither Delivery nor Ground is |
| `LOW VISIBILITY PROCEDURES IN OPERATION` | RVR < 550 m, visibility < 800 m or ceiling < 200 ft (all stations) |

Real-world NOTAMs that come up often, such as `V4 CLOSED DUE TO MAINTENANCE` and the nightly `RWY 33L/15R CLOSED FROM 1700 UTC UNTIL 0100 UTC`, are ready to tick in the NOTAMs list. The 33L/15R closure only shows between 1700Z and 0100Z.

## Contributing

1. Edit the profile in vATIS and export it, or edit the JSON directly.
2. Replace the file at the same path (`OKAC/OKAC.json` or `ORBB/ORBB.json`). Don't rename or move the files, because existing installs update from those URLs.
3. Open a pull request. The **Validate Profiles** check catches duplicate preset ordinals, unknown template variables, broken conditions and bad regex patterns. You can run it locally with `python .github/scripts/validate.py`.
4. Don't touch `updateSerial`. After merge, the **Update JSON Serial** workflow bumps it, and that is what makes vATIS pick up the update.
