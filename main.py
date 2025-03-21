
import sys
import argparse
import os
import uuid
from claude import get_normalized_polylines
from consts import *

def main():
    # By default you specify input file, and output file will be that file but with '.svp' extension
    # By default we jam the entire svg into one bar and one octave, you can specify how many semitones and bars you want

    parser = argparse.ArgumentParser(description='Convert SVG files to SVP format.', add_help=False) # Stupid help conflicts with height
    parser.add_argument('input', type=str, help='Input SVG file')
    parser.add_argument('output', type=str, nargs='?', help='Output SVP file (default: input file with .svp extension)')
    parser.add_argument('--width', '-w', type=float, default=4.0, help='Number of quarter notes wide (default: 4)')
    parser.add_argument('--height', '-h', type=float, default=12.0, help='Number of semitones tall (default: 12)')
    parser.add_argument('-x', type=float, default=4.0, help='Starting X position, in quarter notes (default: 4)')
    parser.add_argument('-y', type=float, default=48.0, help='Starting Y position, in MIDI note IDs (default: 12)')
    parser.add_argument('--precision', '-p', type=float, default=1.0, help='Polyline precision (higher values = more points)')
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite output file if it exists')
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS, help='show this help message and exit')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output if args.output else input_file.rsplit('.', 1)[0] + '.svp'

    # If output file exists, warn the user and ask for confirmation to overwrite
    if not args.force and os.path.exists(output_file):
        print(f"Output file '{output_file}' already exists. Use -f to overwrite.")
        sys.exit(1)

    polylines: list[(float, float)] = get_normalized_polylines(input_file, args.precision)

    # Helper to convert normalized coordinates to SVP coordinates
    def convert_coords(point):
        x = ((point[0] * args.width) + args.x) * 705600000 # Blicks
        y = (point[1] * args.height) + args.y
        return x, y
    
    # Write the SVP file
    pitch_id = 1000

    with open(output_file, 'w') as f:
        notegroup_uuid = str(uuid.uuid4())
        f.write(file_seg_before_uuid)
        f.write(notegroup_uuid)
        f.write(file_seg_after_uuid)

        # For each polyline: We break each polyline into small segments and write them as individual pitch control lines.

        polyline_data = ''
        for polyline in polylines:
            # Determine first point
            first_point = polyline[0]
            first_point_converted = convert_coords(first_point)

            # Write the rest of the points (segments) in the polyline
            for point in polyline[1:]:
                polyline_data += (file_seg_pitch_ctrl_meta.format(first_point_converted[0], first_point_converted[1], pitch_id))
                pitch_id += 1

                point_converted = convert_coords(point)
                x = point_converted[0] - first_point_converted[0]
                y = point_converted[1] - first_point_converted[1]
                if abs(x) < 10000000:  # Avoid near vertical segments
                    x = 10000000
                polyline_data += "[0.0,0.0,{},{}]".format(x, y) + file_seg_pitch_ctrl_end + ','

                # Switch origin
                first_point = point
                first_point_converted = convert_coords(first_point)

        
        # Remove the last comma
        polyline_data = polyline_data[:-1]
        f.write(polyline_data)

        main_group_uuid = str(uuid.uuid4())
        f.write(file_seg_end_before_main_group_uuid1)
        f.write(main_group_uuid)
        f.write(file_seg_end_after_main_group_uuid1)
        f.write(file_seg_end_before_main_group_uuid2)
        f.write(main_group_uuid)
        f.write(file_seg_end_after_main_group_uuid2)

        f.write(file_seg_end_before_group_uuid)
        f.write(notegroup_uuid)
        f.write(file_seg_end_after_group_uuid)

    print(f"Converted '{input_file}' to '{output_file}' successfully.")

if __name__ == '__main__':
    main()
