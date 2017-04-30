/* functions we later use to disable scrolling while the loading animation is present */
// left: 37, up: 38, right: 39, down: 40,
// spacebar: 32, pageup: 33, pagedown: 34, end: 35, home: 36
var keys = {37: 1, 38: 1, 39: 1, 40: 1};

function preventDefault(e) {
    e = e || window.event;
    if (e.preventDefault)
        e.preventDefault();
    e.returnValue = false;
}

function preventDefaultForScrollKeys(e) {
    if (keys[e.keyCode]) {
        preventDefault(e);
        return false;
    }
}

function disableScroll() {
    if (window.addEventListener) // older FF
        window.addEventListener('DOMMouseScroll', preventDefault, false);
    window.onwheel = preventDefault; // modern standard
    window.onmousewheel = document.onmousewheel = preventDefault; // older browsers, IE
    window.ontouchmove  = preventDefault; // mobile
    document.onkeydown  = preventDefaultForScrollKeys;
}

// start by disabling scroll
disableScroll();

function enableScroll() {
    if (window.removeEventListener)
        window.removeEventListener('DOMMouseScroll', preventDefault, false);
    window.onmousewheel = document.onmousewheel = null;
    window.onwheel = null;
    window.ontouchmove = null;
    document.onkeydown = null;
}

// run the loading animation
introduction();

function introduction() {
    /* three.js animation */
    "use strict";

    function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

    function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

    function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

    var Cube = function (_THREE$Object3D) {
        _inherits(Cube, _THREE$Object3D);

        function Cube(size) {
            _classCallCheck(this, Cube);

            var _this = _possibleConstructorReturn(this, _THREE$Object3D.call(this));

            _this.colors = [0xFFB71C, 0xD9D9D9, 0x1AADC1];

            _this.geom = new THREE.BoxGeometry(size, size, size);

            _this.mat = new THREE.MeshBasicMaterial({
                vertexColors: THREE.FaceColors,
                wireframe: false
            });

            _this.colorRadomizer = random(0.9, 1.1);

            for (var i = 0; i < _this.geom.faces.length; i++) {
                _this.geom.faces[i].color.setHex(_this.colors[~ ~(i / 4)]);

                _this.geom.faces[i].color.r *= _this.colorRadomizer;
                _this.geom.faces[i].color.g *= _this.colorRadomizer;
                _this.geom.faces[i].color.b *= _this.colorRadomizer;
            }

            _this.mesh = new THREE.Mesh(_this.geom, _this.mat);
            _this.add(_this.mesh);
            return _this;
        }

        Cube.prototype.update = function update() {
            // this.mesh.geometry.colorsNeedUpdate = true;
        };

        return Cube;
    }(THREE.Object3D);

    var Webgl = function () {
        function Webgl(width, height) {
            _classCallCheck(this, Webgl);

            this.scene = new THREE.Scene();
            this.aspectRatio = width / height;
            this.rotationMode = true;
            this.wireframeMode = false;
            var w = window.innerWidth;
            var h = window.innerHeight;
            this.distance = 1.75*Math.min(w,h);
            this.camera = new THREE.OrthographicCamera(-this.distance * this.aspectRatio, this.distance * this.aspectRatio, this.distance, -this.distance, 1, 1000);
            this.camera.position.set(0, 0, 150);
            this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            this.renderer.setSize(width, height);

            this.animationIntroDone = false;

            this.cubesGroup = new THREE.Object3D();

            this.cubes = [];
            this.cubeSize = 10;
            this.cubeOffset = 10;

            this.drawCubes();

            this.setLights();

            this.animation();
        }

        Webgl.prototype.drawCubes = function drawCubes() {

            for (var i = -2; i <= 2; i++) {
                for (var j = -2; j <= 2; j++) {
                    for (var k = -2; k <= 2; k++) {
                        var cube = new Cube(this.cubeSize);
                        cube.position.x = i * this.cubeSize;
                        cube.position.y = k * this.cubeSize;
                        cube.position.z = j * this.cubeSize;
                        this.cubes.push(cube);
                        this.cubesGroup.add(cube);
                    }
                }
            }

            this.scene.add(this.cubesGroup);
        };

        Webgl.prototype.setLights = function setLights() {
            this.ambientLight = new THREE.AmbientLight(0x9b59b6);
            this.scene.add(this.ambientLight);
        };

        Webgl.prototype.resize = function resize(width, height) {
            this.aspectRatio = width / height;
            this.camera = new THREE.OrthographicCamera(-this.distance * this.aspectRatio, this.distance * this.aspectRatio, this.distance, -this.distance, 1, 1000);
            this.camera.position.set(0, 0, 150);

            this.camera.updateProjectionMatrix();

            this.renderer.setSize(width, height);
        };

        Webgl.prototype.animation = function animation() {

            var initRotationDuration = 0.7;
            var halfLength = Math.floor(this.cubes.length / 2);
            var staggerOffset = 0.03;
            var loopDelay = 1;

            var groupTl = new TimelineMax();

            groupTl.to(this.cubesGroup.rotation, initRotationDuration, { x: 2 * Math.PI + 0.6, y: 2 * Math.PI - 0.8, ease: Cubic.easeOut });

            // Fist half
            for (var i = 0; i < this.cubes.length / 2 - 1; i++) {
                var newX = (this.cubes[i].position.x + this.cubeOffset) * 2.5;
                var newY = (this.cubes[i].position.y + this.cubeOffset) * 2.5;
                var newZ = (this.cubes[i].position.z + this.cubeOffset) * 2.5;
                var delay = initRotationDuration + staggerOffset * i;

                var tl = new TimelineMax({ delay: delay, repeat: -1, repeatDelay: loopDelay, yoyo: true });

                if (i === this.cubes.length / 2 - 2) {
                    tl = new TimelineMax({ delay: delay, repeat: -1, repeatDelay: loopDelay, yoyo: true, onRepeat: function onRepeat() {
                        console.log('reset');
                        groupTl.seek(0);
                    } });
                }

                tl.to(this.cubes[i].position, 0.5, { x: newX, y: newY, z: newZ, ease: Back.easeOut }).to(this.cubes[i].rotation, 0.5, { x: Math.PI, y: -Math.PI, ease: Cubic.easeOut }).to(this.cubes[i].scale, 0.5, { x: 0.5, y: 0.5, z: 0.5, ease: Cubic.easeOut }, "-=0.2");
            }

            // Second half
            for (var i = halfLength; i < this.cubes.length; i++) {

                var newX = (this.cubes[i].position.x + this.cubeOffset) * 2.5;
                var newY = (this.cubes[i].position.y + this.cubeOffset) * 2.5;
                var newZ = (this.cubes[i].position.z + this.cubeOffset) * 2.5;
                var delay = initRotationDuration + staggerOffset * (this.cubes.length - i);

                var tl = new TimelineMax({ delay: delay, repeat: -1, repeatDelay: loopDelay, yoyo: true });

                tl.to(this.cubes[i].position, 0.5, { x: newX, y: newY, z: newZ, ease: Back.easeOut }).to(this.cubes[i].rotation, 0.5, { x: Math.PI, y: -Math.PI, ease: Cubic.easeOut }).to(this.cubes[i].scale, 0.5, { x: 0.5, y: 0.5, z: 0.5, ease: Cubic.easeOut }, "-=0.4");
            }
        };

        Webgl.prototype.render = function render() {

            if (this.rotationMode) {
                this.scene.rotation.z += 0.01;
            }

            this.renderer.autoClear = false;
            this.renderer.clear();
            this.renderer.render(this.scene, this.camera);

            for (var i = 0; i < this.cubes.length; i++) {
                this.cubes[i].update();
            }
        };

        return Webgl;
    }();

// Main js

    var webgl = undefined;
    var audio = undefined;
    var gui = undefined;
// var stats = undefined;

    webgl = new Webgl(window.innerWidth, window.innerHeight);

    document.getElementById('loading').appendChild(webgl.renderer.domElement);

//Stats js
// stats = new Stats();
// stats.setMode(0);
//
// stats.domElement.style.position = 'absolute';
// stats.domElement.style.left = '0px';
// stats.domElement.style.top = '0px';

// document.getElementById('loading').appendChild(stats.domElement);

    window.onresize = resizeHandler;

    animate();

    function resizeHandler() {
        webgl.resize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        //stats.begin();
        requestAnimationFrame(animate);
        webgl.render();
        //stats.end();
    }

    function random(min, max) {
        return Math.random() * (max - min + 1) + min;
    }


    /* check if the project is using jQuery and set the appropriate value */
    if (window.jQuery) { var V = $.Velocity; } else {var V = Velocity; }


    /* loading animation */
    function fadeWelcome() {
        var loadContainer = document.getElementById('loading');
        var homeContainer = document.getElementById('fade-in');
        V(loadContainer, {opacity: 0}, {duration: 2000});
        V(homeContainer, {opacity: 1}, {duration: 2000});
        setTimeout(function() {
            enableScroll();
            loadContainer.style.zIndex = "-1";
        }, 1900);

    }

    function loading(i) {
        var div = document.getElementById('progress');
        setTimeout(function() {
            div.innerHTML = String(i) + '%';
        }, i * 50);
    }

    for (var i = 1; i <= 100; i++) {
        loading(i);
        if (i == 100) {
            setTimeout(function() {
                fadeWelcome();
            }, 5500);
        }
    }
}