
import sys
import argparse
import os
import uuid
from claude import get_normalized_polylines
from consts import *

TINY_WIGGLE = 10000000 * 0.3
BLICK = 705600000 # 1 quarter note in Blicks

SEG_MERGE_SLOPE_TOLERANCE = 0.1

def main():
    # By default you specify input file, and output file will be that file but with '.svp' extension
    # By default we jam the entire svg into one bar and one octave, you can specify how many semitones and bars you want

    parser = argparse.ArgumentParser(description='Convert SVG files to SVP format.', add_help=False) # Stupid help conflicts with height
    parser.add_argument('input', type=str, help='Input SVG file')
    parser.add_argument('output', type=str, nargs='?', help='Output SVP file (default: input file with .svp extension)')
    parser.add_argument('--width', '-w', type=float, default=4.0, help='Number of quarter notes wide (default: 4)')
    parser.add_argument('--height', '-h', type=float, default=12.0, help='Number of semitones tall (default: 12)')
    parser.add_argument('-x', type=float, default=2.0, help='Starting X position, in quarter notes (default: 2)')
    parser.add_argument('-y', type=float, default=48.0, help='Starting Y position, in MIDI note IDs (default: 48)')
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
        x = ((point[0] * args.width) + args.x) * BLICK # Blicks
        y = (point[1] * args.height) + args.y
        return x, y
    
    # Helper to split a polyline into multiple segments that has a monotonically increasing x value
    def split_polyline(polyline):
        segments = []
        ref_point = polyline[0]
        current_segment = [ref_point]
        maximum_wiggle = 0
        merged_wiggle = False

        def finish_current_segment(current_point):
            # Finishes current segment and does some cleanup
            nonlocal current_segment, merged_wiggle, maximum_wiggle, ref_point
            merged_wiggle = False
            maximum_wiggle = 0
            ref_point = current_point

            def slope(point1, point2):
                ret = (point2[1] - point1[1]) / (point2[0] - point1[0]) if (point2[0] - point1[0]) != 0 else 1e-5
                return ret if ret != 0 else 1e-5
            
            finished = False

            # If all parts of a segment has a similar slope, its X delta is less than 5*TINY_WIGGLE, and has <= 5 points
            # we connect the head and tail of the segment to form a single segment
            if len(current_segment) > 2 and len(current_segment) <= 5:
                good_for_merge = True
                total_slope = slope(current_segment[0], current_segment[-1])
                for i in range(len(current_segment) - 1):
                    if abs(slope(current_segment[i], current_segment[i + 1]) / total_slope - 1) > SEG_MERGE_SLOPE_TOLERANCE:
                        good_for_merge = False
                        break
                # Check if the X delta is less than5*TINY_WIGGLE
                if good_for_merge and abs(current_segment[-1][0] - current_segment[0][0]) < (5 * TINY_WIGGLE / BLICK):
                    segments.append([current_segment[0], current_segment[-1]])
                    finished = True

            # If the current and last segment are both 2-point-segments, merging results in similar slopes
            # and the X delta is less than 3*TINY_WIGGLE, we merge them
            if len(segments) > 0 and len(current_segment) == 2 and len(segments[-1]) == 2:
                slope_last = slope(segments[-1][0], segments[-1][1])
                slope_current = slope(current_segment[0], current_segment[1])
                slope_total = slope(segments[-1][0], current_segment[1])
                if abs(slope_last / slope_current - 1) < SEG_MERGE_SLOPE_TOLERANCE and \
                    abs(slope_total / slope_current - 1) < SEG_MERGE_SLOPE_TOLERANCE and \
                    abs(current_segment[1][0] - segments[-1][0][0]) < (3 * TINY_WIGGLE / BLICK):
                    segments[-1][1] = current_segment[1]
                    finished = True
                # We also check with a much stricter tolerance (5%) and doesn't limit the X delta to 3*TINY_WIGGLE
                elif abs(slope_last - slope_current) < min(0.05, SEG_MERGE_SLOPE_TOLERANCE):
                    segments[-1][1] = current_segment[1]
                    finished = True

            if not finished:
                segments.append(current_segment)

            current_segment = [current_point]

            # Visualize all segments with matplotlit
            if False:
                import matplotlib.pyplot as plt
                for segment in segments:
                    x_coords = [convert_coords(point)[0] for point in segment]
                    y_coords = [convert_coords(point)[1] for point in segment]
                    plt.plot(x_coords, y_coords, marker='o')
                plt.title('Segmented Polylines')
                plt.xlabel('X (Blicks)')
                plt.ylabel('Y (MIDI note IDs)')
                plt.grid()
                plt.show()

        for point in polyline[1:]:
            x_wiggle = abs(point[0] - ref_point[0])
            maximum_wiggle = max(maximum_wiggle, x_wiggle)
            # If X wiggle is really small, in this case, we discard everything except the first point
            # and append the current point after (so we essentially merges the wiggle segments)
            if maximum_wiggle < (TINY_WIGGLE / BLICK):
                current_segment = [current_segment[0], point]
                merged_wiggle = True
            # Otherwise, must ensure x is monotonically increasing
            # If we've met this condition after we've merged tiny wiggles, a new segment should be started
            elif point[0] >= current_segment[-1][0]:
                if merged_wiggle:
                    current_segment = [current_segment[0], point]
                    finish_current_segment(point)
                    current_segment = [] # Current segment will be appended of the current point below, avoid repeating points
                current_segment.append(point)
            # If all above fails, we start a new segment
            else:
                current_segment.append(point)
                finish_current_segment(point)
        segments.append(current_segment)

        # print(f"Segmented polyline into {len(segments)} segments")
        return segments
    
    # Write the SVP file
    pitch_id = 1000

    with open(output_file, 'w') as f:
        notegroup_uuid = str(uuid.uuid4())
        f.write(file_seg_before_uuid)
        f.write(notegroup_uuid)
        f.write(file_seg_after_uuid)

        # For each polyline: We break each polyline into small segments whose X value increases monotonically
        # and write them as individual pitch control lines.

        polyline_data = ''
        for polyline in polylines:
            # Split the polyline into segments
            segments = split_polyline(polyline)

            # Make each segment a separate pitch control line
            for segment in segments:
                # Determine the origin
                origin = segment[0]
                origin_converted = convert_coords(origin)

                # Write the first point (origin) in the polyline
                polyline_data += (file_seg_pitch_ctrl_meta.format(origin_converted[0], origin_converted[1], pitch_id))
                pitch_id += 1

                # Write the rest of the points (segments) in the polyline
                # Note that to avoid near vertical segments (they will not be rendered in the software),
                # When the polyline contains only 2 points, we detect if this is a near vertical segment
                # and we add a tiny wiggle to the second point to make it horizontal.
                last_point_converted = origin_converted
                polyline_coords = [0, 0]
                for point in segment[1:]:
                    point_converted = convert_coords(point)

                    # Minimum X wiggle detection
                    if len(segment) == 2 and (abs(point_converted[0] - last_point_converted[0]) < TINY_WIGGLE):
                        point_converted = (last_point_converted[0] + TINY_WIGGLE, point_converted[1])

                    # Relative coordinate to the origin is used as the pitch control line's point coordinates
                    polyline_coords.append(point_converted[0] - origin_converted[0])
                    polyline_coords.append(point_converted[1] - origin_converted[1])
                
                polyline_data += str(polyline_coords) + file_seg_pitch_ctrl_end + ','
        
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
