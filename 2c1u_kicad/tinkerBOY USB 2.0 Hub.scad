board_width = 21.86; // mm
board_width_px = 755;
board_height = 14.02; // mm
board_height_px = 476;
width_px_per_mm = board_width_px / board_width;
height_px_per_mm = board_height_px / board_height;

echo(width_px_per_mm=width_px_per_mm, height_px_per_mm=height_px_per_mm);

pad_width_px = 64;
hole_width_px = 32;
pad_width = pad_width_px / width_px_per_mm;
hole_width = hole_width_px / width_px_per_mm;

echo(pad_width=pad_width, hole_width=hole_width);

left_to_center_of_first_pad_px = 47;
left_pad_x = left_to_center_of_first_pad_px / width_px_per_mm;
bottom_to_center_of_pad_px = 39;
pad_y = bottom_to_center_of_pad_px / width_px_per_mm;
echo(left_pad_x=left_pad_x);

pad_group_center_dist_px = 89;
pad_group_center_dist = pad_group_center_dist_px / width_px_per_mm;
echo(pad_group_center_dist=pad_group_center_dist);
pad_group_padding_px = 102;
pad_group_padding = pad_group_padding_px / width_px_per_mm;
echo(pad_group_padding=pad_group_padding);

$fn = 30;

echo(79 / width_px_per_mm);
echo(169 / width_px_per_mm);

difference() {
    square(size=[board_width, board_height]);

    for(i = [0 : 1 : 7]) {
        echo(i=i, pad_x=pad_x);
        pad_x = left_pad_x + floor(i / 2) * (pad_group_center_dist + pad_group_padding) + (i % 2) * pad_group_center_dist;
        translate([pad_x, pad_y, 0]) {
            cylinder(h=2, r=pad_width / 2, center=true);
        }
    }
}
/*
343.55 px / cm

hole width 36px = 0.10479 cm
pad width 64px = 1.8629 cm
dist from left to center 47px = 0.166 cm
bottom to center 39px = 0.163 cm

dist between first centers 89px = 0.259 cm

pad size 2.1121
hole size 1.0479

103px = 0.2998cm
*/
