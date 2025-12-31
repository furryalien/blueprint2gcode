; Blueprint to G-code
; Input: test_images_corners/test13_cross.png
; Generated with blueprint2gcode.py

G21 ; Set units to millimeters
G90 ; Absolute positioning
G0 Z3.0 ; Pen up
G0 X0 Y0 ; Move to origin

G0 X148.500 Y157.000 F3000 ; Travel to line 1
G0 Z0.0 ; Pen down
G1 X148.500 Y105.347 F1000
G1 X148.153 Y105.000 F1000
G1 X96.500 Y105.000 F1000
G1 X148.153 Y105.000 F1000
G1 X148.500 Y104.653 F1000
G1 X148.500 Y53.347 F1000
G1 X148.500 Y104.653 F1000
G1 X148.847 Y105.000 F1000
G1 X200.153 Y105.000 F1000
G1 X148.847 Y105.000 F1000
G1 X148.500 Y105.347 F1000
G0 Z3.0 ; Pen up

; Return to origin
G0 X0 Y0
G0 Z3.0

; Total drawing distance: 492.57 mm
; Total travel distance: 216.10 mm
; Total lines: 1
; Estimated time: 33.9 seconds (0.6 minutes)
M2 ; End program