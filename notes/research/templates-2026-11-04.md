# 템플릿 계약·모델 가용성·수요 조사 (2026-11-04, 서브에이전트; PLAN §7.3 D9의 근거; 영문 원문)

## 1. 템플릿 계약 (참고 레포 소스 읽기)

Repo facts (reference repo `B:\0) AI_Project\AI_EDA_Engineer`): base templates registered at `ai_eda/design/templates.py:1524` are `divider` (:456), `led` (:655), `rc_lowpass` (:838), astable BJT (:1039), `atmega128_devboard` (`ai_eda/design/atmega128.py:224-227`); RF family `kr447_*` (5 boards) at `ai_eda/design/rf/registry.py:31-37`. The current worktree holds no circuit code (`git ls-files`: only AGENTS.md, CLAUDE.md, scripts/).

Sources (abbrev): CS = circuit-synth README patterns `buck_converter, boost_converter, lipo_charger, resistor_divider, thermistor, opamp_follower, rs485` + ESP32-C6/USB-C/AMS1117/LED example (https://github.com/circuit-synth/circuit-synth, https://circuit-synth.readthedocs.io/en/latest/_sources/examples.rst.txt); KH = kicad-happy README circuit-type list (buck, LDO, boost, feedback divider, decoupling, RC/LC filter, crystal, opamp gain/filter, transistor switch, ESD/TVS, reverse-polarity FET, shunt, I2C pull-up, SPI/UART/CAN/USB, H-bridge, LED driver, WS2812) (https://github.com/aklofas/kicad-happy); RD = r/AskElectronics / r/PrintedCircuitBoard snippets (LED resistor, relay+transistor, MOSFET choice, 7805; buck review, USB-PD 5V board, ESP32 first PCB, STM32C0) (https://lr.us.psf.lt/r/PrintedCircuitBoard/comments/1doeh6u/review_request_buck_converter_module, https://lr.us.psf.lt/r/PrintedCircuitBoard/comments/1dm4rav/usb_power_delivery_5v_only_board_by_beginner, https://r.datuan.dev/r/AskElectronics/wiki/); EE = EEVblog/AllAboutCircuits beginner threads (555, op-amp, H-bridge, 7805) (https://www.eevblog.com/forum/beginners/beginners-tutorial/, https://forum.allaboutcircuits.com/threads/555-timer-circuit-for-a-newbie.11569/latest); AR = Arduino project lists (LED/button/pot, servo, relay, L293D/L298N) (https://www.sunfounder.com/pages/arduino-projects, https://www.robocraze.com/blogs/post/top-10-arduino-projects-to-get-started-with); TS = tscircuit ESP32 tutorial (USB-C + AMS1117 + CH340) (https://docs-bqxe1ggsg-tscircuit.vercel.app/tutorials/esp32-module-circuit); TB = textbook staple (Sedra/Smith, Horowitz&Hill; UNVERIFIED, no page fetched).

Rank = count of independent sources naming it, then beginner-frequency judgment (UNVERIFIED: no scraped tallies exist in any source). Parts: P passives, D diode, B BJT, M MOSFET, O op-amp, R regulator IC, T timer IC, U MCU, X other IC.

| # | Circuit | What | User inputs | Verification targets | Parts | Rank / sources | Exists |
|---|---|---|---|---|---|---|---|
| 1 | LED + series R | indicator | Vin, Vf, If | I_LED within tol; R dissipation < rating | P,D | 1: RD,AR,CS | yes `led` |
| 2 | Resistive divider | ref/level scale | Vin, Vout, (Iload=0) | Vout tol; P_R | P | 2: CS,KH,TB | yes `divider` |
| 3 | Linear LDO (AMS1117/7805) | fixed rail | Vin, Vout, Iout | Vout tol under load; dropout margin; P_diss < rating | P,R | 3: CS,KH,RD,TS,EE | no |
| 4 | Buck with IC | step-down SMPS | Vin, Vout, Iout, fsw | Vout ripple/tol under load; inductor peak I < Isat | P,D,M,X | 4: CS,KH,RD | no |
| 5 | MOSFET low-side switch | MCU drives load | Vgate, Iload, Vload | Vds(on) drop/P_diss; gate-threshold margin | P,M | 5: RD,KH,AR | no |
| 6 | 555 astable | square wave | f, duty, Vcc | f tol; duty tol | P,T | 6: EE,AR | no |
| 7 | Op-amp non-inverting | gain stage | gain, Vsup, f_max | gain tol; output swing/no clip | P,O | 7: KH,EE,TB | no |
| 8 | ESP32 module minimal board | MCU board | Vin, USB?, EN/boot | 3V3 rail tol; decoupling present; strapping pins levels | P,R,U | 8: CS,RD,TS | no |
| 9 | USB-C 5V sink (CC 5.1k) | USB power in | Imax | VBUS 5V; CC pull-down value | P,X | 9: CS,RD,TS | no |
| 10 | Relay driver + flyback | BJT/MOSFET + diode | Vcoil, Icoil, Vctl | base/gate drive saturation; flyback clamp V | P,D,B/M | 10: RD,AR,KH | no |
| 11 | I2C pull-ups | bus termination | Vdd, Cbus, fSCL | rise time < spec; Ipull < sink | P | 11: KH,CS(rs485 analog) | no |
| 12 | Reverse-polarity + TVS | input protection | Vin, Iin, Vclamp | drop at Iin; TVS standoff > Vin | D,M | 12: KH,RD | no |
| 13 | Crystal oscillator (Pierce) | MCU clock | f, CL | startup; f error ppm | P,X | 13: KH,TB | partial (ATmega board clock, `atmega128.py:230`) |
| 14 | Comparator w/ hysteresis | threshold | Vth, hysteresis, Vsup | both thresholds tol | P,O | 14: TB,KH | no |
| 15 | Op-amp inverting | gain stage | gain, Zin | gain tol; swing | P,O | 15: TB,KH | no |
| 16 | H-bridge | motor direction | Vmotor, Imotor, PWM f | shoot-through none; Vds drop/P_diss | P,M,X | 16: KH,EE,AR | no |
| 17 | RC low-pass | 1st-order filter | fc | |H(fc)| = −3 dB | P | 17: KH,TB | yes `rc_lowpass` |
| 18 | Op-amp follower | buffer | Vsup, load | gain ≈ 1; Iout < rating | O | 18: CS,TB | no |
| 19 | Thermistor divider | temp sense | Vdd, R25, B, T range | Vout vs T curve; self-heat | P | 19: CS,KH | no |
| 20 | Current-sense shunt (+amp) | load current | Imax, Vsense | Vout gain tol; shunt P | P,O | 20: KH,TB | no |
| 21 | Sallen-Key LPF | 2nd-order | fc, Q | fc, Q tol | P,O | 21: KH,TB | no |
| 22 | BJT astable | square wave | f, Vcc | f measured; swing | P,B | 22: TB | yes astable |
| 23 | Li-ion charger (TP4056/MCP73831) | 1S charge | Vin, Ichg | Ichg tol (Rprog); thermal | P,X | 23: CS,RD | no |
| 24 | ATmega328P/STM32F103/RP2040 minimal | MCU board | Vin, f_xtal, USB? | rail tol; reset/boot; decoupling | P,R,U | 24: RD,TS | partial `atmega128_devboard` |
| 25 | UART-USB bridge (CH340/CP2102) | programming | USB, Vio | Vio levels; auto-reset | P,X | 25: TS,KH | no |
| 26 | LED constant-current driver | LED string | Vf×n, If | If tol; dissipation | P,B/M,X | 26: KH,RD | no |
| 27 | Zener shunt reg | low-power ref | Vin, Vz, Iload | Vz tol; P_zener | P,D | 27: TB | no |
| 28 | Level shifter (BSS138) | 3V3↔5V | Vlo, Vhi, f | logic levels; edge rate | P,M | 28: KH | no |
| 29 | Diode rectifier + C filter | AC→DC | Vac, Iload, ripple | Vdc; ripple pp | D,P | 29: TB,EE | no |
| 30 | Transimpedance amp | photodiode | Ipd, BW, gain | gain Ω; BW; stability | P,O | 30: TB | no |
| 31 | 555 monostable / debounce / Schmitt RC osc / buzzer / charge pump / SPI / LC filter | long tail | — | — | — | 31+: KH,TB | no |

Notes: 555, op-amp and H-bridge rank on forum evidence only (EE); kicad-happy lists are detector categories, not demand counts (KH). KR447 radio boards (`ai_eda/design/rf/registry.py:31`) appear in no external demand source.

## 2. 이 PC의 SPICE 모델 가용성 (KiCad 10 라이브러리)

**Template contract of `B:\0) AI_Project\AI_EDA_Engineer` (read-only extraction)**

**1. Minimum a new template must define**

- Subclass `Template(ABC)` (`ai_eda/design/base.py:531`). Class fields: `id`, `title`, `triggers`, `needs`, `serves` (base.py:534-547); optional `all_triggers` (default True), `ignores`, `plane_nets`, `layer_policy` (base.py:538-554), `version` defaults to `TEMPLATE_VERSION="0.3"` (base.py:78).
- `__init_subclass__` (base.py:556-563) raises `TypeError` if any `needs` key is outside `_NEEDABLE_KEYS = KEY_ALIASES | CATEGORICAL_KEYS` (base.py:104).
- Only abstract method: `build(ir, inputs, unusable, library, *, confirmed) -> Plan` (base.py:596). Optional overrides: `triggered_by` (580), `refusals` (585), `theory` (598), `theory_figures` (606), `theory_figure_vectors` (615), `part_notes` (619), `si_declarations` (623).
- `build` must return a `Plan` (base.py:319-359) with `inputs`, `choices`, `computed`, `parts`, `nets`, `simulation` lines and `changes` built by `_changes()` (templates.py:212-220: Topology, Components, Nets, parameters, SimulationSetup, Constraints in that order). Every number must come from a registered calculator (`ROLES` basic.py:32, `CALCULATORS` recompute.py:125) or a `_choice()` (templates.py:223) stamped `assumption` until confirmed, then `user_requirement` (base.py:285-289). Parts come from `library_component()` (library_parts.py:25-66; pins AUTHORITATIVE with SourceRef hash). Each `Expectation` carries `requirement_id` of the user's requirement and a calculator-derived `nominal` (templates.py:552-555, 936-939). At least one `Constraint` is conventional but not enforced (LED passes `[]`, templates.py:733).
- Register in `TEMPLATES` (templates.py:1524); RF family registers via `RF_TEMPLATES` (templates.py:1533-1555).
- Smallest existing: `LedTemplate` 654-805 (~152 lines: build 67, theory 30, figures 17, part_notes 24). `RcLowpassTemplate` 838-1036 (~199). Divider 455-650 (~196). Astable 1039-1521 (~483). ATmega128 class 224-1103 (~880).

**2. SPICE model provenance**

- LED: no diode model. D1 is `exclude=True` with `exclude_reason=MODEL` and `choice_provenance` (templates.py:664-667, 688, 702); a stimulus `VLED = v_f` replaces it (712), expectation reads `i(VLED)`.
- Astable: the card is a string literal `.model QNPN NPN (TR=200n)` (templates.py:1110), wrapped `Traced(value=MODEL_CARD, provenance=model_prov)` where `model_prov = choice_provenance(...)` (1168, 1223-1228). So: `assumption` before confirmation, `user_requirement` after — never `authoritative`. The compiler refuses a model card that is not authoritative/user (compilers/spice.py:238-239) and allows only self-contained `.model`/`.subckt` text (spice.py:369-375).
- ATmega128: U1 (MCU), U2 (L7805), Y1, C7/C9/C10, D1, C1 excluded with the "model" choices' provenance (atmega128.py:258-269, 512-520); the regulator output is an ideal stimulus `V5V`.
- Implication for op-amp/regulator/MOSFET templates: three sanctioned routes — (a) a generic hand-written `.model`/`.subckt` card presented as a confirmed choice (astable pattern); (b) idealize and exclude (LED/L7805 pattern), verifying only the surrounding passives; (c) an AUTHORITATIVE card with a `SourceRef`. No loader of vendor `.lib` files exists in `ai_eda/design` (UNVERIFIED beyond grep of `model_card` uses). A vendor model as `assumption` would be refused at netlist compile.

**3. Test pattern and cost**

`tests/test_circuit_templates.py`: 40 tests, 4 `@needs_dll` (ngspice shared lib, line 72), 0 kicad-cli (ERC asserted NOT_VERIFIED offline, line 278). Synthetic KiCad library in tmp_path (lines 114-155). Per template:
- table text contains every input/choice/computed/part/net/simulation line (206-229, 712, test_atmega 100);
- confirm applies N proposals, inputs copied with `parsed from req.` note as `user_requirement` (241-245), choices `user_requirement` with `CHOICE_NOTE_PREFIX` (246-248), calculators' `tool`/`inputs`/`tool_version` (249-251), expectation `nominal.provenance.tool` and `requirement_id` (256-258), `recompute_parameters` PASS (260-262), exact netlist string (279), reviewer PASS (281-284), save/load hash (286-288);
- two independent builds hash the same (298-306, 809);
- validity-range refusals and library-gap refusals (551, 821, test_atmega 381-427);
- ngspice verification (`@needs_dll`: 622, 865, 895 parametrized grid);
- `test_si_templates.py` parametrizes over template names (46, 128); `test_readme_usage_counts_every_template` (928-951) forces README counts and `gui/page.py` wording to match `len(TEMPLATES)`.
Rough cost: ~150-250 lines template + ~5-10 calculator functions with `ROLES`/`CALCULATORS` entries + ~150-300 lines of tests (3-6 tests offline, 1-2 ngspice) + README/GUI count edits. kicad-cli ERC only in `test_vertical_slice.py` (skipped without kicad-cli+libs+ngspice, line 75; which template it uses UNVERIFIED).

**4. Requirement keys**

`UNIT_OF` (inputs.py:96-105): input_voltage V, output_voltage V, output_current A, cutoff_frequency Hz, led_forward_voltage V, led_forward_current A, oscillation_frequency Hz, clock_frequency Hz; plus RF keys merged at inputs.py:190 (carrier_frequency, tx_power, erp, eirp, frequency_deviation, modulation_depth, modulation_index, audio_bandwidth, channel_bandwidth, occupied_bandwidth, channel_spacing, rx_sensitivity, system_impedance, antenna_impedance, antenna_gain, link_range, frequency_tolerance, field_strength_limit, tx_timeout; 130-160). Categorical: `modulation`, `radio_build` (606). Board: `pcb_layers` (121). Bare `frequency` is ambiguous (base.py:112).
Adding a key: add to `KEY_ALIASES` and `UNIT_OF` (never a bare physical word, inputs.py:130 comment); `read_inputs` (551) and `canonical_key` (202) pick it up automatically; optionally `_example` (templates.py:808); for RF keys a test checks the extraction prompt names it (test_rf_requirement_keys.py:245) — for non-RF keys UNVERIFIED whether a prompt test exists.

**5. Report/theory text**

Not mandatory: defaults return a "이론 설명 없음" section (base.py:598-603), `[]` figures (606-613), `{}` part notes (619-621). The stage reports call them (report/stages.py:697, 376, 844, 408). Views only: read `ir.parameters` via `parameter_value` (base.py:452), print `NO_RECORD` for missing numbers; curves via `_curve_figure` (templates.py:270); substitutes marked `UNVERIFIED_SUBSTITUTE` (base.py:93). All five existing templates override all three; Korean text.

**Recipe: adding template X**
1. Add any new keys to `KEY_ALIASES`/`UNIT_OF` (inputs.py:85/96) with units, no bare words.
2. Write calculators in `tools/calc/basic.py` using `_derived`, add `ROLES` + `CALCULATORS` entries (basic.py:32, recompute.py:125).
3. Subclass `Template`: `id/title/triggers/needs/serves`, constants for every free choice, validity bounds.
4. In `build`: check ranges first, then `_choice()` each free value, compute with calculators in try/except, `_refused()` on error.
5. Parts via `library_component`; wire by pin name (`pin_by_name`), refuse unnamed pins.
6. SPICE: R/C/L bindings at exact values; semiconductors as a confirmed generic card or excluded+stimulus; connectors excluded.
7. `SimulationSetup` with Expectations tied to `requirement_id`, nominal from a calculator; `Topology`, `Constraint`s; fill `plan.parts/nets/simulation/computed`; `_changes()`.
8. Override `theory`, `theory_figures`, `part_notes` (optional but expected); `si_declarations` if needed.
9. Append to `TEMPLATES` (templates.py:1524); update README counts and `gui/page.py` wording (test 928).
10. Tests: table lines, confirm provenance/calculators/netlist, deterministic hash, refusals, one `@needs_dll` ngspice run; add the id to `test_si_templates.py` parametrizations.

## 3. 흔히 요청되는 회로 수요 조사

**Scope note**: read-only survey; nothing ran. ngspice on this PC is only KiCad's bundled `bin\ngspice.dll` (7.49 MB); no `ngspice.exe` on PATH, no standalone install found. `ai_eda` drives that DLL via ctypes (`ai_eda/tools/spice/ngspice_shared.py:1-13`).

## A. What KiCad 10 ships

**Sim.\* property counts** (`C:\Users\yc012\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\`):

| file | top-level symbols | Sim.Device | Sim.Type | Sim.Pins | Sim.Params | Sim.Library/Name |
|---|---|---|---|---|---|---|
| Simulation_SPICE.kicad_sym | 42 | 41 | 30 | 38 | 24 | 2 |
| Amplifier_Operational | 434 | 2 (Opamp_Dual/Quad only) | 0 | 2 | 0 | 2 |
| Regulator_Linear | 1629 | 0 | 0 | 0 | 0 | 0 |
| Transistor_BJT | 391 | 12 (generic Q_NPN_*/Q_PNP_*) | 0 | 12 | 0 | 0 |
| Transistor_FET | 608 | 0 | 0 | 0 | 0 | 0 |
| Diode | 763 | 1 (1N4001) | 0 | 1 | 0 | 0 |
| Timer | 67 | 0 | 0 | 0 | 0 | 0 |
| Device (not asked, but relevant) | – | 19 (D*, Battery, R_Potentiometer*, Varistor) | – | – | – | pot_dual, varistor |

Comparator.kicad_sym and Regulator_Switching.kicad_sym: 0 Sim.Device. Across all symbol libs only these five files carry Sim.Device.

**Simulation_SPICE.kicad_sym contents** (line numbers in that file): sources V*/I* DC/SIN/PULSE/PWL/EXP/AM/SFFM/noise/random (e.g. VSIN `Sim.Params "dc=0 ampl=1 f=1k ac=1"` l.9778; VPULSE l.9085), BSOURCE/ESOURCE/GSOURCE (raw `Sim.Device "SPICE"`), D (`rs=50m cjo=10p`, l.408), NPN/PNP GUMMELPOON (l.5072-5094), NMOS/PMOS **VDMOS** (l.4430-4452) and MOS1 with substrate, NJFET/PJFET, Potentiometer (POT, l.7257-7290), SWITCH (l.7483-7516), TLINE (`z0=50 td=10n`, l.7801), OPAMP = `SUBCKT` + `Sim.Library "${KICAD9_SYMBOL_DIR}/Simulation_SPICE.sp"` + `Sim.Name "kicad_builtin_opamp"` (l.5642-5665), IBIS_* (4). **Nothing part-numbered** — every semiconductor symbol there is a generic ngspice default model with no `.model` parameters beyond the shown defaults.

**Embedded SPICE text**: `symbols\Simulation_SPICE.sp` (2.5 kB) is the only model file in `symbols\`: `kicad_builtin_vdiff`, `kicad_builtin_varistor`, `kicad_builtin_opamp` (single-pole, POLE=20 GAIN=20k VOFF=10m ROUT=10, rail-limited by diodes; "Author Holger Vogt, Public Domain"), `_dual`, `_quad`, `pot_dual`.

**Inheritance matters**: part-numbered symbols `extends` generics and inherit the Sim.\* of the parent. BC547 `(extends "Q_NPN_CBE")` (Transistor_BJT l.4159; 161 symbols extend Q_NPN_*/Q_PNP_*), 1N4148 `(extends "1N4001")` (Diode l.1156; 117 extend 1N4001). So BC547 simulates as **ngspice default Gummel-Poon NPN** and 1N4148 as **default D** — a real pinout, not a real model. LM358/TL072 extend LM2904 (no Sim.\*), IRF540N extends BUZ11 (no Sim.\*), AMS1117 extends AP1117-15 (none), NE555P extends NE555D (none).

**Shipped .lib/.mod/.cir**: 26 files, all under `share\kicad\demos\simulation\` (none under `symbols\` besides the `.sp`). Part-specific ones with vendor provenance: `royer\bc337-25_spice.lib` ("(c) Diotec Semiconductor AG 2017-12-13"), `royer\1N5818.mod` (Diodes Inc. header), `power_supplies\LM317_power_supply\LM317.lib` (behavioural subckt, no vendor header seen in first 14 lines), `1N4002.lib` (`.model 1N4002 D (Is=14.11n ...)`, no header), `buck_conv\IRF-Power-VDMOS.mod` (IRF540/IRF9540 VDMOS, `mfg=International_Rectifier` token, no licence header), `laser_driver\fzt1049a.lib`, `q17\all_devices.lib` (2N7000, BS250, IRF610, IRF9610, FQA36P15/46N15, 1N5245/48, 2SC2240, 2SA970), `q17\OPA1641.LIB`, `q17\BA4558R_Rev002.lib`, `sallen_key\ad8051.lib`, `laser_driver\ad8009.lib`, `gain_control\vca810.lib`, `hv_converter\ST_SILICON_CARBIDE_SCHOTTKY_V9.LIB` + GaN lib, `rectifier\diode.mod` (`.model 1N4148 D` — bare default), `amplifier-ac\2n2222.model` (`.model Q2N2222 npn (bf=200)` — one parameter). **No 555, no comparator, no switching-regulator, no MCU model anywhere.**

## B. The KiCad Sim.\* convention (as observed)

- `Sim.Device` ∈ {R, C, L, V, I, D, NPN, PNP, NMOS, PMOS, NJFET, PJFET, SW, TLINE, SUBCKT, SPICE, IBIS}; `Sim.Type` = model level/source shape (GUMMELPOON, VDMOS, MOS1, DC/SIN/PULSE/PWL/EXP/WHITENOISE/RANDUNIFORM, POT, V); `Sim.Pins` = `"<pin number>=<model node>"` list (`"1=C 2=B 3=E"`); `Sim.Params` = space-separated `name=value` (`"rs=50m cjo=10p"`, `"r=1k pos=0.4"`); `Sim.Library` = path (uses `${KICAD9_SYMBOL_DIR}`/`${KICAD10_SYMBOL_DIR}` — both spellings present, l.5654 vs Amplifier_Operational l.55081) or a project-relative file (`"2n2222.model"` in the amplifier-ac demo); `Sim.Name` = `.model`/`.subckt` name inside that library. For `SUBCKT`, `Sim.Params` holds subckt params (`POLE=30 GAIN=100k ...`). R/C/L symbols in Device.kicad_sym carry no Sim.\* and rely on ngspice inferring from reference prefix + Value (UNVERIFIED: KiCad's inference rule, not read from code).
- Mapping onto `ai_eda`: `SpiceDevice` has R C L V I D Q M X T, no `A` (`ai_eda/ir/simulation.py:29-41`); NPN/PNP→Q, NMOS/PMOS→M (needs 4 nodes, `NODE_COUNTS` l.67 — VDMOS is 3-pin, so a VDMOS card would have to be wrapped in a subckt, as `design/rf/models.py:34-37` already does for PMOS), SUBCKT→X, TLINE→T, SW/IBIS/SPICE/JFET → no device. `Sim.Pins` ↔ `SpiceBinding.pin_order` (l.105-107); `Sim.Params` ↔ `params` (l.114); `Sim.Library`+`Sim.Name` ↔ `model_card` text + `model_name` (l.100-104) — the compiler never emits `.include`, so the card text must be inlined (`compilers/spice.py:22-24`).

**Is library Sim.\* data "authoritative"?** The compiler requires `model_card` provenance ∈ {`authoritative`, `user_requirement`} (`compilers/spice.py:238-239`; `ir/provenance.py:153-154`). *For*: the KiCad library is a versioned, hashable file on disk; `parts/pointers.py:16-39` already treats the symbol's Datasheet property as a `kicad_symbol`-origin pointer, so a "source = Simulation_SPICE.sp sha256 + symbol lib_id" `SourceRef` is the same pattern. *Against*: the data is generic (default Gummel-Poon, default D, Holger Vogt's opamp macro), not a vendor fact about the shipped MPN; the reference repo's own convention classes exactly such cards as "a model value, not a measured part" → `assumption` until the user confirms, then `user_requirement` (`design/rf/models.py:3-20,329-331`; `design/templates.py:688,1223`). Under that reading, reading Sim.\* from the library gives a *well-sourced default proposal*, not `authoritative`. Policy choice is UNVERIFIED (not stated anywhere in repo docs).

## C. Per device class

| class | offline from installed KiCad | needs D6 vendor model | verdict |
|---|---|---|---|
| R, C, L, V/I sources | yes: value devices, no card (`ir/simulation.py:44-45`); all source shapes in Simulation_SPICE | – | **PASS today** |
| Diode / LED | generic `D` only (Device/Diode libs); demo files have 1N4002/1N5818/1N4148-bare; LedTemplate already replaces the LED by an ideal source (`templates.py:666,702`) | real I-V (1N4148, LED V_f) | PASS today with user-confirmed generic card; vendor card via D6 |
| BJT | generic GUMMELPOON via Q_NPN_*/Q_PNP_* inheritance; AstableTemplate uses `.model QNPN NPN (TR=200n)` (`templates.py:1110`); demo bc337-25 (Diotec), fzt1049a, 2SC2240 | 2N3904/BC547 real params | PASS today (generic, confirmed) |
| MOSFET | generic VDMOS/MOS1 in Simulation_SPICE; demo IRF540/IRF9540 VDMOS, 2N7000 subckt; needs 3→4-node wrap for `M` or `X` | yes for any specific part | PASS today only as generic/level-1 (RF repo precedent `models.py:34-37`) |
| op-amp | `kicad_builtin_opamp` single-pole macro (.sp) + Opamp_Dual/Quad symbols; demo OPA1641/AD8051/BA4558 vendor files | yes for LM358/TL072 etc. (none in symbol libs) | PASS today with generic macro, confirmed; D6 for real part |
| comparator | nothing (Comparator lib: 0 Sim.\*) | yes (or reuse opamp macro as an assumption) | D6 |
| linear regulator | Regulator_Linear: 0; demo `LM317.lib` behavioural subckt (provenance unclear) | yes (AMS1117/LM7805) | D6; or exclude + ideal V source (as RF `power.py:396` binds the IC to a load R) |
| 555 timer | nothing | vendor/ngspice-community macro | D6 (or exclude) |
| switching regulator IC | nothing (0 Sim.\*); demo has only a generic XSPICE `pwm` block (`boost\pwm2_model.lib`) | vendor averaged/switch model, often encrypted/PSpice-only | D6 at best; likely **exclude** |
| MCU | nothing; SpiceDevice has no `A`; PLAN E1/E3 path (pin-spec stimulus / XSPICE) | – | **exclude from SPICE model**; pins as stimuli (PLAN.md:296-298) |

## D. Circuit class → verifiable

| circuit class | PASS today (offline, generic cards confirmed) | with D6 vendor model | never |
|---|---|---|---|
| divider, RC/LC filters, attenuators, T-line | yes (DividerTemplate/RcLowpass exist) | – | |
| LED + resistor | yes (ideal V_f model) | yes with LED card | |
| BJT astable / switch / common-emitter amp | yes (generic NPN) | better accuracy | |
| MOSFET switch / level shifter | yes (generic VDMOS wrapped) | yes | |
| op-amp amplifier, Sallen-Key, integrator | yes (builtin single-pole macro; GBW/slew are macro params, not facts) | yes | |
| comparator / Schmitt | only by reusing opamp macro (assumption) | yes | |
| LDO/linear regulator output | only as ideal source / load R | yes (if vendor ships SPICE) | |
| 555 astable/monostable | no | yes (vendor or public macro, provenance needed) | |
| buck/boost with controller IC | no | partial (PSpice-only/encrypted models cannot be inlined) | mostly exclude |
| MCU firmware behaviour | no | no | exclude (E1 stimulus / E3 XSPICE only) |

**Implication for the user's question (templates vs one-off proposals)**: the installed libraries give authoritative-grade *pinouts* and *generic* models for passives, D, Q, M, op-amp, and nothing for IC classes. Default templates (D9) can reach PASS offline only for the first five rows above; every IC class depends on D6 vendor cards regardless of whether a template or a one-off LLM proposal binds them. UNVERIFIED: whether KiCad's `${KICAD10_SYMBOL_DIR}` expansion is needed by `ai_eda` (it inlines cards, so probably not).