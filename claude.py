# This file is generated by Claude Sonnet 3.7
# With my own modifications

import xml.etree.ElementTree as ET
import re
import argparse
import traceback
import math
import numpy as np
from svg.path import parse_path, Line, CubicBezier, QuadraticBezier, Arc
from svg.path.path import Move

def extract_paths_from_svg(svg_file):
    """Extract path data from SVG file"""
    
    # Register SVG namespace
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Parse the SVG file
    tree = ET.parse(svg_file)
    root = tree.getroot()
    
    # Get the width and height of the SVG
    try:
        width = float(root.attrib.get('width', '100').replace('px', ''))
        height = float(root.attrib.get('height', '100').replace('px', ''))
    except ValueError:
        width, height = 100, 100  # Default values if parsing fails
        
    # Check for viewBox attribute which might override width/height
    if 'viewBox' in root.attrib:
        viewbox = root.attrib['viewBox'].split()
        if len(viewbox) == 4:
            min_x, min_y, vb_width, vb_height = map(float, viewbox)
            width, height = vb_width, vb_height
    
    paths = []
    
    # Find all path elements
    for path in root.findall('.//svg:path', namespaces):
        if 'd' in path.attrib:
            paths.append(path.attrib['d'])
    
    # Also handle polyline elements
    for polyline in root.findall('.//svg:polyline', namespaces):
        if 'points' in polyline.attrib:
            points = polyline.attrib['points'].strip()
            points = re.sub(r'\s+', ' ', points)  # Normalize whitespace
            
            # Convert polyline points to a path
            point_pairs = []
            for point in points.split():
                if ',' in point:
                    x, y = point.split(',')
                    point_pairs.append((float(x), float(y)))
                elif point_pairs:  # Assume alternating x,y values
                    if len(point_pairs[-1]) == 2:
                        point_pairs.append([float(point)])
                    else:
                        point_pairs[-1].append(float(point))
            
            if point_pairs:
                path_data = f"M {point_pairs[0][0]},{point_pairs[0][1]} "
                for x, y in point_pairs[1:]:
                    path_data += f"L {x},{y} "
                paths.append(path_data)
    
    # Handle polygon elements
    for polygon in root.findall('.//svg:polygon', namespaces):
        if 'points' in polygon.attrib:
            points = polygon.attrib['points'].strip()
            points = re.sub(r'\s+', ' ', points)  # Normalize whitespace
            
            # Convert polygon points to a path (closed)
            point_pairs = []
            for point in points.split():
                if ',' in point:
                    x, y = point.split(',')
                    point_pairs.append((float(x), float(y)))
                elif point_pairs:  # Assume alternating x,y values
                    if len(point_pairs[-1]) == 2:
                        point_pairs.append([float(point)])
                    else:
                        point_pairs[-1].append(float(point))
            
            if point_pairs:
                path_data = f"M {point_pairs[0][0]},{point_pairs[0][1]} "
                for x, y in point_pairs[1:]:
                    path_data += f"L {x},{y} "
                path_data += "Z"  # Close the path
                paths.append(path_data)
    
    # Handle line elements
    for line in root.findall('.//svg:line', namespaces):
        if all(attr in line.attrib for attr in ['x1', 'y1', 'x2', 'y2']):
            x1 = float(line.attrib['x1'])
            y1 = float(line.attrib['y1'])
            x2 = float(line.attrib['x2'])
            y2 = float(line.attrib['y2'])
            
            path_data = f"M {x1},{y1} L {x2},{y2}"
            paths.append(path_data)
    
    # Handle rect elements
    for rect in root.findall('.//svg:rect', namespaces):
        if all(attr in rect.attrib for attr in ['x', 'y', 'width', 'height']):
            x = float(rect.attrib['x'])
            y = float(rect.attrib['y'])
            w = float(rect.attrib['width'])
            h = float(rect.attrib['height'])
            
            # Optional rx, ry for rounded corners
            rx = float(rect.attrib.get('rx', 0))
            ry = float(rect.attrib.get('ry', rx))  # If ry is not specified, use rx
            
            if rx == 0 and ry == 0:
                # Simple rectangle
                path_data = f"M {x},{y} H {x+w} V {y+h} H {x} Z"
            else:
                # Rounded rectangle
                path_data = f"M {x+rx},{y} "
                path_data += f"H {x+w-rx} "
                path_data += f"A {rx},{ry} 0 0 1 {x+w},{y+ry} "
                path_data += f"V {y+h-ry} "
                path_data += f"A {rx},{ry} 0 0 1 {x+w-rx},{y+h} "
                path_data += f"H {x+rx} "
                path_data += f"A {rx},{ry} 0 0 1 {x},{y+h-ry} "
                path_data += f"V {y+ry} "
                path_data += f"A {rx},{ry} 0 0 1 {x+rx},{y} "
                path_data += "Z"
            
            paths.append(path_data)
    
    # Handle circle elements
    for circle in root.findall('.//svg:circle', namespaces):
        if all(attr in circle.attrib for attr in ['cx', 'cy', 'r']):
            cx = float(circle.attrib['cx'])
            cy = float(circle.attrib['cy'])
            r = float(circle.attrib['r'])
            
            # Create a circle path (uses two arc commands)
            path_data = f"M {cx+r},{cy} "
            path_data += f"A {r},{r} 0 0 1 {cx},{cy+r} "
            path_data += f"A {r},{r} 0 0 1 {cx-r},{cy} "
            path_data += f"A {r},{r} 0 0 1 {cx},{cy-r} "
            path_data += f"A {r},{r} 0 0 1 {cx+r},{cy} "
            path_data += "Z"
            
            paths.append(path_data)
    
    # Handle ellipse elements
    for ellipse in root.findall('.//svg:ellipse', namespaces):
        if all(attr in ellipse.attrib for attr in ['cx', 'cy', 'rx', 'ry']):
            cx = float(ellipse.attrib['cx'])
            cy = float(ellipse.attrib['cy'])
            rx = float(ellipse.attrib['rx'])
            ry = float(ellipse.attrib['ry'])
            
            # Create an ellipse path (uses two arc commands)
            path_data = f"M {cx+rx},{cy} "
            path_data += f"A {rx},{ry} 0 0 1 {cx},{cy+ry} "
            path_data += f"A {rx},{ry} 0 0 1 {cx-rx},{cy} "
            path_data += f"A {rx},{ry} 0 0 1 {cx},{cy-ry} "
            path_data += f"A {rx},{ry} 0 0 1 {cx+rx},{cy} "
            path_data += "Z"
            
            paths.append(path_data)
    
    return paths, width, height

def path_to_polyline(path_data, precision):
    """Convert SVG path to polyline with the given precision"""
    
    # Parse the path data
    path = parse_path(path_data)
    
    # Calculate the number of points based on precision
    points = []
    
    for segment in path:
        if isinstance(segment, Move):
            # For Move commands, just add the destination point
            points.append((segment.end.real, segment.end.imag))
        else:
            # For other segments (lines, curves, arcs), sample points
            segment_length = segment.length()
            if segment_length == 0:
                continue
                
            # Calculate number of points based on segment length and precision
            num_points = max(2, int(segment_length * precision))
            
            for i in range(num_points + 1):
                t = i / num_points
                point = segment.point(t)
                points.append((point.real, point.imag))
    
    return points

def find_bounding_box(all_points):
    """Find bounding box for all points across all polylines"""
    if not all_points or len(all_points) == 0:
        return (0, 0, 1, 1)  # Default bounding box
    
    # Flatten the list of points
    flat_points = [point for sublist in all_points for point in sublist]
    
    # Find min/max coordinates
    min_x = min(p[0] for p in flat_points)
    max_x = max(p[0] for p in flat_points)
    min_y = min(p[1] for p in flat_points)
    max_y = max(p[1] for p in flat_points)
    
    return min_x, min_y, max_x, max_y

def normalize_polylines(all_polylines, bounding_box):
    """Normalize all polylines to 0-1 range using the same bounding box"""
    min_x, min_y, max_x, max_y = bounding_box
    
    # Calculate ranges
    x_range = max_x - min_x
    y_range = max_y - min_y
    
    # Handle edge cases where range is zero
    if x_range == 0:
        x_range = 1
    if y_range == 0:
        y_range = 1
    
    normalized_polylines = []
    
    for polyline in all_polylines:
        normalized_points = []
        for x, y in polyline:
            norm_x = (x - min_x) / x_range
            norm_y = 1 + (min_y - y) / y_range # In UI the Y axis grows bottom up
            normalized_points.append((norm_x, norm_y))
        normalized_polylines.append(normalized_points)
    
    return normalized_polylines

def visualize_polylines(all_polylines, title="Normalized Polylines"):
    import matplotlib.pyplot as plt

    # Plot the normalized polylines
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Use different colors for each polyline
    colors = plt.cm.tab10.colors
    
    for i, polyline in enumerate(all_polylines):
        xs = [p[0] for p in polyline]
        ys = [p[1] for p in polyline]
        ax.plot(xs, ys, '-', color=colors[i % len(colors)], label=f"Path {i+1}")
    
    # Add some points to show the vertices
    for i, polyline in enumerate(all_polylines):
        xs = [p[0] for p in polyline]
        ys = [p[1] for p in polyline]
        ax.plot(xs, ys, 'o', color=colors[i % len(colors)], markersize=3, alpha=0.5)
    
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("X (Normalized)")
    ax.set_ylabel("Y (Normalized)")
    ax.grid(True)
    
    # Add legend if there are not too many polylines
    if len(all_polylines) <= 10:
        ax.legend(loc='best')
    
    plt.tight_layout()
    plt.show(block=True)

def get_normalized_polylines(svg_file, precision=1.0):
    """Extract and normalize polylines from an SVG file"""
    
    paths, _, _ = extract_paths_from_svg(svg_file)
    
    original_polylines = []
    all_points = []
    
    # First pass: convert all paths to polylines
    for i, path_data in enumerate(paths):
        try:
            polyline_points = path_to_polyline(path_data, precision)
            if polyline_points:
                original_polylines.append(polyline_points)
                all_points.append(polyline_points)
        except Exception as e:
            print(f"Error processing path #{i}: {e}")
    
    # Find the bounding box for all polylines
    bounding_box = find_bounding_box(all_points)
    print(f"Bounding box: {bounding_box}")
    
    # Normalize all polylines using the same bounding box
    normalized_polylines = normalize_polylines(original_polylines, bounding_box)
    
    return normalized_polylines

def main():
    parser = argparse.ArgumentParser(description='Convert SVG to normalized polylines')
    parser.add_argument('svg_file', help='Input SVG file')
    parser.add_argument('--precision', '-p', type=float, default=1.0, 
                        help='Polyline precision (higher values = more points)')
    parser.add_argument('--output', '-o', help='Output file (defaults to stdout)')
    parser.add_argument('--visualize', '-v', action='store_true', 
                        help='Visualize the normalized polylines')
    
    args = parser.parse_args()
    
    try:
        paths, width, height = extract_paths_from_svg(args.svg_file)
        
        original_polylines = []
        all_points = []
        
        # First pass: convert all paths to polylines
        for i, path_data in enumerate(paths):
            try:
                polyline_points = path_to_polyline(path_data, args.precision)
                if polyline_points:
                    original_polylines.append(polyline_points)
                    all_points.append(polyline_points)
            except Exception as e:
                print(f"Error processing path #{i}: {e}")
        
        # Find the bounding box for all polylines
        bounding_box = find_bounding_box(all_points)
        print(f"Bounding box: {bounding_box}")
        
        # Normalize all polylines using the same bounding box
        normalized_polylines = get_normalized_polylines(args.svg_file, args.precision)
        
        # Generate output
        output_text = "# Normalized polylines (whole picture normalization)\n"
        output_text += f"# Bounding box: {bounding_box}\n\n"
        
        for i, polyline in enumerate(normalized_polylines):
            output_text += f"# Polyline {i+1}\n"
            for j, (x, y) in enumerate(polyline):
                output_text += f"{x:.6f}, {y:.6f}\n"
            output_text += "\n"
        
        # Output to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Output written to {args.output}")
        else:
            if not args.visualize and not args.save_plot:
                print(output_text)
        
        # Visualize
        if args.visualize:
            fig = visualize_polylines(normalized_polylines,
                                        f"Normalized Polylines - Whole Picture (Precision: {args.precision})")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())