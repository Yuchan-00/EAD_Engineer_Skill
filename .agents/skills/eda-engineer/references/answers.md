# Answers: templates, their inputs, control keys, scope questions

Read this when you must choose a template, type an `--answer key=value`, or answer a regulatory scope
question. Everything else: `ai-eda run --help`.

## How a template is chosen

Only confirmed numeric requirements select a template (`user_requirement` or `authoritative`; model
extractions count after `confirm_requirements=yes`). Without `--llm` the request text is not parsed, so
state the inputs as answers, with units: `--answer cutoff_frequency="1 kHz"`. Two matching templates are
refused as `ambiguous` (the message names a `leave_out` answer per template). A confirmed requirement the
chosen template does not serve is refused (closed world) with the exact remedy
`--answer leave_out=<key>`; a later typed answer to that key brings it back.

## The 13 templates (version 0.3)

| id | title | selected by (all keys present) | needs (unit) | validity bounds | the simulation verifies |
|---|---|---|---|---|---|
| divider | unloaded resistive voltage divider | input_voltage + output_voltage (and no max_voltage_drop) | input_voltage (V), output_voltage (V) | 0 < output < input; a stated output_current must be 0 A | v(VOUT) within 1 % (op) |
| led | LED indicator with series resistor | led_forward_voltage or led_forward_current | input_voltage (V), led_forward_voltage (V), led_forward_current (A) | calculator bounds only | current through an ideal constant-V_f source (the LED is not a diode model) |
| rc_lowpass | first-order RC low-pass | cutoff_frequency (and no system_impedance) | cutoff_frequency (Hz) | 2 Hz .. 100 kHz | magnitude at f_c by an ac sweep, 2 % |
| lc_lowpass | second-order LC low-pass, Butterworth, Z0-terminated | cutoff_frequency + system_impedance | cutoff_frequency (Hz), system_impedance (ohm) | 1 kHz .. 30 MHz; 10 .. 600 ohm | level at f_c relative to the passband = -3.01 dB +/- 0.2 dB |
| bjt_lowside_switch | NPN low-side switch with flyback diode | output_current + max_voltage_drop | input_voltage (V, the control level), output_voltage (V, the load supply), output_current (A), max_voltage_drop (V) | 0 < I <= 0.2 A; V_load + 1 V <= 40 V; control >= 1.2 V | ON-state collector level <= max_voltage_drop; OFF clamp <= V_load + v_f (load = constant-current sink) |
| i2c_pullup | I2C pull-up resistors | bus_capacitance + bus_rise_time | input_voltage (V), clock_frequency (Hz), bus_capacitance (F), bus_rise_time (s) | 2.5 .. 5.5 V; 1 kHz .. 5 MHz; 1 pF .. 10 nF; 10 ns .. 10 us; R_min <= R_max | held-low level and the 30 %-70 % rise of SDA (SCL and the real driver's V_OL are not verified) |
| astable | BJT astable multivibrator | oscillation_frequency | oscillation_frequency (Hz), input_voltage (V) | 3 .. 6 V; 100 Hz .. 20 kHz | measured frequency within 10 %, output swing |
| atmega128_devboard | ATmega128 development board | clock_frequency (and no bus keys) | clock_frequency (Hz), input_voltage (V) | 7 .. 15 V; 1 .. 16 MHz | LED current, reset RC delay, AVCC level; the MCU and regulator are excluded |
| kr447_audio_ptt | KR447 audio / PTT bench board | `radio_build=audio_ptt` | input_voltage (V), modulation (`fm`) | 6.6 .. 8.4 V | audio chain, PTT sequencing under confirmed model values; no IC simulated |
| kr447_rx_backend | KR447 receiver IF back-end | `radio_build=rx_backend` | modulation (`fm`), input_voltage (V) | 6.4 .. 8.4 V; 4 layers | fixture networks as "a network verdict under confirmed model values (not a measured part)" |
| kr447_rx_frontend | KR447 receiver front-end | `radio_build=rx_frontend` | carrier_frequency (Hz, a KR 447 channel), input_voltage (V) | 6.4 .. 8.4 V; 4 layers | same, plus bias points |
| kr447_tx_exciter | KR447 transmitter exciter (conducted, 50 ohm) | `radio_build=tx_exciter` | carrier_frequency (Hz), modulation (`fm`), input_voltage (V) | 6.6 .. 8.4 V; power 0.01 .. 1 W; 4 layers | same; antenna keys refused |
| kr447_transceiver | KR447 FM transceiver (antenna or conducted variant) | `radio_build=transceiver` or `transceiver_conducted` | carrier_frequency (Hz), modulation (`fm`), input_voltage (V) | 6.6 .. 8.4 V; 4 layers | same; RELEASE NOT_VERIFIED at best |

Every KR 447 MHz regulatory number in the radio templates is an UNVERIFIED placeholder; `rf.regulatory_profile`
never passes on it and KC conformity assessment is needed before any transmission. The bounds are
engineering limits the template states for its own ideal model, not measured limits of real parts.

## Input keys and units

Canonical key (unit) and the aliases the tool reads: input_voltage (V; supply_voltage, v_in, vin,
battery_voltage), output_voltage (V; v_out, vout), output_current (A; load_current, i_out),
cutoff_frequency (Hz; corner_frequency, f_c), system_impedance (ohm; rf_port_impedance),
led_forward_voltage (V; forward_voltage, v_f), led_forward_current (A; forward_current, led_current, i_f),
oscillation_frequency (Hz; output_frequency, f_osc), clock_frequency (Hz; crystal_frequency, mcu_clock),
max_voltage_drop (V; on_voltage_drop, v_ce_sat), bus_capacitance (F; line_capacitance, c_bus),
bus_rise_time (s; rise_time, t_rise), carrier_frequency (Hz), modulation (categorical: `fm` for the radio
boards), radio_build (categorical: exactly one build name), pcb_layers (2 or 4; default 2).
A bare `frequency` is read by no template; the tool asks which frequency is meant.

## Control keys (steer an agent; never a requirement)

`confirm_requirements`, `accept_implicit=k1,k2`, `reject_implicit=k3` (the LLM extraction, only with
`--llm`); `leave_out=k1,k2` (drop requirements from the design; recorded as the user's decision);
`confirm_design=yes|no`; `confirm_parts=yes|no` (candidate-parts table); `confirm_facts=yes|no`;
`datasheet_facts_file=<json>`; `extract_datasheet_facts=yes` (billed); `accept_regulations=id1,id2`,
`reject_regulations=id3`, `propose_regulations=yes` (billed); `pcb.placement=skip`, `pcb.routing=skip`,
`pcb.routing=partial`, `pcb.silkscreen=skip`.

Accepted confirmations: yes, y, ok, confirm, 네, 예, 확인, 맞습니다 and similar; no, n, cancel, 아니오
decline. A `confirm_design=yes` given together with a requirement-changing answer is ignored and the table
is shown again.

## Baseline checklist and regulatory scope

The first run asks `application` and `jurisdiction` (required); optional: `operating_temperature`,
`protection`. Regulatory scope answers (optional, recorded under category regulatory): `mains_powered`
(yes/no), `highest_rated_voltage` (e.g. `'12 V DC'`), `evaluation_kit` (yes/no), `radio` (yes/no),
`finished_apparatus` (yes/no), `digital_device` (yes/no, US/KR), `kr_licence_free_class` (yes/no, KR),
`intended_use` (free text; falls back to `application`). These decide applicability only; compliance is
never assessed.

## Other inputs the tool reads

`--fab-capability FILE` (fab limits with their page, grounded verbatim), `--catalog CSV` with
`--catalog-date ISO8601` (sourcing data, never an identity), `--regulatory-candidates PATH`,
`--sources-dir DIR`, `--no-pdf`, `--browser PATH`. Network and model flags are listed in `pipeline.md`
under "External actions".
