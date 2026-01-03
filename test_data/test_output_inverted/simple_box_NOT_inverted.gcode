; Blueprint to G-code
; Input: test_data\test_images_inverted\white_on_black_simple_box.png
; Generated with blueprint2gcode.py

G21 ; Set units to millimeters
G90 ; Absolute positioning
G0 Z3.0 ; Pen up
G0 X0 Y0 ; Move to origin

G0 X1.000 Y23.015 F3000 ; Travel to line 1
G0 Z0.0 ; Pen down
G1 X1.258 Y22.758 F1000
G1 X103.485 Y22.758 F1000
G1 X103.743 Y23.015 F1000
G1 X103.743 Y125.243 F1000
G1 X103.485 Y125.500 F1000
G1 X1.258 Y125.500 F1000
G1 X1.000 Y125.243 F1000
G0 Z3.0 ; Pen up

G0 X1.000 Y125.500 F3000 ; Travel to line 2
G0 Z0.0 ; Pen down
G1 X1.000 Y22.758 F1000
G1 X103.743 Y22.758 F1000
G1 X103.743 Y125.500 F1000
G0 Z3.0 ; Pen up

; Return to origin
G0 X0 Y0
G0 Z3.0

; Total drawing distance: 638.54 mm
; Total travel distance: 23.29 mm
; Total lines: 2
; Estimated time: 38.8 seconds (0.6 minutes)
M2 ; End program