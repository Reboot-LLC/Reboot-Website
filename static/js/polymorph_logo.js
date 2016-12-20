/* we first need to generate sequence of points which represent the vertices of our connected graph */
var points = [];
// n is the number of points
// dim is the number of dimension (2 or 3, but you could create more if you want...)
// the lower bound controls the minimum coordinate value, and influences the "spikiness" of the geometry
// the upper bound controls the maximum coordinate value

// these x, y, and z values will be added from a central coordinate of (0, 0, 0) to get a set of vertices

function generatePoints(n, dim, lower_bound, upper_bound) {
    var min = Math.ceil(lower_bound);
    var max = Math.floor(upper_bound);
    for (var i = 0; i < n; i++) {
        var coordinate = [];
        for (var j = 0; j < dim; j++) {
            coordinate.push(Math.floor(Math.random() * (max - min)) + min);
        }
        points.push(coordinate);
    }
}

generatePoints(10, 2, 25, 250);
console.log(points);

/* we now need to draw that shape using Two.js */
function generateShape(coordinate_array) {
    // Make an instance of Two and place it on the page.
    var elem = document.getElementById('logo_div');
    // the width and height need to be the same as the upper bound set above
    var params = { width: 250, height: 250 };
    var two = new Two(params).appendTo(elem);

    var anchors = [];
    for (var i = 0; i < coordinate_array.length; i++) {
        console.log(coordinate_array[i]);
        anchors.push(new Two.Anchor(coordinate_array[i][0], coordinate_array[i][1]));
    }

    var shape = two.makePath(anchors, false);
    shape.stroke = '#65C1C2';
    shape.linewidth = 4;
    shape.fill = '#48DAD0';
    shape.opacity = 0.8;

    // render to the screen
    two.update();
}

generateShape(points);