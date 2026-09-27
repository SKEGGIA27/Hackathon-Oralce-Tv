# Scuderia Tor Vergata STV-E26
# Technical Dossier and Experimental Parts Register

## 1. Vehicle Overview

The STV-E26 is a single-seater electric prototype developed for endurance-style data collection, control-system validation, and university motorsport training. The car uses a carbon composite monocoque, double-wishbone suspension, a high-downforce aero package, and a rear-mounted electric drive unit with regenerative braking.

Primary design targets are stable tyre usage over long runs, strong low-speed traction, and repeatable thermal performance in hot-weather testing.

## 2. Chassis and Safety Structures

- Carbon composite monocoque with aluminum inserts at suspension pickup points.
- Wheelbase: 1605 mm.
- Front track: 1210 mm.
- Rear track: 1195 mm.
- Main roll hoop: steel, integrated into rear bulkhead support structure.
- Static ground clearance: 31 mm in running trim without driver.

## 3. Suspension System

The car uses unequal-length double wishbones front and rear with pushrod actuation and inboard spring-damper units.

- Front lower wishbone structural tube: 18 mm outer diameter steel insert, 1.2 mm wall thickness.
- Rear lower wishbone structural tube: 20 mm outer diameter steel insert, 1.2 mm wall thickness.
- Steering geometry optimized for low-speed rotation with conservative Ackermann.
- Suspension fairings removable for inspection and service.

### 3.1 Experimental suspension arm SA-LF-OPT

The experimental left-front upper suspension fairing assembly SA-LF-OPT uses a removable carbon shell around a steel structural insert.

- Maximum fairing chord: 34 mm.
- Maximum fairing thickness: 18 mm.
- Structural insert wall thickness: 1.2 mm steel.
- Fairing split line leaves rod-end inspection area visible.
- Intended purpose: reduce drag with no significant change in local downforce.

## 4. Aerodynamics

The STV-E26 aerodynamic package uses a front wing, floor fences, diffuser, and a two-element rear wing.

- Overall vehicle width with aero package: 1388 mm.
- Front wing forward extension: 655 mm ahead of the front axle centerline.
- Rear wing total width on the baseline package: 1175 mm.
- Baseline rear-wing main element chord: 292 mm.
- Baseline rear-wing rearward extension from rear axle centerline: 238 mm.

### 4.1 Experimental rear wing assembly RW-26C

The proposed RW-26C update was developed for higher medium-speed downforce at the next test.

- Total assembly width: 1190 mm.
- Main element chord: 308 mm.
- Secondary element chord: 188 mm.
- Rearward extension behind the rear axle centerline: 286 mm.
- Endplate side-elevation envelope: 810 mm by 415 mm.
- Support pylons fixed relative to the gearbox casing.

Engineering note: the geometry improves rear stability in simulation but has not yet been cleared by compliance review.

## 5. Wheels and Tyres

- Approved dry compounds in current inventory: M2 medium slick and H1 hard slick.
- Typical target hot pressure: 1.58 bar front and 1.54 bar rear.
- Tyre blanket use is not part of team operating procedure.
- Wear modelling is maintained for both approved dry compounds.

## 6. Braking System

- Four-wheel hydraulic disc brakes with front-biased cooling.
- Carbon-metallic discs with aluminum hats.
- Brake temperature sensing at each corner integrated into the telemetry logger.
- Regenerative braking blended with hydraulic braking above 35 km/h.

## 7. Powertrain and Accumulator System

- Rear-mounted electric motor and single-speed reduction gearbox.
- Maximum continuous power target: 82 kW.
- Maximum short-duration deployment target: 108 kW for up to ten seconds.
- Regeneration target: up to 22 kW depending on rear-wheel slip state.

### 7.1 Baseline accumulator container

The current approved accumulator housing uses 2.5 mm 6061-T6 aluminum outer walls with internal aramid insulation and ceramic stand-offs at module interfaces.

### 7.2 Experimental accumulator container BAT-X9

The BAT-X9 proposal is intended to reduce mass and simplify service access.

- Primary outer shell material: 1.5 mm magnesium-lithium sheet.
- Inner liner: 3.0 mm aramid panel.
- Fastened service lid with captive hardware.
- Same cell spacing and isolation hardware as the baseline pack.

Engineering note: BAT-X9 offers a modeled mass reduction of 2.8 kg but has not yet passed rules review.

## 8. Sensors and Electronics

- Four brake temperature sensors.
- Four tyre temperature channels.
- Four tyre pressure channels.
- Wheel-speed sensors on all corners.
- Inverter temperature, motor temperature, pack current, pack voltage, and state-of-charge logging.
- GPS timing, IMU, and steering-angle logging for strategy and anomaly analysis.

## 9. Experimental Parts Register Summary

1. SA-LF-OPT left-front suspension fairing: intended for drag reduction, dimensional review required.
2. RW-26C rear wing revision: intended for higher rear downforce, dimensional review required.
3. BAT-X9 accumulator enclosure: intended for mass reduction, material compliance review required.

## 10. Intended Use In The Hackathon

The dossier is designed for the compliance RAG task. Students should compare the dimensions and materials listed here against the regulation handbook and explain their findings with section references.

Your system should:

- identify the relevant regulation sections for each component question,
- compare the component specification to the applicable limit or rule,
- state whether the evidence supports a compliant, non-compliant, or insufficient-information verdict,
- explain the conclusion in clear engineering language.
